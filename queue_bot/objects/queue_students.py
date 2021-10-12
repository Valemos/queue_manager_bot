import random as rnd

from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.orm import relationship

import queue_bot.languages.bot_messages_rus as language_pack
from queue_bot.bot import keyboards
from queue_bot.database import Base, db_session
from .queue_parameters import QueueParameters
from .queue_students_join import QueueStudentOrdered
from .student import Student
from .student_abstract import AbstractStudent
from .student_factory import student_factory


class QueueStudents(Base):
    __tablename__ = "queue"

    id = Column(Integer, Sequence("queue_id_seq"), primary_key=True)
    name = Column(String(50))
    position = Column(Integer)

    # todo modify all accesses to self.stud_ordered
    stud_ordered = relationship(QueueStudentOrdered, order_by=QueueStudentOrdered.position, lazy='joined')

    @staticmethod
    def from_params(params: QueueParameters):
        queue = QueueStudents()
        queue.registered = params.registered
        queue.name = params.name
        queue.stud_ordered = queue.wrap_students(params.students)
        return queue

    def __len__(self):
        if self.stud_ordered is None:
            return 0
        return len(self)

    def __contains__(self, item):
        if isinstance(item, Student):
            return any(map(lambda wrapper: wrapper.student == item, self.stud_ordered))
        elif isinstance(item, int):
            return any(map(lambda wrapper: wrapper.student_id == item, self.stud_ordered))
        return False

    def __str__(self):
        return self.name + ' : ' + str(len(self))

    def str(self):
        if len(self) > 0 and self.position is not None:

            cur_stud, next_stud = self.get_cur_and_next()
            if cur_stud is None:
                return language_pack.queue_finished_select_other.format(self.name)
            else:
                cur_stud = cur_stud.str(self.position + 1)

            if next_stud is not None:
                next_stud = next_stud.str(self.position + 2)
            else:
                next_stud = 'Нет'

            if (self.position + 2) < len(self):
                other_studs = '\n'.join([self.get_student_at(i).str(i + 1)
                                         for i in range(self.position + 2, len(self))])
            else:
                other_studs = ''

            # name must be specified with '\n'
            # because telegram trims first characters if they are '\n'
            queue_name = self.name + '\n\n' if self.name != '' else ''
            return language_pack.queue_format.format(name=queue_name,
                                                     current=cur_stud,
                                                     next=next_stud,
                                                     other=other_studs)
        else:
            return language_pack.queue_finished_select_other.format(self.name)

    def str_simple(self):
        queue_name = (self.name + '\n\n') if self.name != '' else ''
        students_str = [self.get_student_at(i).str() for i in range(len(self))]
        return language_pack.queue_simple_format.format(name=queue_name,
                                                        students='\n'.join(students_str))

    def get_str_for_copy(self):
        students_str = [self.get_student_at(i).str() for i in range(len(self))]
        return language_pack.copy_queue_format.format(name=self.name, students='\n'.join(students_str))

    def move_prev(self):
        if self.position > 0:
            self.increment_position(-1)
            return True
        return False

    def move_next(self):
        if self.position < len(self):
            self.increment_position(1)
            return True
        return False

    def increment_position(self, increment):
        session = db_session()
        # must use this form of increment to produce SQL statement
        self.position = self.position + increment
        session.commit()

    def move_to_index(self, position, desired_position):
        try:
            student_moving = self.stud_ordered.pop(position)
            self.stud_ordered.insert(desired_position, student_moving)
            self.update_positions(position, desired_position)
            return True
        except ValueError:
            return False

    def move_to_end(self, student):
        if student in self.stud_ordered:
            session = db_session()
            student_position = self.stud_ordered.pop(self.index_of(student))
            self.stud_ordered.append(student_position)
            session.commit()
            return True
        else:
            return False

    def swap_students(self, stud1, stud2):
        index1 = self.index_of(stud1)
        index2 = self.index_of(stud2)

        pos1 = self.stud_ordered[index1]
        pos2 = self.stud_ordered[index2]

        session = db_session()
        pos1.position, pos2.position = pos2.position, pos1.position
        self.stud_ordered[index1] = pos2
        self.stud_ordered[index2] = pos1
        session.commit()

    def append_by_name(self, name):
        student = self.registered.get_user_by_name(name)
        if student is None:
            student = self.registered.find_similar_student(name)

        self.append(student)
        return student

    def append(self, student):
        if student is not None:
            # if student exists in queue, delete him by id
            session = db_session()
            self.remove_by_id(student)
            self.stud_ordered.append(QueueStudentOrdered(self.id, student.get_id(), len(self)))
            session.commit()
            return True
        else:
            # todo finish refactoring self.stud_ordered usages
            new_user = self.registered.append_users(student)
            session = db_session()
            self.stud_ordered.append(new_user)
            session.commit()
            return False

    def set_students(self, students: list):
        s = db_session()
        self.stud_ordered = self.wrap_students(students)
        s.commit()

    def clear(self):
        # todo rewrite this with database connection
        self.stud_ordered = []
        self.position = 0

    def remove_student(self, student):
        if student.get_id() is not None:
            self.remove_by_id(student.telegram_id)
        else:
            self.remove_by_name(student.name)

    def remove_by_index(self, index):
        session = db_session()
        self.stud_ordered.pop(index)
        self.adjust_queue_position(index)
        session.commit()

    def remove_by_id(self, remove_id):
        for remove_index in range(len(self)):
            if self.get_student_at(remove_index).telegram_id == remove_id:
                self.remove_by_index(remove_index)
                break

    def remove_by_name(self, student_name):
        """this function should be used only for users with no id"""
        for remove_index in range(len(self)):
            if self.get_student_at(remove_index).name == student_name:
                self.remove_by_index(remove_index)
                break

    def adjust_queue_position(self, deleted_pos):
        """
        if we delete element, that is before current queue position,
        it will shift queue forward by one position
        """
        if deleted_pos < self.position:
            self.position -= 1

    def get_position(self):
        return self.position

    def is_finished(self):
        return self.position >= len(self)

    def get_student_position(self, student):
        for i in range(len(self)):
            if student == self.get_student_at(i):
                return i
        return None

    def set_student_position(self, student, new_position):
        prev_position = self.get_student_position(student)
        if prev_position is None:
            return False
        return self.move_to_index(prev_position, new_position)

    def set_position(self, position):
        session = db_session()
        self.position = position
        session.commit()

    def get_student_at(self, index) -> AbstractStudent:
        return self.stud_ordered[index].student

    def get_current(self) -> AbstractStudent:
        if 0 <= self.position < len(self):
            return self.get_student_at(self.position)
        else:
            return student_factory("Пусто")

    def get_last(self):
        if len(self) > 0:
            return self.get_student_at(-1)
        return None

    def get_cur_and_next(self):
        if 0 <= self.position < len(self) - 1:
            return self.get_student_at(self.position), self.get_student_at(self.position + 1)
        elif self.position == len(self) - 1:
            return self.get_student_at(self.position), None
        return None, None

    # get string format of result of get_cur_and_next() call
    def get_cur_and_next_str(self):
        msg = ''
        cur_stud, next_stud = self.get_cur_and_next()
        if cur_stud is not None:
            msg = 'Сдает - {0}'.format(cur_stud.str())

        if next_stud is not None:
            msg += '\nГотовится - {0}'.format(next_stud.str())

        return msg if msg != '' else language_pack.queue_finished

    def get_keyboard(self, command):
        return keyboards.generate_keyboard(
            command,
            [student.name for student in self.iter_students()],
            [student.code_str() for student in self.iter_students()])

    def get_keyboard_with_position(self, command):
        return keyboards.generate_keyboard(
            command,
            [student.str(i + 1) for i, student in enumerate(self.iter_students())],
            [student.code_str() for student in self.iter_students()])

    def generate_simple(self, students_init=None):
        session = db_session()
        if students_init is None:
            self.stud_ordered = self.registered.get_users()
        else:
            self.stud_ordered = students_init
        session.commit()

    def generate_random(self, students_init=None):
        session = db_session()
        if students_init is None:
            students_init = self.registered.get_users()
            rnd.shuffle(students_init)
            self.stud_ordered = students_init
        else:
            rnd.shuffle(students_init)
            self.stud_ordered = students_init
        session.commit()

    def generate(self, students, is_random: bool):
        if is_random:
            self.generate_random(students)
        else:
            self.generate_simple(students)

    def wrap_students(self, students):
        """
        Needed to wrap every Student object with corresponding QueueStudentOrdered object
        to correctly handle students <-> queue relation in database
        """
        return [QueueStudentOrdered(self.id, student.get_id(), pos) for pos, student in enumerate(students)]

    def update_positions(self, start, end):
        """Updates all positions in wrappers between :start: and :end: and commit changes to database"""
        # todo test correct indices
        if start > end:
            start, end = end, start
        s = db_session()
        for i in range(start, end + 1):
            self.stud_ordered[i].position = i
        s.commit()

    def index_of(self, student):
        for student_pos_iter in self.stud_ordered:
            if student_pos_iter.student == student:
                return student_pos_iter.position

    def iter_students(self):
        for student_pos in self.stud_ordered:
            yield student_pos.student
