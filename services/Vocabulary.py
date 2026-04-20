import tkinter as tk
from tkinter import ttk
import copy
import keyboard
import pyperclip
import string
import re

from utils import Enum


class HarvestWidget:
    def __init__(self, view):
        self.is_active_tab = False

        self.view = view
        self.master = view.root

        self.root = ttk.Frame(master=self.master)

        # Make sure data exists
        model = self.view.mediator.model
        # if 'translation' not in model.Services:
        #     model.Services['translation'] = copy.deepcopy(Enum.Model.Services.value['translation'])

        # Define message
        self.main_message = ttk.Label(self.root)
        self.main_message.pack(expand=False, anchor=tk.N, fill=tk.X)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.VocabularyCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

        # Hotkeys
        keyboard.add_hotkey('ctrl+v', self.on_word_definition_paste)
        keyboard.add_hotkey('alt+a', self.on_word_add)

    def on_menu_command(self, command):
        model = self.view.mediator.model

        self.view.mediator.controller.on_menu_command(command)

    def update(self):
        model = self.view.mediator.model

        if model.Services['vocabulary']['vocabulary_list']:
            current_word = model.Services['vocabulary']['vocabulary_list'][0]
            model.Services['vocabulary']['current_word'] = current_word

            if self.is_active_tab:
                pyperclip.copy(current_word + model.Services['vocabulary']['extra_suffix'])
        else:
            model.Services['vocabulary']['current_word'] = None

        # Update message
        message = f"len(vocabulary_list): {len(model.Services['vocabulary']['vocabulary_list'])}" \
                  + f"\nvocabulary_list[:3]: {model.Services['vocabulary']['vocabulary_list'][:3]}" \
                  + f"\ncurrent_word: {model.Services['vocabulary']['current_word']}" \
                  + f"\nextra_suffix: {model.Services['vocabulary']['extra_suffix']}" \
                  + f"\nreversed: {model.Services['vocabulary']['reversed']}" \

        self.main_message.configure(text=message)

    def on_word_definition_paste(self):
        if not self.is_active_tab:
            return

        model = self.view.mediator.model

        current_word = model.Services['vocabulary']['current_word']

        if not current_word:
            return

        subject_text = model.Services['vocabulary']['current_word']
        predicate_text = pyperclip.paste()

        if predicate_text == subject_text + model.Services['vocabulary']['extra_suffix']:
            return

        if predicate_text == subject_text:
            return

        # Automatically replace word with _, if example is provided
        # predicate_text = predicate_text.replace(current_word, "_")

        # Use standard service

        if model.Services['vocabulary']['reversed']:
            subject_text, predicate_text = predicate_text, subject_text

        term_to_enter = model.Services['standard']['term_to_enter']
        term_to_enter['subject_text'] = subject_text
        # Automatically replace word with _ if there's an example
        # print(predicate_text, subject_text, current_word, predicate_text.replace(current_word, "_"))
        replaced_predicate_text = predicate_text.replace(subject_text, "_").replace(subject_text.lower(), "_").replace(subject_text.upper(), "_").replace(subject_text.capitalize(), "_")

        # # for ing ed
        # if len(subject_text) > 5:
        #     subject_text_2 = subject_text[:-1] + " "
        #     replaced_predicate_text = replaced_predicate_text.replace(subject_text_2, "_ ").replace(subject_text_2.lower(), "_ ").replace(subject_text_2.upper(), "_ ").replace(subject_text_2.capitalize(), "_ ")

        term_to_enter['predicate_text'] = replaced_predicate_text
        self.view.mediator.controller.on_menu_command(Enum.StandardCommand.Enter)
        self.view.mediator.controller.on_menu_command(Enum.VocabularyCommand.Discard_Word)

    def on_word_add(self):
        word_to_add = pyperclip.paste()

        model = self.view.mediator.model
        model.Services['vocabulary']['vocabulary_list'].insert(0, word_to_add)

        self.update()


class Vocabulary:
    HarvestWidget = HarvestWidget

    skip_characters = list(string.punctuation) + [' ', '\n', '\t']

    @staticmethod
    def point_of_difference(string_1, string_2):
        i = 0

        for letter_1, letter_2 in zip(string_1, string_2):
            if letter_1 != letter_2:
                return i

            i += 1

        return None

    @staticmethod
    def simple_redact(word: str) -> str:
        new_word = ''
        symbol = '-'

        for i, character in enumerate(word):
            if i > 1 and i != len(word) - 1:
                if (i + 1) % 2 != 0:
                    if character not in Vocabulary.skip_characters:
                        if i - 1 >= 0 and word[i - 1] not in Vocabulary.skip_characters:
                            if i + 1 < len(word) and word[i + 1] not in Vocabulary.skip_characters:
                                if not (word[i - 1].islower() and character.isupper() and word[i + 1].islower()):
                                    character = symbol

            new_word += character

        return new_word

    @staticmethod
    def stricter_redact(word: str) -> str:
        new_word = ''
        symbol = '-'

        for i, character in enumerate(word):
            if i > 1 and i != len(word) - 1:
                # if (i + 1) % 2 != 0:
                if character not in Vocabulary.skip_characters:
                    if i - 1 >= 0 and word[i - 1] not in Vocabulary.skip_characters:
                        if i + 1 < len(word) and word[i + 1] not in Vocabulary.skip_characters:
                            if not (word[i - 1].islower() and character.isupper() and word[i + 1].islower()):
                                character = symbol

            new_word += character

        return new_word

    @staticmethod
    def redact_and_skip_first_two_letters(word: str) -> str:
        new_word = ''
        symbol = '-'

        for i, character in enumerate(word):
            if i >= 2:
                if character not in Vocabulary.skip_characters:
                    if not (character.isspace() or character.isnumeric()):
                        character = symbol

            new_word += character

        return new_word

    @staticmethod
    def complete_redact(word: str) -> str:
        return '-' * len(word)

    @staticmethod
    def __replace_match(match: re.Match):
        content = match.group()

        if '~1' in content:
            return Vocabulary.stricter_redact(content[2:-2])
        elif '~2' in content:
            return Vocabulary.redact_and_skip_first_two_letters(content[2:-2])
        elif '~3' in content:
            return Vocabulary.complete_redact(content[2:-2])
        else:
            return Vocabulary.simple_redact(content[1:-1])

    @staticmethod
    def redact_by_special_symbol(line: str, special_symbol='~') -> str:
        # pattern = fr'{special_symbol}.*?{special_symbol}'
        # ~(2|1).*?~(2|1)
        # ~(2|1|).*?~(2|1|)
        pattern = fr'{special_symbol}(2|1|).*?{special_symbol}(2|1|)'

        return re.sub(pattern, Vocabulary.__replace_match, line)


# # print(Vocabulary.redact_line_by_special_symbol('Hello ~ThisIsATest~ please ~StandBy~ and ~SeeWhatHappens~'))
# print(Vocabulary.simple_redact('Hello ~1This.Is.A.Test~1 please ~2StandBy~2 and ~SeeWhatHappens~....'))
# print(Vocabulary.stricter_redact('Hello ~1This.Is.A.Test~1 please ~2StandBy~2 and ~SeeWhatHappens~....'))
#
# # print(Vocabulary.complete_redact('abcd'))