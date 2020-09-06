import random as rnd
from pathlib import Path
from queue_bot.varsaver import Savable
from queue_bot.bot_access_levels import AccessLevel
from queue_bot.languages.language_interface import BotMessages, Translatable


class Student:

    def __init__(self, name, telegram_id):
        self.name = name
        self.telegram_id = telegram_id
        self.access_level = AccessLevel.USER

    def __eq__(self, other):
        return self.telegram_id == other.telegram_id

    def __ne__(self, other):
        return self.telegram_id != other.telegram_id

    def __str__(self):
        return self.str()

    def str(self, position=None):
        if position is None:
            return self.name
        else:
            return '{0} - {1}'.format(position, self.name)

    def log_str(self):
        return '{0} - {1}'.format(self.name, str(self.telegram_id))


Student_EMPTY = Student('empty_student', None)


class StudentsQueue(Savable, Translatable):

    _students = []
    queue_pos = 0

    _file_queue = Path('queue.data')
    _file_queue_state = Path('queue_state.data')

    def get_language_pack(self):
        if self.main_bot is not None:
            return self.main_bot.get_language_pack()
        return None

    def __init__(self, bot, students=None):
        if students is None:
            students = []

        self.main_bot = bot
        self._students = students

    def __len__(self):
        if self._students is None:
            return 0
        return len(self._students)

    def __contains__(self, item):
        if isinstance(item, Student):
            for student in self._students:
                if student.telegram_id == item.telegram_id:
                    return True
        elif isinstance(item, int):
            for student in self._students:
                if student.telegram_id == item:
                    return True
        return False

    def move_prev(self):
        if self.queue_pos > 0:
            self.queue_pos -= 1
            return True
        return False

    def move_next(self):
        if self.queue_pos < len(self._students):
            self.queue_pos += 1
            return True
        return False

    def move_to_index(self, position, desired_position):
        try:
            self._students.insert(desired_position, self._students.pop(position))
            return True
        except ValueError:
            return False

    def move_to_end(self, position):
        self._students.append(self._students.pop(position))

    def swap(self, position1, position2):
        self._students[position1], self._students[position2] = self._students[position2], self._students[position1]

    # if student registered as user, returns True, otherwise False
    def append(self, student: Student):
        self._students.append(student)

    def append_by_name(self, name):
        student = self.main_bot.registered_manager.get_user_by_name(name)
        if student is not None:
            self._students.append(student)
            return True
        else:
            self._students.append(self.main_bot.registered_manager.find_similar_student(name))
            return False
    def append_new(self, name, user_id):
        student = self.main_bot.registered_manager.get_user_by_id(user_id)
        if student is not None:
            self._students.append(student)
            return True
        else:
            new_user = self.main_bot.registered_manager.append_new_user(name, user_id)
            self._students.append(new_user)
            return False

    def set_students(self, students):
        self._students = students

    def clear(self):
        self._students = []
        self.queue_pos = 0

    def remove_by_index(self, index):
        if isinstance(index, int):
            self._students.pop(index)
            self.adjust_queue_position(index)
        else:
            to_delete = []
            for ind in index:
                to_delete.append(self._students[ind])

            for elem in to_delete:
                self.remove_by_id(elem.telegram_id)

    def remove_by_id(self, remove_id):
        for remove_index in range(len(self._students)):
            if self._students[remove_index].telegram_id == remove_id:
                self._students.pop(remove_index)
                self.adjust_queue_position(remove_index)
                break

    def remove_by_object(self, student):
        for remove_index in range(len(self._students)):
            if self._students[remove_index] is student:
                self._students.pop(remove_index)
                self.adjust_queue_position(remove_index)
                break

    # if we delete element, that is before current queue position,
    # it will shift queue forward by one position
    def adjust_queue_position(self, deleted_pos):
        if deleted_pos < self.queue_pos:
            self.queue_pos -= 1

    def get_current(self) -> Student:
        if 0 <= self.queue_pos < len(self):
            return self._students[self.queue_pos]
        else:
            return Student_EMPTY

    def get_last(self):
        if len(self) > 0:
            return self._students[-1]
        return Student_EMPTY

    def str(self):
        if len(self._students) > 0:
            if self.queue_pos is not None:
                str_list = []

                cur_item, next_item = self.get_cur_and_next()
                if cur_item is None:
                    return self.get_language_pack().queue_finished

                str_list.append('Сдает:')
                str_list.append(self._students[self.queue_pos].str(self.queue_pos + 1))
                str_list.append('\nСледующий:')
                if next_item is not None:
                    str_list.append(self._students[self.queue_pos + 1].str(self.queue_pos + 2))
                else:
                    str_list.append('Нет')

                if (self.queue_pos + 2) < len(self._students):
                    str_list.append('\nОставшиеся:')
                    for i in range(self.queue_pos + 2, len(self._students)):
                        str_list.append(self._students[i].str(i + 1))

                return '\n'.join(str_list) + '\n\n' + self.get_language_pack().queue_commands
            else:
                return 'Очередь:\n' + '\n'.join([self._students[i].str(i) for i in range(len(self._students))])

        return self.get_language_pack().queue_finished

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
            msg = 'Сдает - {0}'.format(cur_stud.str())

        if next_stud is not None:
            msg += '\nГотовится - {0}'.format(next_stud.str())

        return msg if msg != '' else self.get_language_pack().queue_finished

    # find students
    def parse_students(self, students_str):
        if '\n' in students_str:
            names = students_str.split('\n')
        else:
            names = [students_str]

        students = []
        for name in names:
            user = self.main_bot.registered_manager.get_user_by_name(name)
            if user is None:
                students.append(self.main_bot.registered_manager.find_similar_student(name))
            else:
                students.append(user)
        return students

    def parse_positions_list(self, string, max_index=None):
        if max_index is None:
            max_index = len(self._students)

        if ' ' in string:
            index_str = string.split(' ')
        else:
            index_str = [string]

        err_list = []
        correct_indexes = []

        for pos_str in index_str:
            try:
                position = int(pos_str)
                if 0 < position <= max_index:
                    correct_indexes.append(position)
                else:
                    err_list.append(pos_str)
            except ValueError:
                err_list.append(pos_str)

        return correct_indexes, err_list

    def generate_simple(self, students=None):
        if students is None:
            self._students = self.main_bot.registered_manager.get_users()
        else:
            self._students = students

    def generate_random(self, students=None):
        if students is None:
            students = self.main_bot.registered_manager.get_users()
            rnd.shuffle(students)
            self._students = students
        else:
            rnd.shuffle(students)
            self._students = students

    def load_file(self, saver):
        self._students = saver.load(self._file_queue)
        if self._students is None:
            self._students = []

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

    def remove(self, student: Student):
        if student in self._students:
            self._students.remove(student)
        else:
            return self.get_language_pack().student_not_found.format(student.log_str())
