import tkinter as tk
from tkinter import ttk
import keyboard
import pyperclip
import itertools
import copy
import collections
import os
import pyttsx3
import string
import threading
import time

from utils import Enum
from utils.TermDisplayer import TermDisplayer
from utils import ImageFuncs
from services.Vocabulary import Vocabulary

pyttsx3_engine = pyttsx3.init()
voices = pyttsx3_engine.getProperty('voices')
english_voice = voices[0]
russian_voice = voices[2]

strip_subject_text = True
strip_displayed_predicate = True


def sliding_window(iterable, n):
    "Collect data into overlapping fixed-length chunks or blocks."
    # sliding_window('ABCDEFG', 4) → ABCD BCDE CDEF DEFG
    iterator = iter(iterable)
    window = collections.deque(itertools.islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)


# if os.path.exists(fr'{os.getcwd()}\5000-words.txt'):
#     with open('5000-words.txt', 'r', encoding='utf-8') as file:
#         most_common_english_words = set(file.readlines())
# else:
#     most_common_english_words = set()
#
# # print('most_common_english_words:', len(most_common_english_words))


def point_of_difference(string_1, string_2):
    i = 0

    for letter_1, letter_2 in zip(string_1, string_2):
        if letter_1 != letter_2:
            return i

        i += 1

    return 0


def insert_in_label(text, insertion, position):
    return "%s%s%s" % (text[:position], insertion, text[position:])


def see_subject_and_predicate_difference(subject: str, predicate: str) -> tuple[str, str]:
    subject_lines = subject.split('\n')
    predicate_lines = predicate.split('\n')

    if len(subject_lines) <= 1 or len(predicate_lines) <= 1:
        return subject, predicate

    new_subject_lines = []
    new_predicate_lines = []

    for subject_line, predicate_line in itertools.zip_longest(subject_lines, predicate_lines, fillvalue=''):
        if subject_line != predicate_line:
            # Line aid
            subject_line = '[+]' + subject_line
            predicate_line = '[+]' + predicate_line

            # Line character aid
            index = point_of_difference(subject_line, predicate_line)
            if index > 2:
                subject_line = insert_in_label(
                    text=subject_line,
                    insertion='|',
                    position=index
                )

        new_subject_lines.append(subject_line)
        new_predicate_lines.append(predicate_line)

    return '\n'.join(new_subject_lines), '\n'.join(new_predicate_lines)


class PracticeWidget:
    def __init__(self, view, master, term: dict, is_main=False, is_focused=False):
        self.view = view
        self.term = term

        self.is_sounding = False
        self.is_main = is_main
        self.is_focused = is_focused

        # # word_association_help
        # if False:
        #     if 'word_associations' not in term and '\n' not in term['subject_text']:
        #         word_associations = []
        #
        #         for word in most_common_english_words:
        #             word = word.replace('\n', '')
        #
        #             if word[:3] == term['subject_text'][:3].lower():
        #                 if len(word) > 3 and word != term['subject_text']:
        #                     # highlight
        #
        #
        #
        #                     word_associations.append(f'{word}')
        #                     # print(word)
        #             #
        #
        #             if len(word_associations) >= 1:
        #                 break
        #             # for sub_slice in sliding_window(term['subject_text'], 3):
        #             #     substring = ''.join(sub_slice)
        #             #
        #             #     if substring in word and len(word) > 3:
        #             #
        #             #         # highlight
        #             #         i = word.index(substring)
        #             #         word = word[:i] + '/' + word[i:i+3] +'/'+ word[i+3:]
        #             #
        #             #         word = word.replace('\n', '')
        #             #
        #             #         i = term['subject_text'].index(substring)
        #             #         indicator: str = term['subject_text'][:i] + '/' + term['subject_text'][i:i+3] +'/'+ term['subject_text'][i+3:]
        #             #
        #             #         word_associations.append(f'{indicator}\n{word}')
        #             #
        #             # if len(word_associations) >= 1:
        #             #     break
        #
        #         term['word_associations'] = '\n' + '\n\n'.join(word_associations)

        self.returns = 0

        # Unpack text
        context_text = term.get('context_text', None)

        self.context_text = f"{context_text}" if context_text else ''

        subject_text = f"Subject,\n{term['subject_text']}" if term['subject_text'] else 'Subject, '
        predicate_text = f"{term['predicate_text']}" if term['predicate_text'] else ''

        if strip_displayed_predicate:
            predicate_text = predicate_text.strip()

        # # center them (optional)
        # subject_text = f"Subject,\n{'{:^25s}'.format(term['subject_text'])}"
        # predicate_text = '{:^25s}'.format(predicate_text)
        # # (optional)
        # predicate_text = f'\n{predicate_text}'

        model = self.view.mediator.model

        self.subject_text = f"{subject_text}"
        self.predicate_text = f"{predicate_text}"

        # Normalize, because sometimes \n displays as twice
        normalize_text = self.view.mediator.model.normalize_text
        self.subject_text = normalize_text(self.subject_text)
        self.predicate_text = normalize_text(self.predicate_text)

        # Highlight difference
        extra_length = len('Subject, ')
        self.subject_text = self.subject_text[extra_length:]

        if model.Services['standard']['practice']['see_subject_and_predicate_difference']:
            self.subject_text, self.predicate_text = see_subject_and_predicate_difference(self.subject_text, self.predicate_text)

        self.subject_text = 'Subject,\n' + self.subject_text

        # # Add word association
        # if False and 'word_associations' in term:
        #     if not term['word_associations'].isspace():
        #         self.subject_text += ' ' + term['word_associations']
        #         # self.predicate_text += term['word_associations']
        # if False:
        #     self.predicate_text += '\n' * 23 + '-'.join(list(reversed(term['subject_text'])))

        # Add subject hint, by showing the first letter


        original_subject_text = term.get('subject_text', '')
        if model.Services['standard']['practice']['display_subject_hint'] and type(original_subject_text) == str and len(original_subject_text) >= 1:
            self.predicate_text = f"{original_subject_text[0]}-\n\n{self.predicate_text}"

        # Adjust label
        self.label = tk.Label(master, compound='top', justify=tk.LEFT, pady=0)

        self.label.configure(wraplength=max(self.view.root.winfo_width(), 330))

        # Label For Displaying images
        self.label_for_displaying_image = tk.Label(master, compound='top', justify=tk.LEFT, pady=0)
        self.label_for_displaying_image.configure(wraplength=max(self.view.root.winfo_width(), 330))

        self.entry_text_variable = tk.StringVar()
        self.entry = ttk.Entry(master, textvariable=self.entry_text_variable)

        if self.term['index'] < len(self.term['schedule']):
            self.current_interval = self.term['schedule'][self.term['index']]
        else:
            self.current_interval = None

        if self.term['index'] == 0:
            self.show_subject()
        elif self.term['index'] > 0:
            self.show_predicate()

        # # Passive
        # if self.is_main and term.get('passive', False) and self.is_focused and self.current_interval is not None:
        #     if self.current_interval < 6220*2:
        #         self.threaded_sound()
        #     else:
        #         self.show_subject(f'\n{self.term['subject_text']}')

        # label_for_displaying_image is used for displaying the image on the left side, to make it sure it stays there.
        self.label_for_displaying_image.pack(expand=False, side=tk.TOP, anchor=tk.NW)
        self.label.pack(expand=True, side=tk.TOP, anchor=tk.NW)
        self.entry.pack(fill=tk.BOTH, side=tk.TOP)

        self.entry.bind('<Return>', self.on_entry_return)

    def focus(self):
        self.entry.focus()

    @staticmethod
    def detect_language(text: str):
        russian = 'ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'
        english = string.ascii_letters

        if len(set(text).intersection(set(russian))) > 1:
            return russian_voice.id
        else:
            return english_voice.id

    def sound(self, code='review'):
        self.is_sounding = True

        subject = self.term.get('subject_text', '')
        predicate = self.term.get('predicate_text', '')

        subject = '' if not subject else subject
        predicate = '' if not predicate else predicate

        if subject == '' and predicate == '':
            return

        if code == 'review':
            if self.term['index'] == 0:
                pyttsx3_engine.setProperty('voice', self.detect_language(subject))
                pyttsx3_engine.setProperty('rate', 200)
                # rate - default's 200
                # 1. 200
                # 2. 230
                # 3. 250
                # 4. 270

                # Before
                self.on_entry_return()

                pyttsx3_engine.say(subject)
                pyttsx3_engine.runAndWait()

                # self.on_entry_return()

                # pyttsx3_engine.setProperty('voice', self.detect_language(predicate))
                # pyttsx3_engine.say(predicate)
                # pyttsx3_engine.runAndWait()
                # time.sleep(0.3)

                self.on_entry_return()
                self.is_sounding = False
            else:
                pyttsx3_engine.setProperty('voice', self.detect_language(subject))
                pyttsx3_engine.setProperty('rate', 200)
                # rate - 220
                # 1. 230
                # 2. 240
                # 3. 270
                # 4. 300

                # self.entry_text_variable.set('/')
                # self.on_entry_return()
                if predicate and not predicate.isspace():
                    if subject != predicate:
                        self.label.configure(text=self.predicate_text + self.context_text + '\n' + subject)
                    else:
                        self.label.configure(text=self.predicate_text + self.context_text)
                else:
                    self.label.configure(text=self.subject_text + self.context_text)

                pyttsx3_engine.say(subject)
                pyttsx3_engine.runAndWait()

                self.entry_text_variable.set('')

                self.on_entry_return()
                self.is_sounding = False
        elif code == 'subject':
            pyttsx3_engine.setProperty('voice', self.detect_language(subject))
            pyttsx3_engine.setProperty('rate', 275)

            # if not predicate or predicate.isspace():
            # # if subject:
            #     self.label.configure(text=subject) #+ self.context_text)

            pyttsx3_engine.say(subject)
            pyttsx3_engine.runAndWait()

    def threaded_sound(self, code='review'):
        if not self.is_sounding:
            self.is_sounding = True
            thread = threading.Thread(target=self.sound, args=(code,))
            thread.start()
            return thread

    def show_subject_and_predicate(self):
        if self.context_text:
            custom = self.context_text + ',\n' + self.subject_text
        else:
            custom = self.subject_text + self.context_text

        custom += '\n\nPredicate,\n' + self.predicate_text

        self.label.configure(text=custom, justify='left')

        # Image
        if self.term['subject_image']:
            image_path = fr"{Enum.IMAGES_DIRECTORY}\{self.term['subject_image']}"
            # image = Image.open(image_path)
            # image = ImageTk.PhotoImage(image)
            image = ImageFuncs.resize(image_path, **self.view.mediator.model.get_image_requirements())

            if image != '':
                # self.label.image = image
                # self.label.configure(image=image, anchor="w")
                self.label_for_displaying_image.image = image
                self.label_for_displaying_image.configure(image=image, anchor="w")
            else:
                # self.label.configure(image='')
                self.label_for_displaying_image.configure(image='')
        else:
            # self.label.configure(image='')
            self.label_for_displaying_image.configure(image='')

    def show_subject(self, custom=None):
        # # Show schedule
        # if not self.term.get("index", 0):
        #     print(f"Term Schedule: {self.term['schedule']}")

        if self.context_text:
            custom = custom if custom else self.context_text + ',\n' + self.subject_text
        else:
            custom = custom if custom else self.subject_text + self.context_text

        self.label.configure(text=custom, justify='left')

        # Image
        if self.term['subject_image']:
            image_path = fr"{Enum.IMAGES_DIRECTORY}\{self.term['subject_image']}"
            # image = Image.open(image_path)
            # image = ImageTk.PhotoImage(image)
            image = ImageFuncs.resize(image_path, **self.view.mediator.model.get_image_requirements())

            if image != '':
                # self.label.image = image
                # self.label.configure(image=image, anchor="w")
                self.label_for_displaying_image.image = image
                self.label_for_displaying_image.configure(image=image, anchor="w")
            else:
                # self.label.configure(image='')
                self.label_for_displaying_image.configure(image='')
        else:
            # self.label.configure(image='')
            self.label_for_displaying_image.configure(image='')

    def show_predicate(self):
        if self.context_text:
            text_to_display = self.context_text + ',\n' + self.predicate_text
        else:
            text_to_display = self.predicate_text + self.context_text

        self.label.configure(text=text_to_display, justify='left')

        if self.term['predicate_image']:
            image_path = fr"{Enum.IMAGES_DIRECTORY}\{self.term['predicate_image']}"
            # image = Image.open(image_path)
            # image = ImageTk.PhotoImage(image)
            image = ImageFuncs.resize(image_path, **self.view.mediator.model.get_image_requirements())

            if image != '':
                # self.label.image = image
                # self.label.configure(image=image, anchor="w")
                self.label_for_displaying_image.image = image
                self.label_for_displaying_image.configure(image=image, anchor="w")
            else:
                # self.label.configure(image='')
                self.label_for_displaying_image.configure(image='')

                subject = self.term.get('subject_text', '')
                if subject:
                    self.label.configure(text=self.predicate_text + self.context_text + '\n' + Vocabulary.simple_redact(subject))
                else:
                    self.label.configure(
                        text=self.predicate_text + self.context_text + '\n' + 'IMAGE NOT FOUND')

        else:
            # self.label.configure(image='')
            self.label_for_displaying_image.configure(image='')

    def on_entry_return(self, event=None):
        user_input = self.entry_text_variable.get()
        model = self.view.mediator.model

        if not self.term.get("index", 0):
            if user_input == "h":
                old_schedule = self.term['schedule']
                new_schedule = Enum.Schedule.HalfReinforced.value.copy()
                self.term['schedule'] = new_schedule

                print(f"{old_schedule} changed to {new_schedule}")
                return

        if user_input == '/':
            # Short-cut
            self.entry_text_variable.set(self.term['subject_text'])
        elif user_input == 'sound':
            self.entry_text_variable.set("")
            self.threaded_sound()
        elif user_input == '//':
            normalize_text = self.view.mediator.model.normalize_text
            # self.label.configure(text=normalize_text(self.term['subject_text']))
            self.show_subject()
            self.entry_text_variable.set("")
        elif user_input == '///':
            # Subject and Predicate, side-by-side comparison
            self.show_subject_and_predicate()
            self.entry_text_variable.set("")
        elif user_input in ('.', ';'):
            # Short-cut
            self.entry_text_variable.set(self.term['predicate_text'])
        elif user_input in ('..', ';;'):
            normalize_text = self.view.mediator.model.normalize_text
            self.label.configure(text=normalize_text(self.term['predicate_text']))
            self.entry_text_variable.set("")
        else:
            self.returns += 1

            # # Review Mode
            # if model.Services['standard'].get('review_mode', False):
            #     if len(self.term['schedule']) == 1:
            #         self.review_verify_user_input(user_input)
            #         self.view.mediator.controller.update()
            #
            #         return

            # Enable command & avoid auto-update
            if user_input:
                self.view.mediator.controller.on_menu_command(user_input)

            # Pick message and schedule accordingly
            if self.term['index'] == 0:
                if self.returns == 1:
                    self.show_predicate()
                elif self.returns == 2:
                    self.verify_user_input(user_input)
                    self.view.mediator.controller.update()
            elif self.term['index'] > 0:
                self.verify_user_input(user_input)
                self.view.mediator.controller.update()

    def review_verify_user_input(self, user_input):
        if user_input == '' or user_input == self.term['subject_text'] or user_input == Enum.Scheduling.ScheduleIt:
            scheduling = self.view.mediator.model.practice_set.schedule(self.term)

            # # Additional Aid
            # self.threaded_sound('subject')
        else:
            new_schedule: list = copy.deepcopy(Enum.Schedule.HalfReinforced.value).copy()

            self.term['schedule'] = new_schedule

            scheduling = self.view.mediator.model.practice_set.schedule(self.term, 0)

            # # Additional Aid
            # self.threaded_sound('subject')

    def verify_user_input(self, user_input):
        scheduling = None
        model = self.view.mediator.model

        if self.term['subject_text'] is None:
            subject_text = None
        else:
            subject_text = self.term['subject_text'].strip()

        if user_input == '' or user_input == self.term['subject_text'] or user_input == Enum.Scheduling.ScheduleIt:
            scheduling = self.view.mediator.model.practice_set.schedule(self.term)

            # Additional Aid
            if model.Services['standard']['practice']['auto_sound_subjects']:
                self.threaded_sound('subject')
        elif strip_subject_text and type(subject_text) == str:
            if user_input.strip().lower() == self.term['subject_text'].strip().lower():
                scheduling = self.view.mediator.model.practice_set.schedule(self.term)

                # Additional Aid
                if model.Services['standard']['practice']['auto_sound_subjects']:
                    self.threaded_sound('subject')
        elif self.term['index'] == 1 and self.view.mediator.model.settings[Enum.Settings.Relearn_Index_One]:
            # # Auto-penalize
            # if self.view.mediator.model.settings[Enum.Settings.Auto_Penalize]:
            #     schedule_type = model.settings[Enum.Settings.Auto_Penalize]
            #
            #     if schedule_type in dir(Enum.Schedule):
            #         new_schedule: list = copy.deepcopy(Enum.Schedule[schedule_type].value).copy()
            #
            #         if len(new_schedule) > len(self.term['schedule']):
            #             self.term['schedule'] = new_schedule

            scheduling = self.view.mediator.model.practice_set.schedule(self.term, 0)

            # Additional Aid
            if model.Services['standard']['practice']['auto_sound_subjects']:
                self.threaded_sound('subject')

        if scheduling == Enum.Scheduling.Completed:
            model.Application['completion_count'] += 1


class HarvestWidget:
    def __init__(self, view):
        self.view = view
        self.master = view.root

        self.GROUP = Standard

        self.root = ttk.Frame(master=self.master)

        # Define TermDisplayer
        self.term_displayer = TermDisplayer(self.view, self.root)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.StandardCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

        # Hotkeys
        keyboard.add_hotkey('alt+s', self.on_subject_paste)
        keyboard.add_hotkey('alt+p', self.on_predicate_paste)
        keyboard.add_hotkey('alt+c', self.on_context_paste)
        keyboard.add_hotkey('alt+b', self.on_subject_and_predicate_paste)

        keyboard.add_hotkey('alt+d', self.on_predicate_paste)

        keyboard.add_hotkey('alt+e', lambda: self.on_menu_command(Enum.StandardCommand.Enter))
        keyboard.add_hotkey('alt+r', lambda: self.on_menu_command(Enum.StandardCommand.Reset))

        keyboard.add_hotkey('alt+shift+s', self.on_subject_screenshot)
        keyboard.add_hotkey('alt+shift+p', self.on_predicate_screenshot)
        keyboard.add_hotkey('alt+shift+b', self.on_subject_and_predicate_screenshot)

        self.last_image_id = None
        self.last_image_persist_type = Enum.ImagePersistType.No_Persist

        # keyboard.add_hotkey('alt+shift+a', self.on_passive_enter)
        keyboard.add_hotkey('alt+shift+1', self.on_1_enter)
        keyboard.add_hotkey('alt+shift+2', self.on_2_enter)
        keyboard.add_hotkey('alt+shift+3', self.on_3_enter)
        keyboard.add_hotkey('alt+shift+4', self.on_4_enter)
        keyboard.add_hotkey('alt+shift+5', self.on_5_enter)
        keyboard.add_hotkey('alt+shift+6', self.on_6_enter)
        keyboard.add_hotkey('alt+shift+7', self.on_7_enter)

    def on_menu_command(self, command):
        self.view.mediator.controller.on_menu_command(command)

    def update(self):
        model = self.view.mediator.model
        term_to_enter = model.Services['standard']['term_to_enter']

        self.term_displayer.display_term(term_to_enter)

        # Persist
        if model.Services['standard']['persist']:
            if model.Services['standard']['persist_image_id']:
                persist_image_id = model.Services['standard']['persist_image_id']
                if self.last_image_persist_type == Enum.ImagePersistType.Subject_Image_Persist:
                    term_to_enter['subject_image'] = persist_image_id
                elif self.last_image_persist_type == Enum.ImagePersistType.Predicate_Image_Persist:
                    term_to_enter['predicate_image'] = persist_image_id
                elif self.last_image_persist_type == Enum.ImagePersistType.Subject_And_Predicate_Image_Persist:
                    term_to_enter['predicate_image'] = persist_image_id
                    term_to_enter['subject_image'] = persist_image_id

    def on_subject_paste(self):
        model = self.view.mediator.model
        term_to_enter = model.Services['standard']['term_to_enter']

        value = pyperclip.paste()

        if value:
            term_to_enter['subject_text'] = value
            self.view.update()
            # pyperclip.copy('')
        else:
            self.on_menu_command(Enum.StandardCommand.Set_Subject_Text)

    def on_predicate_paste(self):
        model = self.view.mediator.model
        term_to_enter = model.Services['standard']['term_to_enter']

        value = pyperclip.paste()

        if value:
            term_to_enter['predicate_text'] = value
            self.view.update()
            # pyperclip.copy('')
        else:
            self.on_menu_command(Enum.StandardCommand.Set_Predicate_Text)

    def on_context_paste(self):
        model = self.view.mediator.model
        term_to_enter = model.Services['standard']['term_to_enter']

        value = pyperclip.paste()

        if value:
            term_to_enter['context_text'] = value
            self.view.update()
            # pyperclip.copy('')
        else:
            self.on_menu_command(Enum.StandardCommand.Set_Context_Text)

    def on_subject_and_predicate_paste(self):
        model = self.view.mediator.model
        term_to_enter = model.Services['standard']['term_to_enter']

        value = pyperclip.paste()

        if value:
            term_to_enter['subject_text'] = value
            term_to_enter['predicate_text'] = value
            self.view.update()

    def on_subject_screenshot(self):
        self.on_menu_command(Enum.StandardCommand.Set_Subject_Image)

        # Persist
        self.last_image_persist_type = Enum.ImagePersistType.Subject_Image_Persist

    def on_predicate_screenshot(self):
        self.on_menu_command(Enum.StandardCommand.Set_Predicate_Image)

        # Persist
        self.last_image_persist_type = Enum.ImagePersistType.Predicate_Image_Persist

    def on_subject_and_predicate_screenshot(self):
        self.on_menu_command(Enum.HiddenCommand.Set_Subject_And_Predicate_Image)

        # Persist
        self.last_image_persist_type = Enum.ImagePersistType.Subject_And_Predicate_Image_Persist

    def on_passive_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        term_to_enter['passive'] = True
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = [0, 117, 330, 1777, 6220]
        controller.update()

    def on_1_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = Enum.Schedule.HalfReinforced.value.copy()
        controller.update()

    def on_2_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = Enum.Schedule.Standard.value.copy()
        controller.update()

    def on_3_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = Enum.Schedule.HalfStandard.value.copy()
        controller.update()

    def on_4_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = Enum.Schedule.ReinforcedLongest.value.copy()
        controller.update()

    def on_5_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = Enum.Schedule.Longest.value.copy()
        controller.update()

    def on_6_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = Enum.Schedule.Formula.value.copy()
        controller.update()

    def on_7_enter(self):
        model = self.view.mediator.model
        controller = self.view.mediator.controller

        term_to_enter = model.Services['standard']['term_to_enter']
        self.on_menu_command(Enum.StandardCommand.Enter)
        term_to_enter['schedule'] = Enum.Schedule.Reminder.value.copy()
        controller.update()


class Standard:
    PracticeWidget = PracticeWidget
    HarvestWidget = HarvestWidget


