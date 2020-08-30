import enum
from pathlib import Path
from varsaver import Savable
from students_queue import Student


class AccessLevel(enum.Enum):
    GOD = 0,
    ADMIN = 1,
    USER = 2


class StudentsRegisteredManager(Savable):

    _file_registered_users = Path('data/registered.data')

    # dictionary with id`s as keys and levels as values stored in file
    _file_access_levels = Path('data/access_levels.data')

    _students_reg = []

    def __init__(self, students=None):
        if students is None:
            self._students_reg = []

    def __contains__(self, item):
        for student in self._students_reg:
            if student.telegram_id == item.telegram_id:
                return True
        return False

    def get_users(self):
        return self._students_reg

    def append_user(self, name, telegram_id):
        self._students_reg.append(Student(name, telegram_id))

    def append_users(self, users):
        if isinstance(users, Student):
            self._students_reg.append(users)
        else:
            self._students_reg.extend(users)

    def remove_by_index(self, index):
        for index in index:
            self._students_reg.pop(index)

    def get_names_users(self):
        return [st.name for st in self._students_reg]

    def get_user_by_name(self, name):
        for student in self._students_reg:
            if student.name == name:
                return student
        return None

    def get_users_str(self):
        str_list = []
        i = 1
        for student in self._students_reg:
            str_list.append('{0}. {1}-{2}'.format(i, student.name, str(student.get_id())))
            i += 1

        return 'Все известные пользователи:\n' + '\n'.join(str_list)

    def set_admin(self, admin_id):
        for student in self._students_reg:
            if student.telegram_id == admin_id:
                student.set_access(AccessLevel.ADMIN)

    def set_user(self, user_id):
        for student in self._students_reg:
            if student.telegram_id == user_id:
                student.set_access(AccessLevel.ADMIN)

    def update_access_levels(self, loader):
        access_level_updates = loader.load(self._file_access_levels)
        if access_level_updates is not None:
            for student in self._students_reg:
                if student.get_id() in access_level_updates:
                    student.set_access(AccessLevel(access_level_updates[student.get_id()]))

    def find_similar_student(self, name):
        for student in self._students_reg:
            if self.similarity(name, student.name):
                return student
        return Student(name, None)

    @staticmethod
    def similarity(first, second):
        if (len(first) - len(second)) > 2:
            return False

        if first[0] != second[0]:
            return False

        if len(first) - sum(l1 == l2 for l1, l2 in zip(first[1:], second[1:])) > 2:
            return False
        return True

    def parse_users(self, string):
        if '\n' in string:
            new_users_str_lines = string.split('\n')
        else:
            new_users_str_lines = [string]

        err_list = []
        new_users = []

        for line in new_users_str_lines:
            try:
                user_temp = line.split('-')
                user = Student(user_temp[0], int(user_temp[1]))

                if user not in self:
                    new_users.append(user)
            except Exception:
                err_list.append(line)

        return new_users, err_list

    def save_to_file(self, saver):
        saver.save(self._students_reg, self._file_registered_users)

    def load_file(self, loader):
        self._students_reg = loader.load(self._file_registered_users)

    def get_save_files(self):
        return [self._file_registered_users, self._file_access_levels]
