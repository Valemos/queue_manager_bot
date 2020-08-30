import random as rnd
from bot_messages import *
from registered_manager import RegisteredManager


class Student:

    def __init__(self, name, telegram_id):
        self._name = name
        self._telegram_id = telegram_id

    def get_id(self):
        return self._telegram_id

    def get_string(self, position=None):
        if position is None:
            return self._name
        else:
            return '{0} - {1}'.format(position, self._name)


class StudentsQueue:

    _students = []
    _queue_pos = 0
    students_manager = None

    def __init__(self, students_manager=None, students=None):
        if students_manager is None:
            self.students_manager = RegisteredManager()

        if students is None:
            students = []

        self._students = students

    def move_prev(self):
        if self._queue_pos > 0:
            self._queue_pos -= 1
            return True
        return False

    def move_next(self):
        if self._queue_pos < len(self._students):
            self._queue_pos -= 1
            return True
        return False

    def get_string(self):
        if len(self._students) > 0:
            if self._queue_pos is not None:

                str_list = []

                cur_item, next_item = self.get_cur_and_next()

                if cur_item is None:
                    return msg_queue_finished

                str_list.append('Сдает:')
                str_list.append(self._queue_pos)
                str_list.append('\nСледующий:')
                if next_item is not None:
                    str_list.append(self._students[self._queue_pos + 1].get_string(self._queue_pos + 1))
                else:
                    str_list.append('Нет')

                if (self._queue_pos + 2) < len(self._students):
                    str_list.append('\nОставшиеся:')
                    for i in range(self._queue_pos + 2, len(self._students)):
                        str_list.append(self._students[i].get_string(i))

                return '\n'.join(str_list) + '\n\n' + msg_queue_commands
            else:
                return 'Очередь:\n' + '\n'.join([self._students[i].get_string(i) for i in range(len(self._students))])

        return msg_queue_finished

    # Получить текущего и следующего человека в очереди
    def get_cur_and_next(self):
        if self._queue_pos < len(self._students) - 1 and self._queue_pos >= 0:
            return self._students[self._queue_pos], self._students[self._queue_pos + 1]
        elif self._queue_pos == len(self._students) - 1:
            return self._students[self._queue_pos], None

        return None, None

    def get_cur_and_next_str(self):
        msg = ''
        cur_stud, next_stud = self.get_cur_and_next()
        if cur_stud is not None:
            msg = 'Сдает - {0}'.format(cur_stud.get_string())

        if next_stud is not None:
            msg += '\nГотовится - {0}'.format(next_stud.get_string())

        return msg if msg != '' else msg_queue_finished

    def clear(self):
        pass
