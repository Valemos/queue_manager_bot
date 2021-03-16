from queue_bot.bot.access_levels import AccessLevel
from queue_bot.database import Base, db_session, init_database

from sqlalchemy import Column, String, Integer, Enum


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    access_level = Column(Enum(AccessLevel))

    # initialized in queue_students_table
    queues = None

    def __init__(self, name, telegram_id):
        self.id = telegram_id
        self.name = name
        self.access_level = AccessLevel.USER

    def __eq__(self, other):
        if not isinstance(other, Student):
            return False

        if self.id is not None and other.id is not None:
            return self.id == other.id
        elif self.id is None and other.id is None:
            # if both are None
            return self.name == other.name
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name_id_str()

    def __hash__(self):
        return hash(self.name) + (0 if self.id is None else self.id) * (2 << 64)

    def str(self, position=None):
        if position is None:
            return self.name
        else:
            return f"{position} - {self.name}"

    # to get student back used function in queue_bot.bot_parsers.parse_student
    def code_str(self):
        if self.id is None:
            return str(None) + self.name
        else:
            return '{:0>8}'.format(hex(self.id)[2:]) + self.name

    def name_id_str(self):
        return f"{self.name}: {self.id}"


EmptyStudent = Student('Пусто', None)


if __name__ == '__main__':
    init_database()

    session = db_session()
    session.add(Student("Dmytro", 228))
    session.commit()

    for student in session.query(Student).all():
        print(student)
