from pathlib import Path

from queue_bot.languages.language_interface import Translatable
from queue_bot.varsaver import Savable, VariableSaver
from queue_bot.students_queue import Student, Student_EMPTY
from queue_bot.bot_access_levels import AccessLevel


class StudentsRegisteredManager(Savable, Translatable):

    _file_registered_users = Path('registered.data')

    # dictionary with id`s as keys and levels as values stored in file
    _file_access_levels = Path('access_levels.data')
    _students_reg = []

    def __init__(self, main_bot, students=None):
        if students is None:
            self._students_reg = []
        self.main_bot = main_bot

    def __len__(self):
        return len(self._students_reg)

    def __contains__(self, item):
        for student in self._students_reg:
            if student.telegram_id == item.telegram_id:
                return True
        return False

    def get_language_pack(self):
        return self.main_bot.get_language_pack()

    def get_users(self):
        return self._students_reg

    def append_new_user(self, name, telegram_id):
        new_student = Student(name, telegram_id)
        self._students_reg.append(new_student)
        return new_student

    def append_users(self, users):
        if isinstance(users, Student):
            self._students_reg.append(users)
        else:
            for user in users:
                if user not in self._students_reg:  # TODO check for correct user recognition
                    self._students_reg.append(user)

    def rename(self, index, new_name):
        if 0 <= index < len(self._students_reg):
            self._students_reg[index].name = new_name

    def remove_by_index(self, index):
        if isinstance(index, int):
            self._students_reg.pop(index)
        else:
            for index in index:
                self._students_reg.pop(index)

    def remove_by_id(self, remove_id: int):
        to_delete = []
        for i in range(len(self._students_reg)):
            if self._students_reg[i].telegram_id == remove_id:
                to_delete.append(self._students_reg[i])

        deleted = False
        for elem in to_delete:
            self._students_reg.remove(elem)
            deleted = True

        return deleted

    def get_user_by_name(self, name: int):
        for student in self._students_reg:
            if student.name == name:
                return student
        return None

    def get_user_by_id(self, search_id: int) -> Student:
        for student in self._students_reg:
            if student.telegram_id == search_id:
                return student
        return Student_EMPTY

    def get_users_str(self):
        str_list = []
        i = 1
        for student in self._students_reg:
            str_list.append('{0}. {1}-{2}'.format(i, student.name, str(student.telegram_id)))
            i += 1

        return self.get_language_pack().all_known_users.format('\n'.join(str_list))

    def set_god(self, god_id: int):
        user = self.get_user_by_id(god_id)
        if user is not Student_EMPTY:
            user.access_level = AccessLevel.GOD
            return True
        return False

    def set_admin(self, admin_id: int):
        user = self.get_user_by_id(admin_id)
        if user is not Student_EMPTY:
            user.access_level = AccessLevel.ADMIN
            return True
        return False

    def set_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user is not Student_EMPTY:
            user.access_level = AccessLevel.USER
            return True
        return False

    def find_similar_student(self, name: str):
        for student in self._students_reg:
            if self.is_similar(name, student.name):
                return student
        return Student(name, None)

    @staticmethod
    def is_similar(first: str, second: str):
        if (len(first) - len(second)) > 2:
            return False

        if first[0] != second[0]:
            return False

        if len(first) - sum(l1 == l2 for l1, l2 in zip(first[1:], second[1:])) > 2:
            return False
        return True



    def update_access_levels(self, saver: VariableSaver):
        access_level_updates = saver.load(self._file_access_levels)
        if access_level_updates is not None:
            for student in self._students_reg:
                if student.telegram_id in access_level_updates:
                    student.access_level = AccessLevel(access_level_updates[student.telegram_id])
            self.save_to_file(saver)

    def save_to_file(self, saver: VariableSaver):
        saver.save(self._students_reg, self._file_registered_users)

    def load_file(self, loader: VariableSaver):
        self._students_reg = loader.load(self._file_registered_users)
        if self._students_reg is None:
            self._students_reg = []

    def get_save_files(self):
        return [self._file_registered_users, self._file_access_levels]

    def check_access(self, user_id: int, level_requriment=AccessLevel.ADMIN):
        user = self.get_user_by_id(user_id)
        if user is not None:
            if user.access_level.value <= level_requriment.value:
                return True
        return False
