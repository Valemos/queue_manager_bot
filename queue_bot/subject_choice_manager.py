from queue_bot.varsaver import Savable, FolderType
from pathlib import Path


# controls priority for student choice
class Choice:

    def __init__(self, student, choice_list):
        self.student = student
        self.choices = choice_list

    def get_choice(self, already_chosen):
        for choice in self.choices:
            if choice not in already_chosen:
                return choice


# TODO implement excel file creation and choice append to that file. Files is unique for each chat
class SubjectChoiceManager(Savable):

    def __init__(self):
        self.chat_choice_file = {}
        self.available_choices = []

    def set_available_choices(self, choices):
        self.available_choices = choices

    def create_new_choice_file(self, chat_id, filename):
        # new_path =
        pass

    def save_to_file(self, saver):
        pass

    def load_file(self, saver):
        pass

    def get_save_files(self):
        return list(self.chat_choice_file.values())
