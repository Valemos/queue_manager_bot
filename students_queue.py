import enum
import random as rnd
from pathlib import Path
from bot_messages import *
from registered_manager import StudentsRegisteredManager
from registered_manager import AccessLevel
from varsaver import Savable


class Student:

    _access_level = AccessLevel.USER

    def __init__(self, name, telegram_id):
        self._name = name
        self.telegram_id = telegram_id

    def get_string(self, position=None):
        if position is None:
            return self._name
        else:
            return '{0} - {1}'.format(position, self._name)

    def log_str(self):
        return self._name + ' - ' + str(self.telegram_id)

    def set_access(self, access_level):
        self._access_level = access_level


class StudentsQueue(Savable):

    _students = []
    queue_pos = 0
    registered_manager = None

    _file_queue = Path('queue.data')
    _file_queue_state = Path('queue_state.data')

    def __init__(self, students_manager=None, students=None):
        if students_manager is None:
            self.registered_manager = StudentsRegisteredManager()

        if students is None:
            students = []

        self._students = students

    def __len__(self):
        return len(self._students)

    def __contains__(self, item):
        for student in self._students:
            if student.telegram_id == item.telegram_id:
                return True
        return False

    def move_prev(self):
        if self.queue_pos > 0:
            self.queue_pos -= 1
            return True
        return False

    def move_next(self):
        if self.queue_pos < len(self._students):
            self.queue_pos -= 1
            return True
        return False

    def move_to_end(self, position):
        self._students.append(self._students.pop(position))

    def swap(self, position1, position2):
        self._students[position1], self._students[position2] = self._students[position2], self._students[position1]

    # if student registered as user, returns True, otherwise False
    def append_by_name(self, name):
        student = self.registered_manager.get_user_by_name(name)
        if student is not None:
            self._students.append(student)
            return True
        else:
            self._students.append(self.registered_manager.find_similar_student(name))
            return False

    def clear(self):
        self._students = []
        self.queue_pos = 0

    def remove_by_index(self, index):
        if isinstance(index, int):
            self._students.pop(index)
        else:
            for ind in index:
                self._students.pop(ind)

    def get_string(self):
        if len(self._students) > 0:
            if self.queue_pos is not None:

                str_list = []

                cur_item, next_item = self.get_cur_and_next()

                if cur_item is None:
                    return msg_queue_finished

                str_list.append('Сдает:')
                str_list.append(self.queue_pos)
                str_list.append('\nСледующий:')
                if next_item is not None:
                    str_list.append(self._students[self.queue_pos + 1].get_string(self.queue_pos + 1))
                else:
                    str_list.append('Нет')

                if (self.queue_pos + 2) < len(self._students):
                    str_list.append('\nОставшиеся:')
                    for i in range(self.queue_pos + 2, len(self._students)):
                        str_list.append(self._students[i].get_string(i))

                return '\n'.join(str_list) + '\n\n' + msg_queue_commands
            else:
                return 'Очередь:\n' + '\n'.join([self._students[i].get_string(i) for i in range(len(self._students))])

        return msg_queue_finished

    def get_cur_and_next(self):
        if 0 <= self.queue_pos < len(self._students) - 1:
            return self._students[self.queue_pos], self._students[self.queue_pos + 1]
        elif self.queue_pos == len(self._students) - 1:
            return self._students[self.queue_pos], None
        return None, None

    # get string format of result of get_cur_and_next() call
    def get_cur_and_next_str(self):
        msg = ''
        cur_stud, next_stud = self.get_cur_and_next()
        if cur_stud is not None:
            msg = 'Сдает - {0}'.format(cur_stud.get_string())

        if next_stud is not None:
            msg += '\nГотовится - {0}'.format(next_stud.get_string())

        return msg if msg != '' else msg_queue_finished

    # find students
    def parse_students(self, students_str):
        if '\n' in students_str:
            names = students_str.split('\n')
        else:
            names = [students_str]

        students = []
        for name in names:
            user = self.registered_manager.get_user_by_name(name)
            if user is None:
                students.append(self.registered_manager.find_similar_student(name))
            else:
                students.append(user)
        return students

    def parse_index_list(self, string):
        index_str = []
        if ' ' in string:
            index_str = string.split(' ')
        else:
            index_str = [string]

        err_list = []
        correct_indexes = []

        for pos_str in index_str:
            try:
                position = int(pos_str)
                if 0 < position <= len(self._students):
                    correct_indexes.append(position)
                else:
                    err_list.append(pos_str)
            except Exception:
                err_list.append(pos_str)

        return correct_indexes, err_list

    def generate_simple(self, students=None):
        if students is None:
            self._students = self.registered_manager.get_users()
        else:
            self._students = students

    def generate_random(self, students=None):
        if students is None:
            self._students = rnd.shuffle(self.registered_manager.get_users())
        else:
            self._students = rnd.shuffle(students)

    def load_file(self, saver):
        self._students = saver.load(self._file_queue)
        state = saver.load(self._file_queue_state)

        if state is not None:
            self.queue_pos = state['cur_queue_pos']
        else:
            self.queue_pos = 0

    def save_to_file(self, saver):
        saver.save(self._students, self._file_queue)
        saver.save({'cur_queue_pos': self.queue_pos}, self._file_queue_state)

    def get_save_files(self):
        return [self._file_queue, self._file_queue_state]
