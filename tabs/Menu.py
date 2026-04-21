import tkinter as tk
from tkinter import ttk
import datetime
import pprint
import math

from utils import Enum


class Menu:
    def __init__(self, view):
        self.view = view
        self.master = view.root

        self.root = ttk.Frame(master=self.master)

        # Define main entry
        self.main_entry_text_variable = tk.StringVar()
        self.main_entry = tk.Entry(self.root, textvariable=self.main_entry_text_variable)
        self.main_entry.pack(expand=False, fill=tk.X, side=tk.TOP)
        self.main_entry.focus()
        self.main_entry.bind('<Return>', self.on_main_entry_enter)

        # Define message
        self.main_message = ttk.Label(self.root)
        self.main_message.pack(expand=True, anchor=tk.NW)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.MenuCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

    def update(self):
        model = self.view.mediator.model

        # model.practice_set, find nearest term
        datetime_now = datetime.datetime.now()

        lowest_difference = None
        schedules = []

        if model.practice_set.terms:
            lowest_date = min([datetime.datetime.fromisoformat(term['deadline']) for term in model.practice_set])
            lowest_difference = lowest_date - datetime_now

            schedules = set(tuple(term['schedule']) for term in model.practice_set)

        lowest_difference_2 = None
        # schedules_2 = []

        if model.practice_set.terms:
            terms = [datetime.datetime.fromisoformat(term['deadline']) for term in model.practice_set if term['index'] > 0]
            if terms:
                lowest_date_2 = min(terms)
                lowest_difference_2 = lowest_date_2 - datetime_now

            # schedules_2 = set(tuple(term['schedule']) for term in model.practice_set)

        # Update message
        # + f"\nidentifier_count: {model.Application['identifier_count']}" \
        # + f"\ncurrent_directory: {model.Application['current_directory']}" \

        message = f"now: {datetime.datetime.now().isoformat()}" \
                  + f"\nnumber of sets: {len(model.get_set_files())}" \
                  + f"\ncompletion_count: {model.Application['completion_count']}" \
                  + f"\n" \
                  + f"\nlen(priority)/len(practice_set): {len(model.practice_set.categorize()['priority'])}/{len(model.practice_set)}" \
                  + f"\nlowest index: {min([term['index'] for term in model.practice_set] + [math.inf])}" \
                  + f"\nnext term in: {lowest_difference}" \
                  + f"\nnext non-zero term in: {lowest_difference_2}" \
                  + f"\nschedules used: {schedules}" \
                  + f"\n\n{pprint.pformat(model.settings)}" \
                  # + f"\n\n{[attr for attr in dir(Enum.Preset) if not attr.startswith('__')]}" \
                  # + f"\n\n{[attr for attr in dir(Enum.Schedule) if not attr.startswith('__')]}"

        self.main_message.configure(text=message)

    def on_menu_command(self, command):
        self.view.mediator.controller.on_menu_command(command)

    def on_main_entry_enter(self, event):
        self.view.mediator.controller.on_menu_command(self.main_entry_text_variable.get())
        self.main_entry_text_variable.set('')
