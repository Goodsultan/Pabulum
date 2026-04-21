import typing
import random
import datetime
import json
import pprint

from utils import Enum
from utils.SimpleDialog import SimpleDialog


class Set:
    __slots__ = (
        'terms',
    )

    @staticmethod
    def reenter(term, attribute=None, message=None):
        if attribute is None:
            attribute = SimpleDialog('Attribute', f'Enter term attribute.\n\n{pprint.pformat(term)}')

        if attribute in tuple(Enum.TermAttribute):
            current_value = term.get(attribute, None)

            if type(current_value) == int:
                new_value = SimpleDialog(attribute, message, input_class=int, initial_value=current_value)
            elif type(current_value) == float:
                new_value = SimpleDialog(attribute, message, input_class=float, initial_value=current_value)
            elif type(current_value) == list:
                new_value = SimpleDialog(attribute, message, input_class=str, initial_value=current_value)
            else:
                new_value = SimpleDialog(attribute, message, input_class=str, initial_value=current_value)

            if attribute == Enum.TermAttribute.Schedule.value:
                try:
                    new_value = json.loads(new_value)

                    # check if list is entered correctly
                    if type(new_value) is not list or len(new_value) <= 0:
                        raise ValueError

                    for value in new_value:
                        if type(value) is not int or value < 0:
                            raise ValueError
                except:
                    new_value = [0]

            # Codeword for None
            if new_value == '':
                new_value = None

            term[attribute] = new_value

    def __init__(self, terms: typing.Dict[str, dict]):
        self.terms = terms

    def __len__(self):
        return len(self.terms)

    def __getitem__(self, item):
        return self.terms[item]

    def __iter__(self):
        return iter(self.terms.values())

    def clear(self):
        self.terms.clear()

    def update(self, other):
        if type(other) == dict:
            self.terms.update(other)
        else:
            self.terms.update(other.terms)

    def categorize(self) -> dict:
        # Priority: current > lowest-index > highest-index > zero-index
        datetime_now = datetime.datetime.now()

        practice = list({
            identifier: term
            for identifier, term in self.terms.items()
            if datetime_now > datetime.datetime.fromisoformat(term['deadline'])
        }.items())

        priority = sorted(practice, key=lambda x: (x[1]['index'] == 0, x[1]['index']))

        above_zero = [
            (identifier, term)
            for identifier, term in practice
            if term['index'] > 0
        ]

        return {
            'practice': practice,
            'priority': priority,
            'above_zero': above_zero,
        }

    def schedule(self, term: dict, index=None, delta=1):
        datetime_now = datetime.datetime.now()

        # Get index
        if index is None:
            term['index'] += delta
            index = term['index']
        else:
            # # Trial
            # if index == 0:
            #     if 'on_trial' in term and term['on_trial']:
            #         i = Enum.trials_list.index(term['schedule'])
            #
            #         if i != len(Enum.trials_list) - 1:
            #             i += 1
            #
            #         term['schedule'] = Enum.trials_list[i].copy()

            term['index'] = index

        if index >= len(term['schedule']):
            del self.terms[term['identifier']]

            return Enum.Scheduling.Completed

        addend = datetime.timedelta(seconds=term['schedule'][index])
        new_deadline = datetime_now + addend

        # If more than one day, adjust so that it's due at the very beginning of the day
        if addend > datetime.timedelta(hours=23, minutes=59):
            new_deadline = new_deadline.replace(hour=0, minute=0, second=0, microsecond=0)

        term['deadline'] = new_deadline.isoformat()

        return Enum.Scheduling.Scheduled

    def index(self, index):
        if index in range(len(self)):
            return self[tuple(self.terms)[index]]
        else:
            return None

    def items(self):
        return self.terms.items()

    def randomize_order(self):
        # shuffled_keys = list(self.terms.keys())
        # random.shuffle(shuffled_keys)
        # values = list(self.terms.values())
        # self.terms = dict(zip(shuffled_keys, values))
        #
        # datetime_now = datetime.datetime.now()
        #
        # addends = [10, 20, 30, 40, 50, 60, 70]

        # for identifier, term in self.terms.items():
        #     term['identifier'] = identifier
        #
        #     if term.get('index', -1) == 0:
        #         addend = datetime.timedelta(seconds=random.choice(addends))
        #         new_deadline = datetime_now - addend
        #         term['deadline'] = new_deadline.isoformat()

        shuffled_terms = list(self.terms.items())
        random.shuffle(shuffled_terms)
        self.terms = dict(shuffled_terms)

