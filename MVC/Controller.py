import sys
# import threading
import tkinter.font
from tkinter import messagebox
import keyboard
import copy
import os
# from playsound import playsound
import json
import pyperclip
import random
# from deep_translator import GoogleTranslator
# try:
#     import googletrans
#     translator = googletrans.Translator()
# except:
#     translator = None

import re
import time
import math
import uuid

from utils import Enum
from utils.Set import Set
from utils.Screenshot import Screenshot
from utils.SimpleDialog import SimpleDialog
from services.Vocabulary import Vocabulary
from services.Translation import Translation


class Controller:
    def __init__(self, mediator):
        # Attributes
        self.mediator = mediator

        self.update()

    def update(self):
        try:
            # Update view with current model
            self.mediator.view.update()

            # Dump model
            self.mediator.model.dump()
        except Exception as e:
            print(f"An error occurred: {e}")

    def check_categorization(self):
        model = self.mediator.model
        view = self.mediator.view

        interval = model.settings[Enum.Settings.Categorization_Check_Interval]
        practice_alert_bool = model.settings[Enum.Settings.Practice_Alert]
        minimum_practice_terms_for_alert = model.settings[Enum.Settings.Minimum_Practice_Terms_For_Alert]
        categorization = model.practice_set.categorize()

        # Play sound to alert user of due practice terms
        if practice_alert_bool and len(categorization['priority']) >= minimum_practice_terms_for_alert:
            # Make sure user is not already on the practice tab
            if not view.current_tab_name == view.Tab.Practice.name:
                print(f"{time.time()} - TERM DUE")

                # try:
                #
                #     pass
                #     # threading.Thread(target=playsound, args=(fr'{Enum.SOUNDS_DIRECTORY}\ding.mp3',), daemon=True).start()
                # except Exception as e:
                #     print(e)

        # # Auto return
        # if model.settings[Enum.Settings.Auto_Return] is not False:
        #     if view.current_tab_name == view.Tab.Practice.name:
        #         self.on_menu_command(Enum.PracticeCommand.Return)

        # Update practice tab when necessary
        practice_tab = view.tabs[view.Tab.Practice.name]
        if categorization['priority'] and not practice_tab.practice_widgets:
            practice_tab.update()

        # Update
        view.root.after(interval, self.check_categorization)
        view.tabs[view.Tab.Menu.name].update()

    def on_menu_command(self, command):
        try:
            model = self.mediator.model
            view = self.mediator.view

            # Menu
            if command == Enum.MenuCommand.Help:
                message = '''This is an application created to make learning easier. You can use this program to study vocabulary or programming. It's extremely useful if you have an exam, and you need to memorize a lot of stuff.

type in t1 or t2 or t3 or t4 to navigate around the tabs.
type in s1 or s2 or s3 to navigate around services.

Services specialize in different areas of knowledge:

The standard service helps you to quickly create flashcards.
The images service helps you manage images.
The vocabulary service helps you to create flashcards based on words and definitions faster than standard service.



Happy learning!'''
                messagebox.showinfo('Help', message)
            # elif command == Enum.MenuCommand.Dump_Data:
            #     model.dump()
            elif command == Enum.MenuCommand.Exit:
                model.dump()

                keyboard.unhook_all()
                view.root.destroy()
                sys.exit(0)
            elif command == Enum.MenuCommand.Reset_Completion_Count:
                is_ok = messagebox.askokcancel('Confirm', 'Are you sure you want to reset completion count?')

                if is_ok:
                    model.Application['completion_count'] = 0
            elif command == Enum.MenuCommand.Set_Font_Size:
                font_size = SimpleDialog('Font Size', 'Enter font size.', input_class=int)
                default_font = tkinter.font.nametofont('TkDefaultFont')
                default_font.config(size=font_size)
                print(f"Font size set to {font_size}")
            elif command == Enum.MenuCommand.Print_Sets_Randomly:
                files = model.get_set_files()
                # random.shuffle(files)
                print(files)

                message = f'{files}'
                messagebox.showinfo('Print_Sets_Randomly', message)
            elif command == Enum.MenuCommand.Set_Preset:
                print('presets\n', dir(Enum.Preset))
                preset_type = SimpleDialog('Preset', f'Enter preset type:\n{[attr for attr in dir(Enum.Preset) if not attr.startswith('__')]}', input_class=str)
                if preset_type in dir(Enum.Preset):
                    preset_type: dict = copy.deepcopy(Enum.Preset[preset_type].value)

                    for setting, value in preset_type.items():
                        model.Application['settings'][setting] = value
            elif command == Enum.MenuCommand.Randomize_Practice:
                new_value = not model.settings[Enum.Settings.Randomize_Practice]
                model.settings[Enum.Settings.Randomize_Practice] = new_value
            elif command == Enum.MenuCommand.Save_Practice_Set:
                print(f"PracticeStash\n\tlength: {len(model.PracticeStash)}\n\tkeys: {model.PracticeStash.keys()}")
                set_name = SimpleDialog('Save', f"Enter set name to save as.\nNote: you can delete an existing set if the practice set happens to be empty.\n{list(model.PracticeStash.keys())}")

                if len(model.practice_set.terms) == 0:
                    if set_name in model.PracticeStash:
                        del model.PracticeStash[set_name]
                else:
                    model.PracticeStash[set_name] = copy.deepcopy(model.practice_set.terms)

                # model.practice_set.terms.clear()

            elif command == Enum.MenuCommand.Load_Practice_Set:
                print(f"PracticeStash\n\tlength: {len(model.PracticeStash)}\n\tkeys: {model.PracticeStash.keys()}")
                set_name = SimpleDialog('Load', f'Enter set name to load:\n{list(model.PracticeStash.keys())}')
                self.model.practice_set = Set(model.PracticeStash[set_name])

            # Harvest
            elif command == Enum.HarvestCommand.Back:
                model.Application['harvest_set_index'] -= 1
            elif command == Enum.HarvestCommand.Forward:
                model.Application['harvest_set_index'] += 1
            elif command == Enum.HarvestCommand.Harvest:
                is_ok = messagebox.askokcancel('Confirm', 'Are you sure you want to harvest?')

                if is_ok:
                    model.practice_set.update(model.harvest_set)
                    model.harvest_set.clear()
            elif command == Enum.HarvestCommand.Clear:
                is_ok = messagebox.askokcancel('Confirm', 'Are you sure you clear harvest_set?')

                if is_ok:
                    model.harvest_set.clear()
            elif command == Enum.HarvestCommand.Delete:
                harvest_set_index = model.Application['harvest_set_index']
                term = model.harvest_set.index(harvest_set_index)

                if term:
                    del model.harvest_set.terms[term['identifier']]
            elif command == Enum.HarvestCommand.Reenter:
                harvest_set_index = model.Application['harvest_set_index']
                term = model.harvest_set.index(harvest_set_index)

                if term:
                    Set.reenter(term)
            elif command == Enum.HarvestCommand.Practice:
                harvest_set_index = model.Application['harvest_set_index']
                term = model.harvest_set.index(harvest_set_index)

                if term:
                    model.practice_set.update({term['identifier']: term})
                    self.on_menu_command(Enum.HarvestCommand.Delete)
            elif command == Enum.HarvestCommand.Title:
                current_title = model.Application['harvest_set_title']
                title = SimpleDialog('Title', 'Enter title.', initial_value=current_title)

                if title:
                    model.Application['harvest_set_title'] = title
                else:
                    model.Application['harvest_set_title'] = 'Untitled'
            elif command == Enum.HarvestCommand.Save:
                harvest_title = model.Application['harvest_set_title']
                harvest_set_id = model.new_identifier()

                name1 = f'{harvest_title}_{harvest_set_id}.txt'
                name2 = f'{harvest_set_id}_{harvest_title}.txt'

                with open(fr'{Enum.SETS_DIRECTORY}\{name2}', mode='w') as fp:
                    json.dump(model.harvest_set.terms, fp)

                    pyperclip.copy(f'{name2}')
            elif command == Enum.HarvestCommand.Load:
                harvest_title = SimpleDialog('Load', 'Enter harvest title.')

                path = fr'{Enum.SETS_DIRECTORY}\{harvest_title}'

                if os.path.exists(path):
                    with open(path, mode='r') as fp:
                        terms = json.load(fp)
                        model.harvest_set.update(terms)

                        print(f'\n{harvest_title} loaded successfully!\n')
            elif command == Enum.HarvestCommand.Schedule_All:
                schedule_type = SimpleDialog('Schedule', 'Enter schedule name, or a json list, like [0, 100, 200].', input_class=str)

                try:
                    new_schedule = json.loads(schedule_type)

                    # check if list is entered correctly
                    if type(new_schedule) is not list or len(new_schedule) <= 0:
                        raise ValueError

                    for value in new_schedule:
                        if type(value) is not int or value < 0:
                            raise ValueError

                    for term_id, term in model.harvest_set.items():
                        model.harvest_set.terms[term_id]['schedule'] = new_schedule.copy()
                except:
                    if schedule_type in dir(Enum.Schedule):
                        new_schedule: list = copy.deepcopy(Enum.Schedule[schedule_type].value)

                        for term_id, term in model.harvest_set.items():
                            model.harvest_set.terms[term_id]['schedule'] = new_schedule.copy()

                    else:
                        print('Failed to Schedule_All')
            elif command == Enum.HarvestCommand.First:
                model.Application['harvest_set_index'] = 0
            elif command == Enum.HarvestCommand.Load_All_Sets:
                files = model.get_set_files()

                terms = {}

                for harvest_title in files:
                    path = fr'{Enum.SETS_DIRECTORY}\{harvest_title}'

                    if os.path.exists(path):
                        with open(path, mode='r') as fp:
                            # terms = json.load(fp)
                            # model.harvest_set.update(terms)

                            terms.update(json.load(fp))

                # initial sorting
                terms = dict(sorted(terms.items()))
                model.harvest_set.update(terms)

            # elif command == Enum.HarvestCommand.Toggle_Trial:
            #     for term_id, term in model.harvest_set.items():
            #         if 'on_trial' in model.harvest_set.terms[term_id]:
            #             model.harvest_set.terms[term_id]['on_trial'] = not model.harvest_set.terms[term_id]['on_trial']
            #         else:
            #             model.harvest_set.terms[term_id]['on_trial'] = True
            #
            #         if model.harvest_set.terms[term_id]['on_trial']:
            #             model.harvest_set.terms[term_id]['schedule'] = Enum.trials_list[0].copy()
            # elif command == Enum.HarvestCommand.Pacify:
            #     for term_id, term in model.harvest_set.items():
            #         if 'passive' in model.harvest_set.terms[term_id]:
            #             model.harvest_set.terms[term_id]['passive'] = not model.harvest_set.terms[term_id]['passive']
            #         else:
            #             model.harvest_set.terms[term_id]['passive'] = True
            # elif command == 'Enum.HarvestCommand.Reassign_IDs':
            #     reassigned_terms = {}
            #
            #     for term_id, term in model.harvest_set.items():
            #         # new_term_id = model.new_identifier()
            #         new_term_id = str(uuid.uuid4())
            #
            #         reassigned_terms[new_term_id] = term
            #         term["identifier"] = new_term_id
            #
            #     model.harvest_set.clear()
            #     model.harvest_set.update(reassigned_terms)
            #
            #     # Do Not Update, or otherwise it is an infinite loop
            #     return
            elif command == Enum.HarvestCommand.Load_From_Practice_Set:
                model.harvest_set.update(model.practice_set)

            elif command == Enum.HarvestCommand.Assign_Terms_Set_Title_Context:
                for term_id, term in model.harvest_set.items():
                    new_context_text = model.Application['harvest_set_title']

                    if new_context_text == 'Untitled':
                        new_context_text = None

                    term["context_text"] = new_context_text

            elif command == Enum.HarvestCommand.Help:
                message = f'''You'll see a folder named collections. Use it to organize all of your sets. You can ideally download some sets from the internet. But, you'll have to manually move them to the main directory if you want to be able to load them and practice.

There are two folders: sets and images. These are two folders, holding all the necessary information for your practice. If you want to try a different pair, unfortunately, you will have to exit the program, and manually replace it with another pair. Store those pairs in a folder, named collections to stay organized.

This program is primarily used for memorizing by using spaced repetition. A set contains a bunch of terms, which is basically like a flashcard. A schedule is a list of numbers, representing seconds. For example, the 0 represents you want to learn it now. The 15 represents you want to learn it after 15 seconds.'''

                messagebox.showinfo('Help', message)

            # Standard
            elif command == Enum.StandardCommand.Enter:
                term_to_enter = model.Services['standard']['term_to_enter']

                # Prevent entering if term is empty
                if term_to_enter != Enum.Model.Services.value['standard']['term_to_enter']:
                    term_to_enter.update({
                        'service': Enum.Service.Standard.name,
                        'schedule': copy.copy(model.Services['standard']['default_schedule']),
                    })
                    model.harvest_enter(term_to_enter)

                    # Reset
                    self.on_menu_command(Enum.StandardCommand.Reset)
            elif command == Enum.StandardCommand.Reset:
                # Don't reset context_text
                last_context = model.Services['standard']['term_to_enter'].get('context_text', None)

                term_to_enter = copy.deepcopy(Enum.Model.Services.value['standard']['term_to_enter'])
                model.Services['standard']['term_to_enter'] = term_to_enter

                model.Services['standard']['term_to_enter']['context_text'] = last_context
            elif command == Enum.StandardCommand.Set_Subject_Text:
                term_to_enter = model.Services['standard']['term_to_enter']
                Set.reenter(term_to_enter, 'subject_text', 'Enter subject.')
            elif command == Enum.StandardCommand.Set_Predicate_Text:
                term_to_enter = model.Services['standard']['term_to_enter']
                Set.reenter(term_to_enter, 'predicate_text', 'Enter predicate.')
            elif command == Enum.StandardCommand.Set_Context_Text:
                term_to_enter = model.Services['standard']['term_to_enter']
                Set.reenter(term_to_enter, 'context_text', 'Enter context.')
            elif command == Enum.StandardCommand.Set_Subject_Image:
                image_id = f'img_{model.new_identifier()}.png'
                Screenshot(screenshot_name=image_id, master=self)

                term_to_enter = model.Services['standard']['term_to_enter']
                term_to_enter['subject_image'] = image_id

                # persist
                model.Services['standard']['persist_subject_image'] = image_id
                model.Services['standard']['persist_image_id'] = image_id
            elif command == Enum.StandardCommand.Set_Predicate_Image:
                image_id = f'img_{model.new_identifier()}.png'
                Screenshot(screenshot_name=image_id, master=self)

                term_to_enter = model.Services['standard']['term_to_enter']
                term_to_enter['predicate_image'] = image_id

                # persist
                model.Services['standard']['persist_predicate_image'] = image_id
                model.Services['standard']['persist_image_id'] = image_id
            # elif command == Enum.StandardCommand.Set_Context_Image:
            #     pass
            # elif command == Enum.StandardCommand.Discard_Images:
            #     pass
            elif command == Enum.HiddenCommand.Set_Subject_And_Predicate_Image:
                image_id = f'img_{model.new_identifier()}.png'
                Screenshot(screenshot_name=image_id, master=self)

                term_to_enter = model.Services['standard']['term_to_enter']
                term_to_enter['predicate_image'] = image_id
                term_to_enter['subject_image'] = image_id

                # persist
                model.Services['standard']['persist_subject_and_predicate_image'] = image_id
                model.Services['standard']['persist_image_id'] = image_id
            elif command == Enum.StandardCommand.Toggle_Persist_Image:
                model.Services['standard']['persist'] = not model.Services['standard']['persist']
                print("model.Services['standard']['persist']:", model.Services['standard']['persist'])
            elif command == Enum.StandardCommand.Set_Default_Schedule:
#                 message = f'''Schedule names:
# {[attr for attr in dir(Enum.Schedule) if not attr.startswith('__')]}
# '''
                schedule_type = SimpleDialog('Schedule', 'Enter schedule name, or a json list, like [0, 100, 200].', input_class=str)

                try:
                    new_default_schedule = json.loads(schedule_type)

                    # check if list is entered correctly
                    if type(new_default_schedule) is not list or len(new_default_schedule) <= 0:
                        raise ValueError

                    for value in new_default_schedule:
                        if type(value) is not int or value < 0:
                            raise ValueError

                    model.Services['standard']['default_schedule'] = new_default_schedule.copy()
                except:
                    if schedule_type in dir(Enum.Schedule):
                        new_schedule: list = copy.deepcopy(Enum.Schedule[schedule_type].value)

                        model.Services['standard']['default_schedule'] = new_schedule.copy()
                    else:
                        print('failed to Set_Default_Schedule')
            # elif command == Enum.StandardCommand.Redact:
            #     term_to_enter = model.Services['standard']['term_to_enter']
            #
            #     # Prevent entering if term is empty
            #     if term_to_enter != Enum.Model.Services.value['standard']['term_to_enter']:
            #         term_to_enter.update({
            #             'service': Enum.Service.Standard.name,
            #             'schedule': copy.copy(model.Services['standard']['default_schedule']),
            #             'predicate_text': Vocabulary.simple_redact(term_to_enter['subject_text'])
            #         })
            #         model.harvest_enter(term_to_enter)
            #
            #         # Reset
            #         self.on_menu_command(Enum.StandardCommand.Reset)
            elif command == Enum.StandardCommand.Help:
                message = f'''default_schedule: {model.Services['standard']['default_schedule']}

Hotkeys:
alt+s \t to paste subject_text from your clipboard

alt+p OR alt+d to \t to paste predicate_text from your clipboard

alt+c \t to paste context_text from your clipboard

alt+b \t to paste both subject_text and predicate_text from your clipboard

alt+e \t to enter the term and send it to the harvest tab

alt+r \t to reset the term, useful if you want to redo the term

alt+shift+s \t for screenshotting subject

alt+shift+p \t for screenshotting predicate

alt+shift+b \t for screenshotting both subject and predicate

Tip: if these hotkeys ever become unresponsive, close and reopen the program to fix it.'''
                messagebox.showinfo('Help', message)

            # Images
            elif command == Enum.ImagesCommand.Back:
                model.Services['images']['current_index'] -= 1

                if model.Services['images']['current_index'] == -1:
                    image_files = model.get_image_files()
                    model.Services['images']['current_index'] = len(image_files) - 1
            elif command == Enum.ImagesCommand.Forward:
                model.Services['images']['current_index'] += 1
            elif command == Enum.ImagesCommand.Copy:
                current_index = model.Services['images']['current_index']

                try:
                    image_name = model.get_image_files()[current_index]
                except IndexError:
                    image_name = None

                if image_name:
                    name, extension = image_name.split('.')

                    edited_image = view.tabs[view.Tab.Services.name].tabs[Enum.Service.Images.name].edited_image

                    new_image_name = f"img_{model.new_identifier()}.{extension}"
                    image_file_path_destination = fr"{Enum.IMAGES_DIRECTORY}\{new_image_name}"

                    edited_image.save(image_file_path_destination)

                    # Adjust current_index
                    image_files = model.get_image_files()
                    model.Services['images']['current_index'] = image_files.index(new_image_name)

                    # Extra
                    pyperclip.copy(new_image_name)
            elif command == Enum.ImagesCommand.Screenshot:
                image_id = f'img_{model.new_identifier()}.png'
                Screenshot(screenshot_name=image_id, master=self)

                # Rare case if images_files are empty
                image_files = model.get_image_files()
                if len(image_files):
                    model.Services['images']['current_index'] = len(image_files)
                else:
                    model.Services['images']['current_index'] = 0
            elif command == Enum.ImagesCommand.Delete:
                current_index = model.Services['images']['current_index']

                try:
                    image_file = model.get_image_files()[current_index]
                except IndexError:
                    image_file = None

                if image_file:
                    os.remove(fr"{Enum.IMAGES_DIRECTORY}\{image_file}")
            elif command == Enum.ImagesCommand.Replace:
                current_index = model.Services['images']['current_index']

                try:
                    image_name = model.get_image_files()[current_index]
                except IndexError:
                    image_name = None

                if image_name:
                    edited_image = view.tabs[view.Tab.Services.name].tabs[Enum.Service.Images.name].edited_image

                    image_file_path_destination = fr"{Enum.IMAGES_DIRECTORY}\{image_name}"

                    os.remove(image_file_path_destination)
                    edited_image.save(image_file_path_destination)

                    image_files = model.get_image_files()
                    model.Services['images']['current_index'] = image_files.index(image_name)
            elif command == Enum.ImagesCommand.Fill_Crimson:
                services = view.tabs[view.Tab.Services.name]
                images = services.tabs[Enum.Service.Images.name]
                images.to_fill = Enum.CRIMSON
            elif command == Enum.ImagesCommand.Fill_None:
                services = view.tabs[view.Tab.Services.name]
                images = services.tabs[Enum.Service.Images.name]
                images.to_fill = None

            elif command == Enum.ImagesCommand.First:
                model.Services['images']['current_index'] = 0

            elif command == Enum.ImagesCommand.Help:
                message = '''Given the selected image, the name of the image will be in your clipboard automatically, so that you may paste it and see its name.

You can the commands Fill_Crimson and Fill_None to highlight certain parts of the image. If you want to redo it, hit enter. If you are satisfied with the result, use the command Replace to finalize the image.

The Copy command will duplicate the image, so there will be two duplicated images.
'''

                messagebox.showinfo('Help', message)

            # Practice
            elif command == Enum.PracticeCommand.Delete:
                term_identifier = model.Application['current_practice_term_identifier']
                term = model.practice_set.terms.get(term_identifier, None)

                if term:
                    del model.practice_set.terms[term_identifier]
            elif command == Enum.PracticeCommand.Relearn:
                term_identifier = model.Application['current_practice_term_identifier']
                term = model.practice_set.terms.get(term_identifier, None)

                if term:
                    model.practice_set.schedule(term, 0)
            elif command == Enum.PracticeCommand.Reenter:
                term_identifier = model.Application['current_practice_term_identifier']

                term = model.practice_set.terms.get(term_identifier, None)

                if term:
                    Set.reenter(term)
            elif command == Enum.PracticeCommand.Toggle_Alert:
                new_value = not model.settings[Enum.Settings.Practice_Alert]
                model.settings[Enum.Settings.Practice_Alert] = new_value
            elif command == Enum.PracticeCommand.Set_Practice_Stack_Length:
                integer = SimpleDialog('Stack Length', 'Enter stack length.', input_class=int)
                model.settings[Enum.Settings.Practice_Stack_Length] = integer
            elif command == Enum.PracticeCommand.Clear:
                is_ok = messagebox.askokcancel('Confirm', 'Are you sure you clear practice_set?')

                if is_ok:
                    model.practice_set.clear()
            elif command == Enum.PracticeCommand.Penalize:
                term_identifier = model.Application['current_practice_term_identifier']
                term = model.practice_set.terms.get(term_identifier, None)

                if term:
                    schedule_type = SimpleDialog('Schedule', 'Enter schedule type.', input_class=str)

                    if schedule_type in dir(Enum.Schedule):
                        new_schedule: list = copy.deepcopy(Enum.Schedule[schedule_type].value)

                        term['schedule'] = new_schedule.copy()
            # elif command == Enum.PracticeCommand.Penalize_Standard:
            #     term_identifier = model.Application['current_practice_term_identifier']
            #     term = model.practice_set.terms.get(term_identifier, None)
            #
            #     if term:
            #         new_schedule: list = Enum.Schedule.Standard.value
            #
            #         term['schedule'] = new_schedule.copy()
            #
            #         model.practice_set.schedule(term, 0)
            # elif command == Enum.PracticeCommand.Penalize_Reinforced:
            #     term_identifier = model.Application['current_practice_term_identifier']
            #     term = model.practice_set.terms.get(term_identifier, None)
            #
            #     if term:
            #         new_schedule: list = Enum.Schedule.Reinforced.value
            #
            #         term['schedule'] = new_schedule.copy()
            #
            #         model.practice_set.schedule(term, 0)
            elif command == Enum.PracticeCommand.Schedule_One_Index:
                practices = view.tabs[view.Tab.Practice.name]
                main_practice_widget = practices.main_practice_widget

                main_practice_widget.verify_user_input(Enum.Scheduling.ScheduleIt)
            elif command == Enum.PracticeCommand.Copy_Subject:
                term_identifier = model.Application['current_practice_term_identifier']
                term = model.practice_set.terms.get(term_identifier, None)

                if term and "subject_text" in term:
                    pyperclip.copy(term["subject_text"])

                    practices = view.tabs[view.Tab.Practice.name]
                    main_practice_widget = practices.main_practice_widget
                    main_practice_widget.entry_text_variable.set(term["subject_text"])

                    # Do not update
                    return

            elif command == Enum.PracticeCommand.Return:
                term_identifier = model.Application['current_practice_term_identifier']
                term = model.practice_set.terms.get(term_identifier, None)

                if term:
                    practices = view.tabs[view.Tab.Practice.name]
                    main_practice_widget = practices.main_practice_widget
                    main_practice_widget.on_entry_return(None)

                    # Do not update
                    return

            # elif command == Enum.PracticeCommand.Sound_Terms:
            #     practice_tab = view.tabs[view.Tab.Practice.name]
            #     practice_tab.sound_terms = not practice_tab.sound_terms
            #     print("practice_tab.sound_terms", practice_tab.sound_terms)
            #     # practice_tab.update()

            elif command == Enum.PracticeCommand.Toggle_Auto_Sound_Subjects:
                model.Services['standard']['practice']['auto_sound_subjects'] = not model.Services['standard']['practice']['auto_sound_subjects']

            elif command == Enum.PracticeCommand.Toggle_Display_Subject_Hint:
                model.Services['standard']['practice']['display_subject_hint'] = not model.Services['standard']['practice']['display_subject_hint']

            elif command == Enum.PracticeCommand.Toggle_See_Subject_And_Predicate_Difference:
                model.Services['standard']['practice']['see_subject_and_predicate_difference'] = not model.Services['standard']['practice']['see_subject_and_predicate_difference']

            elif command == Enum.PracticeCommand.Help:
                auto_sound_subjects = model.Services['standard']['practice']['auto_sound_subjects']
                display_subject_hint = model.Services['standard']['practice']['display_subject_hint']
                see_subject_and_predicate_difference = model.Services['standard']['practice']['see_subject_and_predicate_difference']
                message = f'''Standard Service:
auto_sound_subjects: {auto_sound_subjects}
display_subject_hint: {display_subject_hint}
see_subject_and_predicate_difference: {see_subject_and_predicate_difference}

Type in:
/ \t to see subject_text

sound \t to sound out the subject_text

// \t to see subject_text

/// \t to see both subject_text and predicate_text

. OR ; \t to see predicate_text

.. OR ;; \t to see predicate_text 

The Relearn command is extremely useful if you want to redo the space repetition all over again, starting at 0.
'''
                messagebox.showinfo('Help', message)


            # Translation
            # elif command == Enum.TranslationCommand.Translate_Text:
            #     translation_text: str = model.Services['translation']['translation_text']
            #     words_at_a_time = 4
            #     word_frequency = model.Services['translation']['word_frequency']
            #
            #     match model.Services['translation']['language'].lower():
            #         case 'japanese' | 'tangorin':
            #             if '\n' in translation_text:
            #                 original, translated = translation_text.split('\n')
            #             elif '。 ' in translation_text:
            #                 original, translated = translation_text.split('。 ')
            #             else:
            #                 original = translation_text
            #                 translated = None
            #
            #             items = Translation.process_japanese(original)
            #
            #             # Counting
            #             for japanese, pronunciation in items:
            #                 if japanese not in word_frequency:
            #                     word_frequency[japanese] = 0
            #
            #                 word_frequency[japanese] += 1
            #
            #             print()
            #             print(items)
            #             print('len(items)', len(items))
            #
            #             # Pronunciation
            #             for japanese, pronunciation in items:
            #                 if word_frequency[japanese] > 1:
            #                     continue
            #
            #                 if len(pronunciation) <= 3:
            #                     continue
            #
            #                 # Redacted pronunciation
            #                 term_to_enter = model.Services['standard']['term_to_enter']
            #
            #                 redacted_pronunciation = Vocabulary.redact(pronunciation)
            #                 # term_to_enter['context_text'] = 'rRr'
            #                 term_to_enter['subject_text'] = pronunciation
            #                 term_to_enter['predicate_text'] = redacted_pronunciation
            #
            #                 self.on_menu_command(Enum.StandardCommand.Enter)
            #
            #             # Pronunciation
            #             for japanese, pronunciation in items:
            #                 if word_frequency[japanese] > 1:
            #                     continue
            #
            #                 term_to_enter = model.Services['standard']['term_to_enter']
            #
            #                 # term_to_enter['context_text'] = 'pPp'
            #                 term_to_enter['subject_text'] = pronunciation
            #                 term_to_enter['predicate_text'] = japanese
            #
            #                 self.on_menu_command(Enum.StandardCommand.Enter)
            #
            #             # Meanings
            #             # translations = []
            #
            #             for japanese, pronunciation in items:
            #                 if word_frequency[japanese] > 1:
            #                     continue
            #
            #                 try:
            #                     # translation = translator.translate(japanese, src=googletrans.LANGCODES['japanese']).text
            #
            #                     # # For japanese
            #                     # term_to_enter = model.Services['standard']['term_to_enter']
            #                     # term_to_enter['context_text'] = 'mMm'
            #                     # term_to_enter['subject_text'] = translation
            #                     # term_to_enter['predicate_text'] = japanese
            #                     #
            #                     # self.on_menu_command(Enum.StandardCommand.Enter)
            #                     #
            #                     # translations.append(translation)
            #
            #                     # For pronunciation
            #                     term_to_enter = model.Services['standard']['term_to_enter']
            #                     # term_to_enter['context_text'] = 'mMm'
            #                     # term_to_enter['subject_text'] = translation
            #                     term_to_enter['predicate_text'] = pronunciation
            #
            #                     self.on_menu_command(Enum.StandardCommand.Enter)
            #
            #                     time.sleep(0.1)
            #                 except:
            #                     # translations.append(None)
            #                     time.sleep(3)
            #
            #             # for (japanese, pronunciation), translation in zip(items, translations):
            #             #     if translation:
            #             #         # For pronunciation
            #             #         term_to_enter = model.Services['standard']['term_to_enter']
            #             #         term_to_enter['context_text'] = 'mMm'
            #             #         term_to_enter['subject_text'] = translation
            #             #         term_to_enter['predicate_text'] = pronunciation
            #             #
            #             #         self.on_menu_command(Enum.StandardCommand.Enter)
            #
            #             term_to_enter = model.Services['standard']['term_to_enter']
            #             term_to_enter['context_text'] = None
            #
            #             chunks = len(items)/words_at_a_time
            #
            #             japanese_items = list(map(lambda x: x[0], items))
            #             translated_items = list(map(lambda x: x[1], items))
            #
            #             for i in range(math.ceil(chunks)):
            #                 term_to_enter = model.Services['standard']['term_to_enter']
            #
            #                 term_to_enter['context_text'] = translated
            #                 term_to_enter['subject_text'] = f'{' '.join(translated_items[:i*4])} | {' - '.join(translated_items[i*4:(i+1)*4])}'
            #                 term_to_enter['predicate_text'] = f'{''.join(japanese_items[:i*4])} | {' - '.join(japanese_items[i*4:(i+1)*4])}\n{' '.join(translated_items[:(i)*4])}'
            #
            #                 self.on_menu_command(Enum.StandardCommand.Enter)
            #
            #             term_to_enter = model.Services['standard']['term_to_enter']
            #             term_to_enter['context_text'] = None
            # elif command == Enum.TranslationCommand.Set_Source:
            #     source = SimpleDialog('Source', 'Enter source.', input_class=str)
            #
            #     if source in googletrans.LANGUAGES:
            #         model.Services['translation']['src'] = source
            # elif command == Enum.TranslationCommand.Set_Destination:
            #     destination = SimpleDialog('Destination', 'Enter destination.', input_class=str)
            #
            #     if destination in googletrans.LANGUAGES:
            #         model.Services['translation']['dest'] = destination
            elif command == Enum.PracticeCommand.Randomize_Order:
                model.practice_set.randomize_order()

            # elif command == Enum.TranslationCommand.Reset_All:
            #     is_ok = messagebox.askokcancel('Confirm', 'Are you sure you want to reset all?')
            #
            #     if is_ok:
            #         model.Services['translation'] = copy.deepcopy(Enum.Model.Services.value['translation'])
            # elif command == Enum.TranslationCommand.Set_Language:
            #     language = SimpleDialog('Language', 'Enter language.', input_class=str)
            #     model.Services['translation']['language'] = language

            # Vocabulary
            elif command == Enum.VocabularyCommand.Extend_Vocabulary_List:
                vocabulary_list_extension_string = SimpleDialog('Vocabulary List', 'Enter vocabulary list extension.', input_class=str)

                vocabulary_list_extension = []

                try:
                    # Method 1
                    vocabulary_list_extension.extend(json.loads(vocabulary_list_extension_string))
                except:
                    try:
                        # Method 2 - Security Hazard?
                        # vocabulary_list_extension.extend(list(eval(vocabulary_list_extension_string)))
                        raise Exception
                    except:
                        # Method 3
                        sep = ' '
                        if vocabulary_list_extension_string.count(',') >= 2:
                            sep = ','

                        if vocabulary_list_extension_string.count(', ') >= 2:
                            sep = ', '

                        if vocabulary_list_extension_string.count('\n') >= 2:
                            sep = '\n'

                        vocabulary_list_extension.extend(vocabulary_list_extension_string.split(sep))

                model.Services['vocabulary']['vocabulary_list'].extend(vocabulary_list_extension)
            elif command == Enum.VocabularyCommand.Rewrite_Word:
                if model.Services['vocabulary']['vocabulary_list']:
                    new_word = SimpleDialog('Rewrite Word', 'Enter word.', input_class=str)

                    model.Services['vocabulary']['vocabulary_list'][0] = new_word
            elif command == Enum.VocabularyCommand.Discard_Word:
                if model.Services['vocabulary']['vocabulary_list']:
                    del model.Services['vocabulary']['vocabulary_list'][0]
            elif command == Enum.VocabularyCommand.Clear_Vocabulary_List:
                is_ok = messagebox.askokcancel('Confirm', 'Are you sure you want to clear vocabulary list?')

                if is_ok:
                    model.Services['vocabulary']['vocabulary_list'].clear()
            elif command == Enum.VocabularyCommand.Rewrite_Suffix:
                suffix_string = SimpleDialog('Extra Suffix', 'Enter suffix.', input_class=str)

                model.Services['vocabulary']['extra_suffix'] = suffix_string
            # elif command == Enum.VocabularyCommand.Redact_Vocabulary_List:
            #     is_ok = messagebox.askokcancel('Confirm', 'Are you sure you want to redact vocabulary list?')
            #
            #     if is_ok:
            #         for word in model.Services['vocabulary']['vocabulary_list']:
            #             predicate_text = Vocabulary.simple_redact(word)
            #
            #             # Use standard service
            #             term_to_enter = model.Services['standard']['term_to_enter']
            #             term_to_enter['subject_text'] = word
            #             term_to_enter['predicate_text'] = predicate_text
            #             self.on_menu_command(Enum.StandardCommand.Enter)
            #
            #     model.Services['vocabulary']['vocabulary_list'].clear()
            # elif command == Enum.VocabularyCommand.Redact_Word:
            #     word = model.Services['vocabulary']['vocabulary_list'][0]
            #     predicate_text = Vocabulary.simple_redact(word)
            #
            #     # Use standard service
            #     term_to_enter = model.Services['standard']['term_to_enter']
            #     term_to_enter['subject_text'] = word
            #     term_to_enter['predicate_text'] = predicate_text
            #     self.on_menu_command(Enum.StandardCommand.Enter)
            #
            #     self.on_menu_command(Enum.VocabularyCommand.Discard_Word)
            elif command == Enum.VocabularyCommand.Reverse:
                model.Services['vocabulary']['reversed'] = not model.Services['vocabulary']['reversed']
            elif command == Enum.VocabularyCommand.Copy_Vocabulary_List:
                pyperclip.copy(str(model.Services['vocabulary']['vocabulary_list']))
            elif command == Enum.VocabularyCommand.Help:
                message = '''Hotkeys:
                
ctrl+v \t to paste definition from your clipboard and send it to the harvest tab

alt+a \t to add a new word to the list from your clipboard

Note: these hotkeys will be disabled if you switch to another service, because you may use ctrl+v by accident. 

If reversed is set to true, it's assumed the list contains definitions, instead of words.

The extra suffix is useful when you are using, for example, Google. You can search "pabulum def" instead of "pabulum" for better internet search results. Note that the extra suffix won't be included in the final term.


For extending the vocabulary list, you may enter these as an example:

["word1", "word2", "word3"]

word1, word2, word3

word1,word2,word3

word1
word2
word3'''
                messagebox.showinfo('Help', message)

            # Regex
            elif command == Enum.RegexCommand.Enter_Regex:
                regex = SimpleDialog('Regex', 'Enter regex.', input_class=str)
                text = model.Services['regex']['text']

                try:
                    for subject_text, predicate_text in re.findall(regex, text):
                        if model.Services['regex']['reverse']:
                            subject_text, predicate_text = predicate_text, subject_text

                        # Use standard service
                        term_to_enter = model.Services['standard']['term_to_enter']
                        term_to_enter['subject_text'] = subject_text
                        term_to_enter['predicate_text'] = predicate_text
                        self.on_menu_command(Enum.StandardCommand.Enter)

                except Exception as e:
                    print(e)
            # elif command == Enum.RegexCommand.Reset:
            #     pass
            elif command == Enum.RegexCommand.Reverse_Groups:
                model.Services['regex']['reverse'] = not model.Services['regex']['reverse']
            elif command == Enum.RegexCommand.Slice:
                text = model.Services['regex']['text']
                words = text.split(' ')

                for i, word in enumerate(words):
                    if i == 0:
                        continue

                    subject_text = word
                    predicate_text = ' '.join(words[:i])

                    # Use standard service
                    term_to_enter = model.Services['standard']['term_to_enter']
                    term_to_enter['subject_text'] = subject_text
                    term_to_enter['predicate_text'] = predicate_text
                    self.on_menu_command(Enum.StandardCommand.Enter)

            # General
            elif type(command) == str:
                if command.startswith('t'):
                    # Short-cut for switching tabs
                    index = command[1:]

                    if not index.isnumeric():
                        return

                    index = int(index)

                    if index not in range(1, len(view.tabs) + 1):
                        return

                    view.notebook.select(index - 1)
                elif command.startswith('s'):
                    # automatically go to Services tab
                    view.notebook.select(3 - 1)

                    if type(command) == str and command.startswith('s'):
                        # Short-cut for switching services
                        index = command[1:]

                        if not index.isnumeric():
                            return

                        index = int(index)

                        services = view.tabs[view.Tab.Services.name]

                        if index not in range(1, len(services.tabs.values()) + 1):
                            return

                        services.notebook.select(index - 1)
                elif command.startswith('img_'):
                    image_file_path_destination = fr"{Enum.IMAGES_DIRECTORY}\{command}"
                    if os.path.exists(image_file_path_destination):
                        image_files = model.get_image_files()
                        model.Services['images']['current_index'] = image_files.index(command)
                elif command.isnumeric():
                    # Short-cut for selecting command
                    index = int(command)

                    commands = tuple(view.tabs.values())[
                        view.notebook.index(view.notebook.select())
                    ].commands

                    if index not in range(1, len(commands) + 1):
                        return

                    command = commands[index - 1]

                    self.on_menu_command(command)

            self.update()

        except Exception as e:
            print(f"An error occurred: {e}")