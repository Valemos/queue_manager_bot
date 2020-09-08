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

    def get_choice(self, available: dict, limit = 1):
        for choice in self.priority_choices:
            if available[choice.student.id] < limit:
                return choice


class SubjectChoiceGroup:

    def __init__(self, subject_name, available_range: (int, int), priority_limit=5, repeat_limit=0):
        self.name = subject_name
        self.priority_limit = priority_limit
        self.repeat_limit = repeat_limit

        # this variable stores dict with counts
        self.available_range = available_range
        self.available_subjects = {i: 0 for i in range(self.available_range[0], self.available_range[1] + 1)}
        self.student_choices = []

        # self.choices_file = Path("{0}.data".format(subject_name))
        self.excel_file = FolderType.SubjectChoices.value / Path("{0}.xlsx".format(self.name))

    def add(self, choice: Choice):
        if choice not in self.student_choices:
            self.student_choices.append(choice)

    def delete(self, choice: Choice):
        if choice in self.student_choices:
            self.student_choices.remove(choice)

    def get_students_choices(self):
        self.available_subjects = {i: 0 for i in range(self.available_range[0], self.available_range[1] + 1)}
        student_choices = {}
        for choice in self.student_choices:
            chosen_subject = choice.get_choice(self.available_subjects, self.repeat_limit)
            self.available_subjects[chosen_subject] += 1
            student_choices[choice.student] = chosen_subject
        return sorted(student_choices, key=lambda item: item[0].name)

    def save_to_excel(self):
        final_choices = self.get_students_choices()

        data = {'Имя': [], 'Тема': []}
        data.update({'приоритет' + str(i): [] for i in range(1, self.priority_limit + 1)})

        for choice in self.student_choices:
            data['Имя'] = choice.student.name
            # todo write choices to excel

            # save all priorities to data dict


        df = pd.DataFrame(data)
        writer = pd.ExcelWriter(self.excel_file, engine='openpyxl')
        df.to_excel(writer, index=False)
        writer.save()
        return self.excel_file

    def get_save_files(self):
        return [self.excel_file]


class SubjectChoiceManager(Savable):

    file_current_subject = Path('current_choice_subject.data')

    def __init__(self):
        self.current_subject = None
        self.can_choose = False

    def start_choosing(self):
        self.can_choose = self.current_subject is not None
        return self.can_choose

    def stop_choosing(self):
        self.can_choose = False

    def get_choices_str(self):
        string = ''
        for student, subject in self.current_subject.get_students_choices().items():
            string += '{0} - {1}'.format(student.name, subject)
        return string

    def get_subject_range(self):
        return self.current_subject.available_range

    def get_priority_limit(self):
        if self.current_subject is not None:
            return self.current_subject.priority_limit
        return 5

    def add_choice(self, student, priority_choices):
        if self.current_subject is not None:
            self.current_subject.add_choice(Choice(student, priority_choices[:self.get_priority_limit()]))
            return True
        return False

    def set_choice_group(self, name, value_range, repeat_limit, priority_limit=5):
        if self.current_subject is not None:
            self.current_subject.save_to_excel()
        self.current_subject = SubjectChoiceGroup(name, value_range, priority_limit, repeat_limit)

    def save_to_excel(self):
        return self.current_subject.save_to_excel()

    def save_to_file(self, saver):
        self.current_subject.save_to_excel()
        saver.save(self.current_subject, self.file_current_subject, FolderType.SubjectChoices)

    def load_file(self, saver):
        self.current_subject = saver.load(self.file_current_subject, FolderType.SubjectChoices)

    def get_save_files(self):
        if self.current_subject is not None:
            return [self.file_current_subject] + self.current_subject.get_save_files()
        else:
            return [self.file_current_subject]
