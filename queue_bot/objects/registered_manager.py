from pathlib import Path
from typing import Optional

from pyjarowinkler import distance  # string similarity
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from queue_bot.database import Base, Session
from queue_bot.objects.queue_user_info import QueueUserInfo
from queue_bot.objects.student import Student
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack


# todo finish persistence
class RegisteredManager(Base):
    __tablename__ = 'registered'

    chat_id = Column(Integer, primary_key=True, default=0)
    students = relationship("Student")

    def __init__(self, chat_id, students=None):
        if chat_id is None:
            raise ValueError('Cannot create registered manager without chat id')

        self.chat_id = chat_id
        self.students = students if students is not None else []

    def __len__(self):
        return len(self.students)

    def __contains__(self, item):
        return item in self.students

    def get_users(self):
        return self.students

    def add_new_user(self, name, telegram_id):
        with Session.begin() as session:
            new_student = Student(name, telegram_id)
            new_student.chat_id = self.chat_id
            session.add(new_student)
            return new_student

    def append_users(self, users):
        if isinstance(users, Student):
            self.students.append(users)
        else:
            for user in users:
                if user not in self.students:
                    self.students.append(user)

    def rename_user(self, student, new_name):
        if student in self.students:
            self.students[self.students.index(student)].name = new_name

    def remove_by_index(self, index):
        if isinstance(index, int):
            self.students.pop(index)
        else:
            to_delete = []
            for i in index:
                to_delete.append(self.students[i])

            deleted = False
            for elem in to_delete:
                self.students.remove(elem)
                deleted = True
            return deleted

    def remove_by_id(self, remove_id: int):
        for i in range(len(self.students)):
            if self.students[i].telegram_id == remove_id:
                self.students.pop(i)
                return True
        return False

    # converts list of names to Student objects
    def get_registered_students(self, names: list):
        students = []
        for name in names:
            student = self.get_by_name(name)
            if student is None:
                student = self.find_similar_student(name)
            elif student is None:
                student = Student(name, 0)
            students.append(student)

        return students

    def get_update_user_info(self, update):
        student = self.get_by_id(update.effective_user.id)
        if student is None:
            return QueueUserInfo(update.effective_user.full_name, None, AccessLevel.USER)
        return QueueUserInfo.from_student(student)

    def get_by_name(self, name: int) -> Optional[Student]:
        for student in self.students:
            if student.name == name:
                return student
        return None

    def get_by_id(self, search_id: int) -> Optional[Student]:
        with Session() as session:
            return session.query(Student).filter_by(
                chat_id=self.chat_id,
                telegram_id=search_id).first()

    def get_users_str(self):
        str_list = []
        i = 1
        for student in self.students:
            str_list.append('{0}. {1}-{2}'.format(i, student.name, str(student.telegram_id)))
            i += 1

        return language_pack.all_known_users.format('\n'.join(str_list))

    def get_users_keyboard(self, command):
        return self.main_bot.keyboards.generate_keyboard(
            command,
            [s.name for s in self.students],
            [s.str_name_id() for s in self.students])

    def get_admins_keyboard(self, command):
        admins = []
        for user in self.students:
            if user.access_level is AccessLevel.ADMIN:
                admins.append(user)

        return self.main_bot.keyboards.generate_keyboard(
            command,
            [s.name for s in admins],
            [s.str_name_id() for s in admins])

    def exists_user_access(self, access_level):
        for user in self.students:
            if user.access_level is access_level:
                return True
        return False

    def set_god(self, god_id: int):
        user = self.get_by_id(god_id)
        if user is not None:
            user.access_level = AccessLevel.GOD
            return True
        return False

    def set_admin(self, admin_id: int):
        user = self.get_by_id(admin_id)
        if user is not None:
            user.access_level = AccessLevel.ADMIN
            return True
        return False

    def set_user(self, user_id: int):
        user = self.get_by_id(user_id)
        if user is not None:
            user.access_level = AccessLevel.USER
            return True
        return False

    def find_similar_student(self, name: str):
        for student in self.students:
            if RegisteredManager.is_similar(name, student.name):
                return student
        return None

    @staticmethod
    def is_similar(first: str, second: str):
        dist = distance.get_jaro_distance(first, second)
        return dist > 0.9

    # by default this function requires private chat to allow commands
    def check_access(self, update, level_requirement=AccessLevel.ADMIN):
        info = self.get_update_user_info(update)
        return info.access_level.value <= level_requirement.value


def get_chat_registered(chat_id) -> RegisteredManager:
    with Session() as session:
        registered = session.query(RegisteredManager).filter_by(chat_id=chat_id).first()
        if registered is None:
            with session.begin():
                registered = RegisteredManager(chat_id)
                session.add(registered)
        return registered
