import enum
import os

from services.Standard import Standard
from services.Images import Images
from services.Translation import Translation
from services.Vocabulary import Vocabulary
from services.Regex import Regex

GOLDEN_RATIO = (1 + 5 ** 0.5) / 2

# Colors
LIGHT_GRAY = '#D3D3D3'
CRIMSON = '#DC143C'

# Directories
# IMAGES_DIRECTORY = fr"{os.getcwd()}\images"
# SETS_DIRECTORY = fr"{os.getcwd()}\sets" #os.path.join(os.getcwd(), "sets")
# SOUNDS_DIRECTORY = fr"{os.getcwd()}\sounds"

# COLLECTIONS_DIRECTORY = fr"{os.getcwd()}\collections"

# MAX_NUMBER_OF_AUXILIARY_FOLDERS = 1000
#
# # To add more images and sets folder into the same directory
# auxiliary_images_directories = [
#     fr"{os.getcwd()}\images_{i}"
#     for i in range(1, MAX_NUMBER_OF_AUXILIARY_FOLDERS+1)
# ] # + [
# #     fr"{os.getcwd()}\images{i}"
# #     for i in range(1, MAX_NUMBER_OF_AUXILIARY_FOLDERS+1)
# # ]
#
# auxiliary_sets_directories = [
#     fr"{os.getcwd()}\sets_{i}"
#     for i in range(1, MAX_NUMBER_OF_AUXILIARY_FOLDERS+1)
# ] # + [
# #     fr"{os.getcwd()}\sets{i}"
# #     for i in range(1, MAX_NUMBER_OF_AUXILIARY_FOLDERS+1)
# # ]

WINDOW_WIDTH = 300
WINDOW_HEIGHT = int(WINDOW_WIDTH * (1 / GOLDEN_RATIO))


class Scheduling(enum.StrEnum):
    Scheduled = enum.auto()
    Completed = enum.auto()
    ScheduleIt = enum.auto()


class Schedule(enum.Enum):
    HalfStandard = [0, 15, 244, 1111]
    Standard = [0, 15, 117, 244, 1111]
    HalfReinforced = [0, 7, 15, 117, 244, 1111]
    Reinforced = [0, 3, 7, 15, 117, 244, 1111]
    DoubleReinforced = [0, 3, 7, 15, 30, 117, 244, 1111]
    TripleReinforced = [0, 3, 7, 15, 30, 45, 60, 117, 200, 244, 500, 700, 1111]

    LongReviewStandard = [0, 15, 1111]
    ShortReviewStandard = [0, 15, 660]

    Long = [0, 15, 300, 1555]
    Longer = [0, 15, 330, 1777]
    Longest = [0, 330, 1777, 6220]
    ShortLongest1 = [0, 330, 6220]
    ShortLongest2 = [0, 330, 1777]
    ReinforcedLongest = [0, 117, 330, 1777, 6220]
    DoubleLongest = [0, 1777, 6220, 6220*2]
    TripleLongest = [0, 330, 1777, 6220, 6220*2]

    Short = [0, 15, 300, 300]

    Twice = [0, 20]
    LightReview = [0, 30]
    LongTwice = [0, 40]
    LongestTwice = [0, 330]
    OneMinute = [0, 60]
    ReinforcedReview = [0, 15, 60]
    StandardReview = [0, 15, 330]

    Once = [0]
    Reviewer = [0, 5, 15]

    # SoundReview = [0, 5, 25, 60*2, 60*10, 60*60, 60*60*2]
    # SoundReview2 = [0, 0, 5, 25, 60*2, 60*10, 60*60]

    # SpacedSoundReview = [0, 0, 25, 244, 1111, 60*60]
    # SpacedSoundReview2 = [0, 0, 25, 244, 1111, 60 * 60, 6220*2]
    # at 5, begin active stage
    # 86400 - a day in seconds
    # PassiveStage = [0, 0, 1, 5, 25, 6220 * 2, 86400 * 3, 86400 * 7]
    # ActiveStage = [0, 7, 15, 117, 244, 1111] #[0, 15, 117, 244, 1111]

    # 4
    # PS = [0, 0, 0, 0, 6220 * 2, 86400 * 3, 86400 * 7]
    # AS = [0, 7, 15, 117, 244, 1111]

    # Formula = [0, 15, 244, 1111]
    # LongFormula = [0, 244, 1111]
    Formula = [0, 20, 330, 1777]
    Reminder = [0, 330, 1777]


# trials_list_1 = [
#     [0, 500],
#     [0, 15, 300, 1555],
#     [0, 15, 117, 244, 1111],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_2 = [
#     [0, 500],
#     [0, 15, 117, 244, 1111],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_3 = [
#     [0, 15, 244, 500],
#     [0, 15, 117, 244, 1111],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_4 = [
#     [0, 15, 244, 500],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_5 = [
#     [0, 500],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_6 = [
#     [0, 15, 117, 244, 1111],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_7 = [
#     [0, 15, 244, 500],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_8 = [
#     [0, 100],
#     [0, 7, 15, 117, 244, 1111]
# ]
#
# trials_list_9 = [
#     [0, 50],
#     [0, 7, 15, 117, 244, 1111]
# ]

trial_list_10 = [
    [0, 5, 15],
    [0, 3, 5, 15]
]

trials_list = trial_list_10


class TermAttribute(enum.StrEnum):
    Identifier = enum.auto()
    Service = enum.auto()
    Schedule = enum.auto()
    Index = enum.auto()
    Deadline = enum.auto()

    Subject_Text = enum.auto()
    Predicate_Text = enum.auto()
    Context_Text = enum.auto()

    Subject_Image = enum.auto()
    Predicate_Image = enum.auto()

    Context_Image = enum.auto()


class Service(enum.Enum):
    Standard = Standard
    Images = Images
    Vocabulary = Vocabulary
    # Regex = Regex
    # Translation = Translation


class Settings(enum.StrEnum):
    Categorization_Check_Interval = enum.auto()
    Practice_Alert = enum.auto()
    Minimum_Practice_Terms_For_Alert = enum.auto()

    Relearn_Index_One = enum.auto(),
    Practice_Stack_Length = enum.auto()

    Maximum_Image_Width = enum.auto()

    Maximum_Image_Height = enum.auto()
    Minimum_Image_Height = enum.auto()

    Blacklisted_Term_Attributes = enum.auto()

    Randomize_Practice = enum.auto()
    Auto_Penalize = enum.auto()

    # Auto_Return = enum.auto()


class Preset(enum.Enum):
    SMALLER_SCREEN = {
        Settings.Maximum_Image_Width: 300,

        Settings.Maximum_Image_Height: 300,
        Settings.Minimum_Image_Height: 170,
    }

    SMALL_SCREEN = {
        Settings.Maximum_Image_Width: 1000,

        Settings.Maximum_Image_Height: 300,
        Settings.Minimum_Image_Height: 170,
    }

    BIG_SCREEN = {
        Settings.Maximum_Image_Width: 1200,

        Settings.Maximum_Image_Height: 1200,
        Settings.Minimum_Image_Height: 400,
    }

    BIGGER_SCREEN = {
        Settings.Maximum_Image_Width: 1600,

        Settings.Maximum_Image_Height: 1200,
        Settings.Minimum_Image_Height: 700,
    }

    # LENIENT = {
    #     Settings.Randomize_Practice: False,
    #     Settings.Auto_Penalize: False
    # }

    # STRICT = {
    #     Settings.Randomize_Practice: True,
    #     Settings.Auto_Penalize: Schedule.Standard.name
    # }


class Model(enum.Enum):
    # "identifier_count": 47471, "completion_count": 99241,

    Application = {
        'current_directory': os.getcwd(),

        'identifier_count': 0,
        'completion_count': 0,

        'harvest_set': {},

        'harvest_set_index': 0,
        'harvest_set_title': 'Untitled',

        'current_practice_term_identifier': None,

        'settings': {
            Settings.Categorization_Check_Interval: 10_000,
            Settings.Practice_Alert: True,
            Settings.Minimum_Practice_Terms_For_Alert: 5,

            Settings.Relearn_Index_One: True,
            Settings.Practice_Stack_Length: 1,

            Settings.Maximum_Image_Width: 1000,

            Settings.Maximum_Image_Height: 300,
            Settings.Minimum_Image_Height: 170,

            Settings.Randomize_Practice: False,

            Settings.Blacklisted_Term_Attributes: [
                TermAttribute.Identifier.value,
                # TermAttribute.Schedule.value,
                TermAttribute.Index.value,
                TermAttribute.Deadline.value,
            ],

            # Settings.Auto_Return: False,
        },

        'practice_set': {},
    }

    Services = {
        'standard': {
            'term_to_enter': {
                'subject_text': None,
                'predicate_text': None,

                'predicate_image': None,
                'subject_image': None,

                'context_text': None,
            },

            'context_text': '',
            # 'highlight_difference': True,
            'default_schedule': Schedule.Longest.value,
            'case_insensitive': True,
            # 'review_mode': False,
            # 'word_association_help': True,

            'persist_subject_image': None,
            'persist_predicate_image': None,
            'persist_subject_and_predicate_image': None,
            'persist_image_id': None,
            'persist': False,

            'practice': {
                'auto_sound_subjects': True,
                'strip_subject_text': True,
                'display_subject_hint': False,
                'strip_displayed_predicate': True,
                'see_subject_and_predicate_difference': True,
                'voice_rate': 220
            }
        },

        'images': {
            'current_index': 0
        },

        'vocabulary': {
            'vocabulary_list': [],
            'current_word': None,
            'extra_suffix': '',
            'reversed': False,
        },

        # 'translation': {
        #     'language': 'japanese',
        #     'word_frequency': {},
        #     'translation_text': '',
        # },
        #
        # 'regex': {
        #     'text': '',
        #     'reverse': False,
        # },
    }

    PracticeStash = {}


class AbstractCommandClass(enum.Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return f"{count + 1}. {name.replace('_', ' ').lower()}"


class MenuCommand(AbstractCommandClass):
    Help = enum.auto()

    # Dump_Data = enum.auto()
    Exit = enum.auto()
    Reset_Completion_Count = enum.auto()
    Set_Font_Size = enum.auto()
    Print_Sets_Randomly = enum.auto()
    Set_Preset = enum.auto()
    Randomize_Practice = enum.auto()
    Load_Practice_Set = enum.auto()
    Save_Practice_Set = enum.auto()
    Pick_Main_Directory = enum.auto()


class HarvestCommand(AbstractCommandClass):
    Help = enum.auto()

    Back = enum.auto()
    Forward = enum.auto()

    Harvest = enum.auto()
    Clear_Set = enum.auto()
    Delete = enum.auto()
    Reenter = enum.auto()

    Practice = enum.auto()
    Practice_Amount_Of_Terms = enum.auto()

    Set_Title = enum.auto()
    Save = enum.auto()
    Load_Set = enum.auto()

    Schedule_All = enum.auto()

    # First = enum.auto()

    Load_All_Sets = enum.auto()

    # Toggle_Trial = enum.auto()

    # Pacify = enum.auto()
    # Reassign_IDs = enum.auto()

    Load_From_Practice_Set = enum.auto()

    Assign_All_Title_As_Context = enum.auto()


class StandardCommand(AbstractCommandClass):
    Help = enum.auto()

    Enter = enum.auto()
    Reset = enum.auto()

    Set_Subject_Text = enum.auto()
    Set_Predicate_Text = enum.auto()
    Set_Context_Text = enum.auto()

    Set_Subject_Image = enum.auto()
    Set_Predicate_Image = enum.auto()

    # Set_Context_Image = enum.auto()
    #
    # Discard_Images = enum.auto()

    Set_Default_Schedule = enum.auto()

    # Redact = enum.auto()

    Toggle_Persist_Image = enum.auto()

    # Invert_All = enum.auto()


class ImagePersistType(enum.StrEnum):
    No_Persist = enum.auto()
    Subject_Image_Persist = enum.auto()
    Predicate_Image_Persist = enum.auto()
    Subject_And_Predicate_Image_Persist = enum.auto()


class ImagesCommand(AbstractCommandClass):
    Help = enum.auto()

    Back = enum.auto()
    Forward = enum.auto()

    Copy = enum.auto()
    Screenshot = enum.auto()
    Delete = enum.auto()
    Replace = enum.auto()
    Fill_Crimson = enum.auto()
    Fill_None = enum.auto()

    # First=enum.auto()


class PracticeCommand(AbstractCommandClass):
    Help = enum.auto()

    Delete = enum.auto()
    Relearn = enum.auto()
    Reenter = enum.auto()
    Toggle_Alert = enum.auto()
    Set_Practice_Stack_Length = enum.auto()
    Clear_Set = enum.auto()
    Penalize = enum.auto()
    # Penalize_Standard = enum.auto()
    # Penalize_Reinforced = enum.auto()
    Schedule_One_Index = enum.auto()
    Copy_Subject = enum.auto()
    Return = enum.auto()
    # Sound_Terms = enum.auto()
    Randomize_Order = enum.auto()

    Toggle_Auto_Sound_Subjects = enum.auto()
    Toggle_Display_Subject_Hint = enum.auto()
    Toggle_See_Subject_And_Predicate_Difference = enum.auto()


class TranslationCommand(AbstractCommandClass):
    Translate_Text = enum.auto()
    # Set_Source = enum.auto()
    # Set_Destination = enum.auto()
    Reset_All = enum.auto()
    Set_Language = enum.auto()
    # Set_Number_Of_words = enum.auto()
    # Set_Word_Buffer_Size = enum.auto()


class VocabularyCommand(AbstractCommandClass):
    Help = enum.auto()

    Extend_Vocabulary_List = enum.auto()
    Rewrite_Word = enum.auto()
    Discard_Word = enum.auto()
    Clear_Vocabulary_List = enum.auto()
    Rewrite_Suffix = enum.auto()
    # Redact_Vocabulary_List = enum.auto()
    # Redact_Word = enum.auto()
    Reverse = enum.auto()
    Copy_Vocabulary_List = enum.auto()


class RegexCommand(AbstractCommandClass):
    Enter_Regex = enum.auto()
    Reset = enum.auto()
    Reverse_Groups = enum.auto()
    Slice = enum.auto()
    Slice_Redacted = enum.auto()


class HiddenCommand(AbstractCommandClass):
    Set_Subject_And_Predicate_Image = enum.auto()
    Persist_Image = enum.auto()
