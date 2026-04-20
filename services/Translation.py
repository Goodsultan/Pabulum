import tkinter as tk
from tkinter import ttk
import copy
import string
import re
import math

from utils import Enum


class HarvestWidget:
    def __init__(self, view):
        self.view = view
        self.master = view.root

        self.root = ttk.Frame(master=self.master)

        # Make sure data exists
        model = self.view.mediator.model
        if 'translation' not in model.Services:
            model.Services['translation'] = copy.deepcopy(Enum.Model.Services.value['translation'])

        # Define message
        self.main_message = ttk.Label(self.root)
        self.main_message.pack(expand=False, anchor=tk.N, fill=tk.X)

        # Define text
        self.translation_text = tk.Text(self.root)
        self.translation_text.pack(expand=True, fill=tk.BOTH)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.TranslationCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

    def on_menu_command(self, command):
        model = self.view.mediator.model

        model.Services['translation']['translation_text'] = self.translation_text.get("1.0", 'end-1c')

        self.view.mediator.controller.on_menu_command(command)

        match command:
            case Enum.TranslationCommand.Translate_Text | Enum.TranslationCommand.Reset_All:
                self.translation_text.delete('1.0', tk.END)

    def update(self):
        model = self.view.mediator.model
        translation_text = self.translation_text.get("1.0", 'end-1c')

        # Update message
        message = f"language: {model.Services['translation']['language']}" \
                  + f"\nlen(word_frequency): {len(model.Services['translation']['word_frequency'])}" \
                  + f"\ncharacter count: {len(translation_text)}" \
                  + f"\nword count: {len(translation_text.split(' '))}" \

        self.main_message.configure(text=message)


class Translation:
    HarvestWidget = HarvestWidget

    @staticmethod
    def remove_punctuation(text: str) -> str:
        punctuation = [
            ',', '!', '?', '.', '„', '”', '"', '(', ')', ':', '»', '«', ';', '、', '。',
            '【', '】', '「', '」', '〝', '〟', '！', '？'
        ]
        translator = str.maketrans('', '', string.punctuation + ''.join(punctuation))
        clean_text = text.translate(translator)

        return clean_text

    @staticmethod
    def process_japanese(input_string: str) -> list:
        input_string = Translation.remove_punctuation(input_string)

        pattern = r'([^\x00-\x7F]+)([a-zA-Z]+)'

        matches = re.findall(pattern, input_string)

        return [(pair[0], pair[1]) for pair in matches]

