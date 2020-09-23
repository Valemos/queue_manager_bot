from queue_bot.object_file_saver import FolderType
from queue_bot.savable_interface import Savable
from pathlib import Path
import pandas as pd


# controls priority for student choice
class Choice:

    def __init__(self, student, choice_list: list):
        self.student = student
        self.priority_choices = choice_list
        self.finally_chosen = None

    def __eq__(self, other):
        if self.student == other.student:
            return True
        return False

    def __ne__(self, other):
        if self.student != other.student:
            return True
        return False

    def update_final_choice(self, available: dict, limit=1):
        for choice in self.priority_choices:
            if available[choice] < limit:
                self.finally_chosen = choice
                available[choice] += 1
                return choice, available
        return None, available


class SubjectChoiceGroup:

    def __init__(self, subject_name, available_range: (int, int), priority_limit=5, repeat_limit=1):
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
            chosen_subject, self.available_subjects = choice.update_final_choice(
                                                        self.available_subjects,
                                                        self.repeat_limit)
            if chosen_subject is not None:
                self.student_choices.append(choice)

            return chosen_subject
        else:
            choice_idx = self.student_choices.index(choice)

            # revert previous subject choice
            self.available_subjects[self.student_choices[choice_idx].finally_chosen] -= 1
            # update using current choice
            chosen_subject, self.available_subjects = choice.update_final_choice(self.available_subjects, self.repeat_limit)

            # if choice valid, update it
            if chosen_subject is not None:
                self.student_choices[choice_idx] = choice

            return chosen_subject

    def remove(self, choice: Choice):
        if choice in self.student_choices:
            self.student_choices.remove(choice)
            self.update_choices()

    def update_choices(self):
        self.available_subjects = {i: 0 for i in range(self.available_range[0], self.available_range[1] + 1)}
        for choice in self.student_choices:
            self.available_subjects = choice.update_final_choice(self.available_subjects, self.repeat_limit)[1]

    def get_students_choices(self):
        self.student_choices = sorted(self.student_choices, key=lambda item: item.student.name)
        return {choice.student: choice for choice in self.student_choices}

    def save_to_excel(self):
        student_priorities = self.get_students_choices()

        data = {'Имя': ['']*len(student_priorities), 'Тема': [0] * len(student_priorities)}
        data.update({'приоритет' + str(i): [''] * len(student_priorities) for i in range(1, self.priority_limit + 1)})

        index = 0
        for choice in self.student_choices:
            data['Имя'][index] = choice.student.name
            data['Тема'][index] = student_priorities[choice.student].finally_chosen

            for i in range(1, len(choice.priority_choices) + 1):
                data['приоритет' + str(i)][index] = choice.priority_choices[i - 1]
            index += 1

        self.excel_file.parent.mkdir(parents=True, exist_ok=True)
        self.excel_file.open('w').close()

        df = pd.DataFrame(data)
        writer = pd.ExcelWriter(self.excel_file, engine='openpyxl')
        df.to_excel(writer, index=False)
        writer.save()
        return self.excel_file

    def get_save_files(self):
        return [FolderType.SubjectChoices.value / self.excel_file]


class SubjectChoiceManager(Savable):

    file_current_subject = FolderType.SubjectChoices.value / Path('current_choice_subject.data')

    def __init__(self):
        self.current_subjects = None
        self.can_choose = False

    def start_choosing(self):
        self.can_choose = self.current_subjects is not None
        return self.can_choose

    def stop_choosing(self):
        self.can_choose = False

    def get_choices_str(self):
        choice_str = []
        for choice in self.current_subjects.get_students_choices().values():
            choice_str.append('{0} - {1}'.format(choice.student.name, choice.finally_chosen))
        return '\n'.join(choice_str), self.get_available_str()

    def get_available_str(self):
        available_str = []
        for subject, count in self.current_subjects.available_subjects.items():
            if count < self.current_subjects.repeat_limit:
                available_str.append(str(subject))

        return ', '.join(available_str)

    def get_subject_range(self):
        return self.current_subjects.available_range

    def get_priority_limit(self):
        if self.current_subjects is not None:
            return self.current_subjects.priority_limit
        return 5

    def add_choice(self, student, priority_choices):
        if self.current_subjects is not None:
            if len(priority_choices) > 0:
                return self.current_subjects.add(Choice(student, priority_choices[: self.get_priority_limit()]))
        return None

    def remove_choice(self, student_requested):
        self.current_subjects.remove(Choice(student_requested, []))

    def set_choice_group(self, name, value_range, repeat_limit, priority_limit=5):
        if self.current_subjects is not None:
            self.current_subjects.save_to_excel()
        self.current_subjects = SubjectChoiceGroup(name, value_range, priority_limit, repeat_limit)

    def save_to_excel(self):
        return self.current_subjects.save_to_excel()

    def save_to_file(self, saver):
        self.current_subjects.save_to_excel()
        saver.save(self.current_subjects, self.file_current_subject)

    def load_file(self, saver):
        self.current_subjects = saver.load(self.file_current_subject)
        if self.current_subjects is None:
            self.current_subjects = []

    def get_save_files(self):
        return [FolderType.SubjectChoices.value / self.file_current_subject]
