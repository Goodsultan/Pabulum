import tkinter as tk
from tkinter import ttk
# from tkinter.tix import *

from utils import Enum
from utils.TermDisplayer import TermDisplayer


class Harvest:
    def __init__(self, view):
        self.view = view
        self.master = view.root

        self.root = ttk.Frame(master=self.master)

        self.current_term = None

        # Define two main frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        self.prioritization_frame = tk.Frame(self.root)
        self.prioritization_frame.pack(expand=False, fill=tk.Y, side=tk.RIGHT)

        # tool_tip = Balloon(self.prioritization_frame)

        # For displaying term given harvest_set_index
        self.term_displayer = TermDisplayer(self.view, self.main_frame)

        # Define main entry
        self.main_entry_text_variable = tk.StringVar()
        self.main_entry = tk.Entry(self.main_frame, textvariable=self.main_entry_text_variable)
        self.main_entry.pack(expand=False, fill=tk.X, side=tk.TOP)
        self.main_entry.focus()
        self.main_entry.bind('<Return>', self.on_main_entry_enter)

        # Prioritization Frame
        button = tk.Button(self.prioritization_frame, text='Delete', command=lambda: self.on_menu_command(Enum.HarvestCommand.Delete))
        button.pack(expand=False, fill=tk.X, side=tk.TOP)

        schedule_names = ['HalfReinforced', 'Standard', 'HalfStandard', 'LongReviewStandard', 'ShortReviewStandard', 'ReinforcedLongest', 'Longest', 'Formula', 'ShortLongest1', 'ShortLongest2']

        for name in schedule_names:
            display_name = f"{name}:\n{Enum.Schedule[name].value.copy()}"

            button = tk.Button(self.prioritization_frame, text=display_name,
                               command=lambda schedule_name=name: self.change_current_term_schedule(schedule_name=schedule_name))
            # tool_tip.bind_widget(button, balloonmsg=f"{Enum.Schedule[name].value}")
            button.pack(expand=False, fill=tk.X, side=tk.TOP)

        # Define message
        self.main_message = ttk.Label(
            self.main_frame,
        )
        self.main_message.pack(expand=False, anchor=tk.NW, side=tk.TOP)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.HarvestCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

    def change_current_term_schedule(self, schedule_name, go_forward=True):
        if self.current_term:
            self.current_term['schedule'] = Enum.Schedule[schedule_name].value.copy()

        if go_forward:
            self.on_menu_command(Enum.HarvestCommand.Forward)
            self.update()

    def update(self):
        model = self.view.mediator.model

        # Display term given harvest_set_index
        harvest_set_index = model.Application['harvest_set_index']
        term = model.harvest_set.index(harvest_set_index)

        if term:
            self.term_displayer.display_term(term)
            self.current_term = term
        else:
            self.term_displayer.clear()
            model.Application['harvest_set_index'] = len(model.harvest_set) - 1
            self.current_term = None

        # Update message
        message = f"title: {model.Application['harvest_set_title']}" \
                  + f"\nharvest_set_index/len(harvest_set): {model.Application['harvest_set_index'] + 1}/{len(model.harvest_set)}"
        self.main_message.configure(text=message)

    def on_menu_command(self, command):
        self.view.mediator.controller.on_menu_command(command)

    def on_main_entry_enter(self, event):
        self.view.mediator.controller.on_menu_command(self.main_entry_text_variable.get())
        self.main_entry_text_variable.set('')
