from queue_bot.varsaver import Savable, FolderType
from pathlib import Path
import pandas as pd


# controls priority for student choice
class Choice:

    def __init__(self, student, choice_list):
        self.student = student
        self.priority_choices = choice_list

    def __eq__(self, other):
        if self.student == other.student:
            return True
        return False

    def __ne__(self, other):
        if self.student != other.student:
            return True
        return False

    def get_choice(self, available: list):
        for choice in self.priority_choices:
            if choice in available:
                return choice


class SubjectChoiceGroup:

    def __init__(self, subject_name, available_choices: list, priority_limit=5, repeat_limit=0):
        self.name = subject_name
        self.priority_limit = priority_limit
        self.repeat_limit = repeat_limit

        # this variable stores dict with counts
        self.available_choices = {i: 0 for i in available_choices}
        self.student_choices = []

        # self.choices_file = Path("{0}.data".format(subject_name))
        self.excel_file = FolderType.SubjectChoices.value / Path("{0}.xlsx".format(self.name))

    def add(self, choice: Choice):
        if choice not in self.student_choices:
            self.student_choices.append(choice)

    def update(self, choice: Choice):
        if choice in self.student_choices:
            self.student_choices[self.student_choices.index(choice)] = choice

    def delete(self, choice: Choice):
        if choice in self.student_choices:
            self.student_choices.remove(choice)

    def get_students_choices(self):
        # todo write choice algorythm. it will use available choices dict to limit maximum subject choice number
        pass

    def save_to_excel(self):
        data = {}
        for choice in self.student_choices:
            data['student_name'] = choice.student.name
            # save all 5 priorities to data dict
            for i in range(len(choice.priority_choices)):
                data[str(i)] = choice.priority_choices[i]

        df = pd.DataFrame(data)
        writer = pd.ExcelWriter(self.excel_file, engine='openpyxl')
        df.to_excel(writer, index=False)
        writer.save()

    def get_save_files(self):
        return [self.excel_file]


class SubjectChoiceManager(Savable):

    file_current_subject = Path('current_choice_subject.data')

    def __init__(self):
        self.current_subject = None
        self.can_choose = False

    def start_choosing(self):
        if self.current_subject is None:
            return False
        self.can_choose = True
        return True

    def stop_choosing(self):
        self.can_choose = False

    def get_priority_limit(self):
        if self.current_subject is not None:
            return self.current_subject.priority_limit
        return 0

    def add_choice(self, student, priority_choices):
        if self.current_subject is not None:
            self.current_subject.add_choice(Choice(student, priority_choices))
            return True
        return False

    def set_choice_group(self, name, available, repeat_limit, priority_limit=5):
        if self.current_subject is not None:
            self.current_subject.save_to_excel()
        self.current_subject = SubjectChoiceGroup(name, available, priority_limit, repeat_limit)

    def save_to_file(self, saver):
        self.current_subject.save_to_excel()
        saver.save(self.current_subject, self.file_current_subject, FolderType.SubjectChoices)

    def load_file(self, saver):
        self.current_subject = saver.load(self.file_current_subject, FolderType.SubjectChoices)

    def get_save_files(self):
        return [self.file_current_subject] + self.current_subject.get_save_files()
