import tkinter as tk
from tkinter import ttk
import random
import keyboard

from utils import Enum


class Practice:
    def __init__(self, view):
        self.view = view
        self.master = view.root

        # Configuration
        self.sound_terms = False

        self.root = ttk.Frame(master=self.master)

        self.current_term = None

        self.main_practice_widget = None

        # Define main entry
        self.main_entry_text_variable = tk.StringVar()
        self.main_entry = tk.Entry(self.root, textvariable=self.main_entry_text_variable)
        self.main_entry.pack(expand=False, fill=tk.X, side=tk.TOP)
        self.main_entry.focus()
        self.main_entry.bind('<Return>', self.on_main_entry_enter)

        self.practice_widgets = []

        # Define stack
        self.stack_frame = ttk.Frame(master=self.root)
        self.stack_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.PracticeCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

        keyboard.add_hotkey('alt+return', lambda: self.on_menu_command(Enum.PracticeCommand.Return))

    def update(self):
        model = self.view.mediator.model

        # Update stack
        stack_frame_children = self.stack_frame.winfo_children()
        for child in stack_frame_children:
            child.pack_forget()
            child.destroy()

        categorization = model.practice_set.categorize()
        practice_stack_length = model.settings[Enum.Settings.Practice_Stack_Length]

        # Focus main entry before focusing to a term
        self.main_entry.focus()
        self.main_entry.focus_set()

        # Display practice widgets
        self.practice_widgets.clear()

        self.main_practice_widget = None

        priority_list = categorization['priority']
        if model.settings[Enum.Settings.Randomize_Practice]:
            priority_list = categorization['above_zero']

            if not len(priority_list):
                priority_list = categorization['practice']

            random.shuffle(priority_list)

            # Schedule size matters
            # ...

            # Don't randomize schedule
            if True:
                priority_list.sort(key=lambda x: x[1]['index'], reverse=True)

            # Bigger schedule rights
            if True:
                priority_list.sort(key=lambda x: len(x[1]['schedule']), reverse=True)

            # 500, 10,000
        else:
            # Order them by ID for reviewing sets
            pass

            #priority_list.sort(key=lambda x: int(x[0]))

        # Review mode
        if model.Services['standard'].get('review_mode', False):
            priority_list.sort(key=lambda x: len(x[1]['schedule']))

        #print(len(priority_list), priority_list[0][0], type(priority_list[0][0]))

        focused = self.view.current_tab_name == self.view.Tab.Practice.name

        for index, term_tuple in enumerate(priority_list[:practice_stack_length]):
            term_identifier, term = term_tuple

            frame = tk.Frame(self.stack_frame, borderwidth=1, relief=tk.SOLID)
            frame.pack(expand=False, fill=tk.X, side=tk.TOP)

            if index == 0:
                practice_widget = Enum.Service[term['service']].value.PracticeWidget(self.view, frame, term, is_main=True, is_focused=focused)
            else:
                practice_widget = Enum.Service[term['service']].value.PracticeWidget(self.view, frame, term, is_focused=focused)

            # store
            self.practice_widgets.append(practice_widget)

            if index == 0:
                practice_widget.focus()
                self.current_term = term
                model.Application['current_practice_term_identifier'] = term_identifier

                self.main_practice_widget = practice_widget

                # if self.sound_terms:
                #     if not self.main_practice_widget.is_sounding:
                #         self.main_practice_widget.threaded_sound()

    def on_menu_command(self, command):
        self.view.mediator.controller.on_menu_command(command)

    def on_main_entry_enter(self, event):
        self.view.mediator.controller.on_menu_command(self.main_entry_text_variable.get())
        self.main_entry_text_variable.set('')
