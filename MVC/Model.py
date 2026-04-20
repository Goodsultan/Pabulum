import json
import copy
import datetime
import os
import uuid

from utils import Enum
from utils.Set import Set


class Model:
    __slots__ = (
        'Application',
        'Services',
        'PracticeStash',

        'harvest_set',
        'practice_set',
        'settings',
    )

    def __init__(self):
        # Load data
        for model in Enum.Model:
            filename = f'{model.name}.txt'

            try:
                with open(filename, mode='r') as file:
                    data = json.load(file)

            except FileNotFoundError:
                with open(filename, mode='w') as file:
                    data = copy.deepcopy(model.value)
                    json.dump(data, file)

            setattr(self, model.name, data)

        # Quick-access attributes
        self.harvest_set: Set = Set(self.Application['harvest_set'])
        self.practice_set: Set = Set(self.Application['practice_set'])
        self.settings = self.Application['settings']

    def dump(self):
        for model in Enum.Model:
            filename = f'{model.name}.txt'

            with open(filename, mode='w') as file:
                json.dump(getattr(self, model.name), file)

    def new_identifier(self) -> str:
        self.Application['identifier_count'] += 1

        # To avoid conflict with JSON
        return f"{self.Application['identifier_count']}"

    def harvest_enter(self, term: dict):
        # identifier = self.new_identifier()
        identifier = self.new_identifier() + "-" + str(uuid.uuid4())

        term.update({
            'identifier': identifier,
            'deadline': datetime.datetime.now().isoformat(),
            'index': 0
        })

        self.harvest_set.update({
            identifier: term
        })

        self.Application['harvest_set_index'] = len(self.harvest_set) - 1

    @staticmethod
    def get_image_files():
        image_files = tuple(
            f for f in os.listdir(Enum.IMAGES_DIRECTORY)
            if os.path.isfile(os.path.join(Enum.IMAGES_DIRECTORY, f))
        )

        return sorted(image_files)

    @staticmethod
    def get_set_files():
        set_files = tuple(
            f for f in os.listdir(Enum.SETS_DIRECTORY)
            if os.path.isfile(os.path.join(Enum.SETS_DIRECTORY, f))
        )

        return sorted(set_files)

    def get_image_requirements(self) -> dict:
        return {
            'min_height': self.settings[Enum.Settings.Minimum_Image_Height],
            'max_height': self.settings[Enum.Settings.Maximum_Image_Height],

            'max_width': self.settings[Enum.Settings.Maximum_Image_Width],
        }

    @staticmethod
    def normalize_text(text: str) -> str:
        # Split the text into lines
        lines = text.split('\n')

        # Strip leading and trailing whitespaces from each line
        stripped_lines = [line.rstrip() for line in lines]

        # Join the stripped lines back into a single string
        result_text = '\n'.join(stripped_lines)

        return result_text

