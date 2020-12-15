import random as rnd
from pathlib import Path

from queue_bot.student import Student, EmptyStudent
from queue_bot.misc.object_file_saver import FolderType
from queue_bot.savable_interface import Savable


class StudentsQueue(Savable):

    queue_pos = 0
    students = []

    save_folder = FolderType.QueuesData.value

    file_format_queue = 'queue_{0}.data'
    file_format_queue_state = 'state_{0}.data'

    copy_queue_format = '/new_queue {name}\n{students}'

    def __init__(self, bot, name=None, students=None):
        self.name = name if name is not None else bot.language_pack.default_queue_name
        self.main_bot = bot
        self.students = students if students is not None else []

    def __len__(self):
        if self.students is None:
            return 0
        return len(self.students)

    def __contains__(self, item):
        if isinstance(item, Student):
            return item in self.students
        elif isinstance(item, int):
            for student in self.students:
                if student.telegram_id == item:
                    return True
        return False

    def __str__(self):
        return self.name + ' : ' + str(len(self.students))

    def str(self):
        if len(self.students) > 0 and self.queue_pos is not None:

            cur_stud, next_stud = self.get_cur_and_next()
            if cur_stud is None:
                return self.main_bot.language_pack.queue_finished_select_other.format(self.name)
            else:
                cur_stud = cur_stud.str(self.queue_pos + 1)

            if next_stud is not None:
                next_stud = next_stud.str(self.queue_pos + 2)
            else:
                next_stud = 'Нет'

            if (self.queue_pos + 2) < len(self.students):
                other_studs = '\n'.join([self.students[i].str(i + 1)
                                         for i in range(self.queue_pos + 2, len(self.students))])
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
            return self.main_bot.language_pack.queue_finished_select_other.format(self.name)

    def str_simple(self):
        queue_name = (self.name + '\n\n') if self.name != '' else ''
        students_str = [self.students[i].str() for i in range(len(self.students))]
        return self.main_bot.language_pack.queue_simple_format.format(name=queue_name,
                                                                      students='\n'.join(students_str))

    def get_str_for_copy(self):
        students_str = [self.students[i].str() for i in range(len(self.students))]
        return self.copy_queue_format.format(name=self.name, students='\n'.join(students_str))

    def move_prev(self):
        if self.queue_pos > 0:
            self.queue_pos -= 1
            return True
        return False

    def move_next(self):
        if self.queue_pos < len(self.students):
            self.queue_pos += 1
            return True
        return False

    def move_to_index(self, position, desired_position):
        try:
            # todo: fix insert to first position
            self.students.insert(desired_position, self.students.pop(position))
            return True
        except ValueError:
            return False

    def move_to_end(self, student):
        if student in self.students:
            self.students.append(self.students.pop(self.students.index(student)))
            return True
        else:
            return False

    def swap_students(self, stud1, stud2):
        pos1 = self.students.index(stud1)
        pos2 = self.students.index(stud2)
        self.students[pos1], self.students[pos2] = self.students[pos2], self.students[pos1]

    def append_by_name(self, name):
        student = self.main_bot.registered_manager.get_user_by_name(name)
        if student is not None:
            self.students.append(student)
            return True
        else:
            self.students.append(self.main_bot.registered_manager.find_similar_student(name))
            return False

    def append_to_queue(self, student):
        if student in self.students:
            self.students.remove(student)

        if student is not None:
            self.students.append(student)
            return True
        else:
            new_user = self.main_bot.registered_manager.append_users(student)
            self.students.append(new_user)
            return False

    def set_students(self, students):
        self.students = list(students)

    def clear(self):
        self.students = []
        self.queue_pos = 0

    def remove_student(self, student):
        if student.telegram_id is not None:
            self.remove_by_id(student.telegram_id)
        else:
            self.remove_by_name(student.name)

    def remove_by_index(self, index):
        if isinstance(index, int):
            self.students.pop(index)
            self.adjust_queue_position(index)
        else:
            to_delete = []
            for ind in index:
                to_delete.append(self.students[ind])

            for elem in to_delete:
                self.remove_by_id(elem.telegram_id)

    def remove_by_id(self, remove_id):
        for remove_index in range(len(self.students)):
            if self.students[remove_index].telegram_id == remove_id:
                self.students.pop(remove_index)
                self.adjust_queue_position(remove_index)
                break

    def remove_by_name(self, student_name):
        for remove_index in range(len(self.students)):
            if self.students[remove_index].telegram_id is None:
                if self.students[remove_index].name == student_name:
                    self.students.pop(remove_index)
                    self.adjust_queue_position(remove_index)
                    break

    # if we delete element, that is before current queue position,
    # it will shift queue forward by one position
    def adjust_queue_position(self, deleted_pos):
        if deleted_pos < self.queue_pos:
            self.queue_pos -= 1

    def get_position(self):
        return self.queue_pos

    def get_student_position(self, student):
        for i in range(len(self.students)):
            if student == self.students[i]:
                return i
        return None

    def set_student_position(self, student, new_position):
        prev_position = self.get_student_position(student)
        if prev_position is None:
            return False
        return self.move_to_index(prev_position, new_position)

    def set_position(self, position):
        self.queue_pos = position

    def get_current(self):
        if 0 <= self.queue_pos < len(self):
            return self.students[self.queue_pos]
        else:
            return EmptyStudent

    def get_last(self):
        if len(self) > 0:
            return self.students[-1]
        return None

    def get_names_with_positions(self):
        names = []
        for i in range(len(self.students)):
            names.append(self.students[i].str(i))
        return names

    def get_student_identifiers(self):
        names = []
        for i in range(len(self.students)):
            names.append(self.students[i].str(i))
        return names

    def get_cur_and_next(self):
        if 0 <= self.queue_pos < len(self.students) - 1:
            return self.students[self.queue_pos], self.students[self.queue_pos + 1]
        elif self.queue_pos == len(self.students) - 1:
            return self.students[self.queue_pos], None
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
        return self.main_bot.keyboards.generate_keyboard(
            command,
            [s.name for s in self.students],
            [s.str_name_id() for s in self.students])

    def get_students_keyboard_with_position(self, command):
        return self.main_bot.keyboards.generate_keyboard(
            command,
            [self.students[i].str(i + 1) for i in range(len(self.students))],
            [s.str_name_id() for s in self.students])

    def generate_simple(self, students=None):
        if students is None:
            self.students = self.main_bot.registered_manager.get_users()
        else:
            self.students = students

    def generate_random(self, students=None):
        if students is None:
            students = self.main_bot.registered_manager.get_users()
            rnd.shuffle(students)
            self.students = students
        else:
            rnd.shuffle(students)
            self.students = students

    def get_state_save_file(self):
        return self.save_folder / Path(self.file_format_queue_state.format(self.name))

    def get_queue_save_file(self):
        return self.save_folder / Path(self.file_format_queue.format(self.name))

    def get_save_files(self):
        return [self.get_state_save_file(), self.get_queue_save_file()]

    def get_save_file_formats(self):
        return [self.file_format_queue, self.file_format_queue_state]

    def save_to_file(self, saver):
        state = {'_queue_pos': self.queue_pos}
        saver.save(state, self.get_state_save_file())
        saver.save(self.students, self.get_queue_save_file())

    def load_file(self, saver):
        self.students = saver.load(self.get_queue_save_file())
        state = saver.load(self.get_state_save_file())
        self.queue_pos = state['_queue_pos']
