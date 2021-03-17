from pyjarowinkler import distance

from queue_bot.bot import keyboards
from queue_bot.database import db_session
from queue_bot.objects.student import Student
from queue_bot.bot.access_levels import AccessLevel
import queue_bot.languages.bot_messages_rus as language_pack

from telegram import Chat

from queue_bot.objects.student_abstract import AbstractStudent
from queue_bot.objects.student_factory import student_factory


class RegisteredManager:

    students = []

    def __init__(self, students=None):
        if students is None:
            self.students = self.load_students()

    def __len__(self):
        return len(self.students)

    def __contains__(self, item):
        return item in self.students

    @staticmethod
    def load_students():
        session = db_session()
        students = [student_factory(s) for s in session.query(AbstractStudent).all()]
        session.close()
        return students

    def get_users(self):
        return self.students

    def add_user(self, name, telegram_id):
        # todo add database interaction
        self.students.append(student_factory(name, telegram_id))

    def append_users(self, users):
        # todo add database interaction
        if isinstance(users, Student):
            self.students.append(users)
        else:
            for user in users:
                if user not in self.students:
                    self.students.append(user)

    def rename_user(self, student, new_name):
        # todo add database interaction
        if student in self.students:
            self.students[self.students.index(student)].name = new_name

    def remove_by_id(self, remove_id: int):
        # todo add database interaction
        for i in range(len(self.students)):
            if self.students[i].telegram_id == remove_id:
                self.students.pop(i)
                return True
        return False

    # converts list of names to Student objects
    def get_registered_students(self, names: list):
        # todo add database interaction
        students = []
        for name in names:
            student = self.get_user_by_name(name)
            if student is None:
                student = self.find_similar_student(name)
            elif student is None:
                student = student_factory(name, 0)
            students.append(student)

        return students

    def get_user_by_update(self, update):
        student = self.get_user_by_id(update.effective_user.telegram_id)
        if student is None:
            return student_factory(update.effective_user.full_name, None)
        return student

    def get_user_by_name(self, name: int):
        # todo add database interaction
        for student in self.students:
            if student.name == name:
                return student
        return None

    def get_user_by_id(self, search_id: int):
        # todo add database interaction
        for student in self.students:
            if student.telegram_id == search_id:
                return student
        return None

    def get_users_str(self):
        return language_pack.all_known_users.format(
            '\n'.join([f"{i}. {student.name_id_str()}" for i, student in enumerate(self.students)]))

    def get_users_keyboard(self, command):
        return keyboards.generate_keyboard(
            command,
            [s.name for s in self.students],
            [s.code_str() for s in self.students])

    def get_admins_keyboard(self, command):
        admins = []
        for user in self.students:
            if user.access_level is AccessLevel.ADMIN:
                admins.append(user)

        return keyboards.generate_keyboard(
            command,
            [s.name for s in admins],
            [s.code_str() for s in admins])

    def exists_user_access(self, access_level):
        for user in self.students:
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
        for student in self.students:
            if RegisteredManager.is_similar(name, student.name):
                return student_factory(student)
        return student_factory(name, None)

    @staticmethod
    def is_similar(first: str, second: str):
        dist = distance.get_jaro_distance(first, second)
        return dist > 0.9

    def update_access_levels(self, saver):
        # todo change to database loading
        access_level_updates = saver.load(self._file_access_levels)
        if access_level_updates is not None:
            for student in self.students:
                if student.telegram_id in access_level_updates:
                    student.access_level = AccessLevel(access_level_updates[student.telegram_id])

    # by default this function requires private chat to allow command_handling
    def check_access(self, update, level_requirement=AccessLevel.ADMIN, check_chat_private=True):
        student = self.get_user_by_update(update)

        if check_chat_private:
            if update.effective_chat.type != Chat.PRIVATE:
                return False

        return student.access_level.value <= level_requirement.value
