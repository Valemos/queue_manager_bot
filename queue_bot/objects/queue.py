import random as rnd
from pathlib import Path

from sqlalchemy import Column, Integer, ForeignKey, delete, String
from sqlalchemy.orm import relationship

from queue_bot import language_pack
from queue_bot.bot import keyboards
from queue_bot.database import Base, Session
from .queue_user_info import QueueUserInfo
from .registered_manager import get_chat_registered
from .queue_member import QueueMember
from .student import Student


# todo finish persistence
class Queue(Base):
    __tablename__ = 'queue'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    chat_id = Column(Integer, ForeignKey('queues_manager.chat_id'))
    current_position = Column(Integer)
    members = relationship("QueueMember")

    def __init__(self, name=None, position=0):
        self.name = name if name is not None else language_pack.default_queue_name
        self.members: list[QueueMember] = []
        self.current_position = position

    def __len__(self):
        if self.members is None:
            return 0
        return len(self.members)

    def __contains__(self, item):
        if isinstance(item, Student):
            return item in self.members
        elif isinstance(item, int):
            for student in self.members:
                if student.telegram_id == item:
                    return True
        return False

    def __str__(self):
        return self.name + ' : ' + str(len(self.members))

    def str(self):
        if len(self.members) > 0 and self.current_position is not None:

            cur_stud, next_stud = self.get_cur_and_next()
            if cur_stud is None:
                return language_pack.queue_finished_select_other.format(self.name)
            else:
                cur_stud = cur_stud.str(self.current_position + 1)

            if next_stud is not None:
                next_stud = next_stud.str(self.current_position + 2)
            else:
                next_stud = 'Нет'

            if (self.current_position + 2) < len(self.members):
                other_studs = '\n'.join([self.members[i].str(i + 1)
                                         for i in range(self.current_position + 2, len(self.members))])
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
        students_str = [self.members[i].str() for i in range(len(self.members))]
        return language_pack.queue_simple_format.format(name=queue_name,
                                                                      students='\n'.join(students_str))

    def get_str_for_copy(self):
        students_str = [self.members[i].str() for i in range(len(self.members))]
        return self.copy_queue_format.format(name=self.name, students='\n'.join(students_str))

    def move_prev(self):
        with Session.begin() as session:
            if self.current_position > 0:
                self.current_position -= 1
            else:
                self.current_position = 0
            session.add(self)

    def move_next(self):
        with Session.begin() as session:
            if self.current_position < len(self.members):
                self.current_position += 1
            else:
                self.current_position = len(self.members) - 1
            session.add(self)

    def move_to_index(self, position, desired_position):
        with Session.begin() as session:
            prev_member = self.members.pop(position)
            self.members.insert(desired_position, prev_member)
            session.add(self)

    def move_to_end(self, student):
        with Session.begin() as session:
            session.add(self)
            if student in self.members:
                self.members.append(self.members.pop(self.members.index(student)))
                self.update_positions()

    def swap_students(self, stud1, stud2):
        with Session.begin() as session:
            session.add(self)
            pos1 = self.members.index(stud1)
            pos2 = self.members.index(stud2)
            self.members[pos1], self.members[pos2] = self.members[pos2], self.members[pos1]
            self.members[pos1].position = pos1 + 1
            self.members[pos2].position = pos2 + 1

    def append_by_name(self, name):
        with Session.begin() as session:
            session.add(self)
            registered = get_chat_registered(self.chat_id)
            session.add(registered)
            student = registered.get_by_name(name)
            if student is not None:
                self.members.append(student)
            else:
                self.members.append(registered.find_similar_student(name))

    def append_member(self, info: QueueUserInfo):
        self.remove_by_name(info.name)

        registered = get_chat_registered(self.chat_id).get_by_id(info.telegram_id)
        if registered is not None:
            self.set_last_member(registered.name)
        else:
            self.set_last_member(info.name)

    def set_last_member(self, member_name):
        with Session.begin() as session:
            session.add(self)
            self.members.append(QueueMember(self.id, member_name, len(self.members)))

    def set_students(self, students):
        with Session.begin() as s:
            for student in students:
                self.set_last_member(student.name)
            s.add(self)

    def clear(self):
        with Session.begin() as session:
            self.members = []
            self.current_position = 0
            session.add(self)

    def remove_student(self, student):
        if student.telegram_id is not None:
            self.remove_by_id(student.telegram_id)
        else:
            self.remove_by_name(student.name)

    def remove_by_index(self, index):
        if isinstance(index, int):
            self.pop_member(index)
        else:
            to_delete = []
            for ind in index:
                to_delete.append(self.members[ind])

            for elem in to_delete:
                self.remove_by_id(elem.telegram_id)

    def remove_by_id(self, remove_id):
        with Session.begin() as session:
            registered = get_chat_registered(self.chat_id).get_by_id(remove_id)
            if registered is None: return

            query = delete(QueueMember).where(QueueMember.queue_id == self.id and
                                              QueueMember.name == registered.name)
            session.execute(query)

    def remove_by_name(self, student_name):
        for remove_index in range(len(self.members)):
            if self.members[remove_index].telegram_id is None:
                if self.members[remove_index].name == student_name:
                    self.pop_member(remove_index)
                    break

    def pop_member(self, index):
        self.members.pop(index)

        self.adjust_position(index)

    def adjust_position(self, index):
        # if we delete element, that is before current queue position,
        # it will shift queue forward by one position
        if index < self.current_position:
            self.current_position -= 1

    def update_positions(self):
        with Session.begin() as s:
            s.add(self)
            for i, member in enumerate(self.members, start=1):
                member.position = i

    def get_position(self):
        return self.current_position

    def get_student_position(self, student):
        for i in range(len(self.members)):
            if student == self.members[i]:
                return i
        return None

    def set_student_position(self, student, new_position):
        prev_position = self.get_student_position(student)
        self.move_to_index(prev_position, new_position)

    def set_position(self, position):
        self.current_position = position

    def get_current(self):
        return self.members[self.current_position]

    def get_last(self):
        if len(self) > 0:
            return self.members[-1]
        return None

    def get_names_with_positions(self):
        names = []
        for i in range(len(self.members)):
            names.append(self.members[i].str(i))
        return names

    def get_student_identifiers(self):
        names = []
        for i in range(len(self.members)):
            names.append(self.members[i].str(i))
        return names

    def get_cur_and_next(self):
        if 0 <= self.current_position < len(self.members) - 1:
            return self.members[self.current_position], self.members[self.current_position + 1]
        elif self.current_position == len(self.members) - 1:
            return self.members[self.current_position], None
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

    def get_students_keyboard(self, command):
        return keyboards.generate_keyboard(
            command,
            [s.name for s in self.members],
            [s.str_name_id() for s in self.members])

    def get_keyboard_with_position(self, command):
        return keyboards.generate_keyboard(
            command,
            [self.members[i].str(i + 1) for i in range(len(self.members))],
            [s.str_name_id() for s in self.members])

    def generate_simple(self, students=None):
        if students is None:
            self.members = get_chat_registered(self.chat_id).get_users()
        else:
            self.members = students

    def generate_random(self, students=None):
        if students is None:
            students = get_chat_registered(self.chat_id).get_users()
            rnd.shuffle(students)
            self.members = students
        else:
            rnd.shuffle(students)
            self.members = students
