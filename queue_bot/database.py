from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

_engine = create_engine('sqlite:///:memory:', echo=True)
db_session = sessionmaker(bind=_engine)


def init_database():
    init_relations()
    Base.metadata.create_all(_engine)


def reset_database():
    Base.metadata.drop_all(_engine)
    Base.metadata.create_all(_engine)


def init_relations():
    from queue_bot.objects.queue_students import QueueStudents
    from queue_bot.objects.student import Student
    from queue_bot.objects.queue_student_table import QueueStudentsJoin

    students_relation = relationship('Student',
                                     secondary=QueueStudentsJoin,
                                     viewonly=True,
                                     order_by=QueueStudentsJoin.position,
                                     back_populates="queues",
                                     lazy='joined')

    queues_relation = relationship('QueueStudents',
                                   secondary=QueueStudentsJoin,
                                   viewonly=True,
                                   back_populates="students",
                                   lazy=True)

    QueueStudents.students = students_relation
    Student.queues = queues_relation
