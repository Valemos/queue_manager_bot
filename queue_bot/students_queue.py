import random as rnd
from pathlib import Path

from queue_bot.student import Student, EmptyStudent
from queue_bot.object_file_saver import FolderType
from queue_bot.savable_interface import Savable


class StudentsQueue(Savable):

    name = ''

    _queue_pos = 0
    _students = []

    file_format_queue = 'queue_{0}.data'
    file_format_queue_state = 'state_{0}.data'

    copy_queue_format = '/new_queue {name}\n\n{students}'

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
            return item in self._students
        elif isinstance(item, int):
            for student in self._students:
                if student.telegram_id == item:
                    return True
        return False

    def __str__(self):
        return self.name + ' : ' + str(len(self._students))

    def move_prev(self):
        if self._queue_pos > 0:
            self._queue_pos -= 1
            return True
        return False

    def move_next(self):
        if self._queue_pos < len(self._students):
            self._queue_pos += 1
            return True
        return False

    def move_to_index(self, position, desired_position):
        try:
            self._students.insert(desired_position, self._students.pop(position))
            return True
        except ValueError:
            return False

    def move_to_end(self, student):
        if student in self._students:
            self._students.append(self._students.pop(self._students.index(student)))
            return True
        else:
            return False

    def swap(self, position1, position2):
        self._students[position1], self._students[position2] = self._students[position2], self._students[position1]

    def append_by_name(self, name):
        student = self.main_bot.registered_manager.get_user_by_name(name)
        if student is not None:
            self._students.append(student)
            return True
        else:
            self._students.append(self.main_bot.registered_manager.find_similar_student(name))
            return False

    def append_to_queue(self, student):
        if student in self._students:
            self._students.remove(student)

        if student is not None:
            self._students.append(student)
            return True
        else:
            new_user = self.main_bot.registered_manager.append_users(student)
            self._students.append(new_user)
            return False

    def set_students(self, students):
        self._students = list(students)

    def clear(self):
        self._students = []
        self._queue_pos = 0

    def remove_student(self, student):
        if student.telegram_id is not None:
            self.remove_by_id(student.telegram_id)
        else:
            self.remove_by_name(student.name)

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

    def remove_by_name(self, student_name):
        for remove_index in range(len(self._students)):
            if self._students[remove_index].telegram_id is None:
                if self._students[remove_index].name == student_name:
                    self._students.pop(remove_index)
                    self.adjust_queue_position(remove_index)
                    break

    # if we delete element, that is before current queue position,
    # it will shift queue forward by one position
    def adjust_queue_position(self, deleted_pos):
        if deleted_pos < self._queue_pos:
            self._queue_pos -= 1

    def get_position(self):
        return self._queue_pos

    def set_position(self, position):
        self._queue_pos = position

    def get_current(self):
        if 0 <= self._queue_pos < len(self):
            return self._students[self._queue_pos]
        else:
            return EmptyStudent

    def get_last(self):
        if len(self) > 0:
            return self._students[-1]
        return None

    def get_names_with_positions(self):
        names = []
        for i in range(len(self._students)):
            names.append(self._students[i].str(i))
        return names

    def get_student_identifiers(self):
        names = []
        for i in range(len(self._students)):
            names.append(self._students[i].str(i))
        return names

    def str(self):
        if len(self._students) > 0 and self._queue_pos is not None:

            cur_stud, next_stud = self.get_cur_and_next()
            if cur_stud is None:
                return self.main_bot.language_pack.queue_finished
            else:
                cur_stud = cur_stud.str(self._queue_pos + 1)

            if next_stud is not None:
                next_stud = next_stud.str(self._queue_pos + 2)
            else:
                next_stud = 'Нет'

            if (self._queue_pos + 2) < len(self._students):
                other_studs = '\n'.join([self._students[i].str(i + 1)
                                         for i in range(self._queue_pos + 2, len(self._students))])
            else:
                other_studs = ''

            # name must be specified with '\n'
            # because telegram trims first characters if they are '\n'
            queue_name = self.name + '\n\n' if self.name != '' else ''
            return self.main_bot.language_pack.queue_format.format(name=queue_name,
                                                                   current=cur_stud,
                                                                   next=next_stud,
                                                                   other=other_studs)
        else:
            return self.main_bot.language_pack.queue_finished

    def str_simple(self):
        queue_name = (self.name + '\n\n') if self.name != '' else ''
        students_str = [self._students[i].str() for i in range(len(self._students))]
        return self.main_bot.language_pack.queue_simple_format.format(name=queue_name,
                                                                      students='\n'.join(students_str))

    def get_str_for_copy(self):
        students_str = [self._students[i].str() for i in range(len(self._students))]
        return self.copy_queue_format.format(name=self.name, students='\n'.join(students_str))

    def get_cur_and_next(self):
        if 0 <= self._queue_pos < len(self._students) - 1:
            return self._students[self._queue_pos], self._students[self._queue_pos + 1]
        elif self._queue_pos == len(self._students) - 1:
            return self._students[self._queue_pos], None
        return None, None

    # get string format of result of get_cur_and_next() call
    def get_cur_and_next_str(self):
        msg = ''
        cur_stud, next_stud = self.get_cur_and_next()
        if cur_stud is not None:
            msg = 'Сдает - {0}'.format(cur_stud.str())

        if next_stud is not None:
            msg += '\nГотовится - {0}'.format(next_stud.str())

        return msg if msg != '' else self.main_bot.language_pack.queue_finished

    def get_students_keyboard(self, command):
        return self.main_bot.keyboards.generate_keyboard(command,
                                                         [s.name for s in self._students],
                                                         [s.str_name_id() for s in self._students])

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

    def get_state_save_file(self):
        return FolderType.QueuesData.value / Path(self.file_format_queue_state.format(self.name))

    def get_queue_save_file(self):
        return FolderType.QueuesData.value / Path(self.file_format_queue.format(self.name))

    def get_save_files(self):
        return [self.get_state_save_file(), self.get_queue_save_file()]

    def save_to_file(self, saver):
        state = {'_queue_pos': self._queue_pos}
        saver.save(state, self.get_state_save_file())
        saver.save(self._students, self.get_queue_save_file())

    def load_file(self, saver):
        self._students = saver.load(self.get_queue_save_file())
        state = saver.load(self.get_state_save_file())
        self._queue_pos = state['_queue_pos']
