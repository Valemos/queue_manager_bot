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
    members = relationship("QueueMember", order_by="QueueMember.position")

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

    def description(self):
        if len(self.members) > 0 and self.current_position is not None:

            cur_stud, next_stud = self.get_cur_and_next()
            if cur_stud is None:
                return language_pack.queue_finished_select_other.format(self.name)
            else:
                cur_stud = cur_stud.description(self.current_position + 1)

            if next_stud is not None:
                next_stud = next_stud.description(self.current_position + 2)
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

    def get_member_names(self):
        return [self.members[i] for i in range(len(self.members))]

    def get_name(self):
        return self.name

    def move_prev(self):
        self.increment_position(-1)

    def move_next(self):
        self.increment_position(1)

    def increment_position(self, amount):
        with Session.begin() as session:
            session.add(self)
            if 0 < self.current_position < len(self.members) - 1:
                self.current_position += amount

    def move_to_index(self, position, desired_position):
        with Session.begin() as session:
            session.add(self)
            prev_member = self.members.pop(position)
            self.members.insert(desired_position, prev_member)
            self.update_positions()

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
            if student is None:
                student = registered.find_similar_student(name)

            self.set_last_member(student.name if student is not None else name)

    def append_info(self, info: QueueUserInfo):
        registered = get_chat_registered(self.chat_id).get_by_id(info.telegram_id)
        self.set_last_member(registered.name if registered is not None else info.name)

    def set_last_member(self, member_name):
        with Session.begin() as session:
            session.add(self)
            self.remove_by_name(member_name)
            self.members.append(QueueMember(self.id, member_name, len(self.members)))

    def set_students(self, students):
        with Session.begin() as session:
            session.add(self)
            for student in students:
                self.set_last_member(student.name)

    def clear(self):
        with Session.begin() as session:
            session.add(self)
            self.members = []
            self.current_position = 0

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

    def get_student_position(self, student_name):
        with Session() as session:
            session.add(self)
            for i, member in enumerate(self.members):
                if student_name == member.name:
                    return i
            return None

    def set_student_position(self, student, new_position):
        with Session() as session:
            session.add(self)
            prev_position = self.get_student_position(student)
            self.move_to_index(prev_position, new_position)

    def set_position(self, position):
        with Session() as session:
            session.add(self)
            self.current_position = position

    def get_current(self):
        with Session() as session:
            session.add(self)
            return self.members[self.current_position]

    def get_last(self):
        with Session() as session:
            session.add(self)
            if len(self) > 0:
                return self.members[-1]
            return None

    def get_names_with_positions(self):
        names = []
        for i in range(len(self.members)):
            names.append(self.members[i].str(i))
        return names

    def get_cur_and_next(self):
        with Session() as session:
            session.add(self)
            if 0 <= self.current_position < len(self.members) - 1:
                return self.members[self.current_position].name, \
                       self.members[self.current_position + 1].name
            elif self.current_position == len(self.members) - 1:
                return self.members[self.current_position].name, None
            return None, None

    def get_keyboard_with_position(self, command):
        with Session() as session:
            session.add(self)
            return keyboards.generate_keyboard(
                command,
                [self.members[i].str(i + 1) for i in range(len(self.members))],
                [s.str_name_id() for s in self.members])

    def generate_simple(self, students=None):
        if students is None:
            students = get_chat_registered(self.chat_id).get_users()

        for student in students:
            self.set_last_member(student.name)

    def generate_random(self, students=None):
        if students is None:
            students = get_chat_registered(self.chat_id).get_users()
            rnd.shuffle(students)
            self.members = students
        else:
            rnd.shuffle(students)
            self.members = students
