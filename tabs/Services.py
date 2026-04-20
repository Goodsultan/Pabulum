import tkinter as tk
from tkinter import ttk

from utils import Enum


class Services:
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

        # Define notebook
        self.notebook = ttk.Notebook(self.root)
        self.tabs = {}
        self.current_tab_name = None

        for service in Enum.Service:
            service_object = service.value.HarvestWidget(self.view)

            self.tabs[service.name] = service_object

            self.notebook.add(
                service_object.root,
                text=f'{len(self.tabs)}. {service.name}'
            )

        self.notebook.pack(expand=True, fill=tk.BOTH, anchor=tk.CENTER)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        self.commands = []

    def update(self):
        model = self.view.mediator.model

        for tab in self.tabs.values():
            tab.update()

    def on_menu_command(self, command):
        self.view.mediator.controller.on_menu_command(command)

    def on_main_entry_enter(self, event):
        self.view.mediator.controller.on_menu_command(self.main_entry_text_variable.get())
        self.main_entry_text_variable.set('')

    def on_tab_changed(self, event):
        selected_tab_index = self.notebook.index(self.notebook.select())
        selected_tab = tuple(self.tabs.values())[selected_tab_index]

        # is_active_tab property
        for tab in self.tabs.values():
            if hasattr(tab, 'is_active_tab'):
                tab.is_active_tab = False
        if hasattr(selected_tab, 'is_active_tab'):
            selected_tab.is_active_tab = True

        self.current_tab_name = tuple(self.tabs.keys())[selected_tab_index]

        self.menu = selected_tab.menu
        self.commands = selected_tab.commands

        self.view.on_tab_changed(None)

