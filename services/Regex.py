import tkinter as tk
from tkinter import ttk
import copy

from utils import Enum


class HarvestWidget:
    def __init__(self, view):
        self.view = view
        self.master = view.root

        self.root = ttk.Frame(master=self.master)

        # Make sure data exists
        model = self.view.mediator.model
        if 'regex' not in model.Services:
            model.Services['regex'] = copy.deepcopy(Enum.Model.Services.value['regex'])

        # Define message
        self.main_message = ttk.Label(self.root)
        self.main_message.pack(expand=False, anchor=tk.N, fill=tk.X)

        # Define text
        self.text = tk.Text(self.root)
        self.text.pack(expand=True, fill=tk.BOTH)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.RegexCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

    def on_menu_command(self, command):
        model = self.view.mediator.model

        model.Services['regex']['text'] = self.text.get("1.0", 'end-1c')

        self.view.mediator.controller.on_menu_command(command)

        match command:
            case Enum.RegexCommand.Reset:
                self.text.delete('1.0', tk.END)

    def update(self):
        model = self.view.mediator.model
        text = self.text.get("1.0", 'end-1c')
        model.Services['regex']['text'] = text

        # Update message
        message = f"reverse: {model.Services['regex']['reverse']}"

        self.main_message.configure(text=message)


class Regex:
    HarvestWidget = HarvestWidget
