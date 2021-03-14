from pathlib import Path
from pyjarowinkler import distance  # string similarity
from queue_bot.objects.student import Student
from queue_bot.bot.access_levels import AccessLevel

from telegram import Chat


class StudentsRegisteredManager:

    students_reg = []

    def __init__(self, main_bot, students=None):
        if students is None:
            self.students_reg = []
        self.main_bot = main_bot

    def __len__(self):
        return len(self.students_reg)

    def __contains__(self, item):
        return item in self.students_reg

    def get_users(self):
        return self.students_reg

    def add_user(self, name, telegram_id):
        self.students_reg.append(Student(name, telegram_id))

    def append_users(self, users):
        if isinstance(users, Student):
            self.students_reg.append(users)
        else:
            for user in users:
                if user not in self.students_reg:
                    self.students_reg.append(user)

    def rename_user(self, student, new_name):
        if student in self.students_reg:
            self.students_reg[self.students_reg.index(student)].name = new_name

    def remove_by_id(self, remove_id: int):
        for i in range(len(self.students_reg)):
            if self.students_reg[i].telegram_id == remove_id:
                self.students_reg.pop(i)
                return True
        return False

    # converts list of names to Student objects
    def get_registered_students(self, names: list):
        students = []
        for name in names:
            student = self.get_user_by_name(name)
            if student is None:
                student = self.find_similar_student(name)
            elif student is None:
                student = Student(name, 0)
            students.append(student)

        return students

    def get_user_by_update(self, update):
        student = self.get_user_by_id(update.effective_user.id)
        if student is None:
            return Student(update.effective_user.full_name, None)
        return student

    def get_user_by_name(self, name: int):
        for student in self.students_reg:
            if student.name == name:
                return student
        return None

    def get_user_by_id(self, search_id: int):
        for student in self.students_reg:
            if student.telegram_id == search_id:
                return student
        return None

    def get_users_str(self):
        str_list = []
        i = 1
        for student in self.students_reg:
            str_list.append('{0}. {1}-{2}'.format(i, student.name, str(student.telegram_id)))
            i += 1

        return self.main_bot.language_pack.all_known_users.format('\n'.join(str_list))

    def get_users_keyboard(self, command):
        return self.main_bot.keyboards.generate_keyboard(
            command,
            [s.name for s in self.students_reg],
            [s.str_name_id() for s in self.students_reg])

    def get_admins_keyboard(self, command):
        admins = []
        for user in self.students_reg:
            if user.access_level is AccessLevel.ADMIN:
                admins.append(user)

        return self.main_bot.keyboards.generate_keyboard(
            command,
            [s.name for s in admins],
            [s.str_name_id() for s in admins])

    def exists_user_access(self, access_level):
        for user in self.students_reg:
            if user.access_level is access_level:
                return True
        return False

    def set_god(self, god_id: int):
        user = self.get_user_by_id(god_id)
        if user is not None:
            user.access_level = AccessLevel.GOD
            return True
        return False

    def set_admin(self, admin_id: int):
        user = self.get_user_by_id(admin_id)
        if user is not None:
            user.access_level = AccessLevel.ADMIN
            return True
        return False

    def set_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user is not None:
            user.access_level = AccessLevel.USER
            return True
        return False

    def find_similar_student(self, name: str):
        for student in self.students_reg:
            if StudentsRegisteredManager.is_similar(name, student.name):
                return student
        return Student(name, None)

    @staticmethod
    def is_similar(first: str, second: str):
        dist = distance.get_jaro_distance(first, second)
        return dist > 0.9

    def update_access_levels(self, saver):
        # todo change to file loading
        access_level_updates = saver.load(self._file_access_levels)
        if access_level_updates is not None:
            for student in self.students_reg:
                if student.telegram_id in access_level_updates:
                    student.access_level = AccessLevel(access_level_updates[student.telegram_id])

    # by default this function requires private chat to allow commands
    def check_access(self, update, level_requriment=AccessLevel.ADMIN, check_chat_private=True):
        student = self.get_user_by_update(update)

        if check_chat_private:
            if update.effective_chat.type != Chat.PRIVATE:
                return False

        return student.access_level.value <= level_requriment.value
