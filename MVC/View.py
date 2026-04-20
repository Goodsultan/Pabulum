import tkinter as tk
from tkinter import ttk
import enum
import keyboard
# from tkinter import tix

from utils import Enum
from tabs.Menu import Menu
from tabs.Harvest import Harvest
from tabs.Services import Services
from tabs.Practice import Practice


class View:
    class Tab(enum.Enum):
        Menu = Menu
        Harvest = Harvest
        Services = Services
        Practice = Practice

    def __init__(self, mediator):
        self.mediator = mediator

        # self.root = tix.Tk()
        self.root = tk.Tk()

        # Root configuration
        self.root.title('PV2')

        self.root.minsize(
            Enum.WINDOW_WIDTH,
            Enum.WINDOW_HEIGHT
        )
        self.root.geometry('%dx%d+%d+%d' % (Enum.WINDOW_WIDTH, Enum.WINDOW_HEIGHT, 0, 0))
        # self.root.pack_propagate(False)
        # self.root.attributes('-topmost', True)

        # Create notebook and its tabs
        self.notebook = ttk.Notebook(self.root)
        self.tabs = {}
        self.current_tab_name = None

        for tab in View.Tab:
            tab_object = tab.value(self)
            self.tabs[tab.name] = tab_object

            self.notebook.add(
                tab_object.root,
                text=f'{len(self.tabs)}. {tab.name}'
            )

        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Handle when user changes of tabs
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        self.on_tab_changed(None)

        # Check practice set categorization
        interval = self.mediator.model.settings[Enum.Settings.Categorization_Check_Interval]
        self.root.after(interval, self.check_categorization)

        # Shortcut
        keyboard.add_hotkey('alt+u', self.update)

    def update(self):
        for tab in self.tabs.values():
            tab.update()

    def check_categorization(self):
        self.mediator.controller.check_categorization()

    def on_tab_changed(self, event):
        selected_tab_index = self.notebook.index(self.notebook.select())
        selected_tab = tuple(self.tabs.values())[selected_tab_index]
        self.current_tab_name = tuple(self.tabs.keys())[selected_tab_index]

        self.root.configure(menu=selected_tab.menu)

        selected_tab.main_entry.focus()

