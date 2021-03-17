from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from queue_bot.database import Base


class QueueStudentOrdered(Base):
    __tablename__ = 'queue_student'

    queue_id = Column(Integer, ForeignKey('queue.id'), primary_key=True)
    student_id = Column(Integer, ForeignKey('student.id'), primary_key=True)
    position = Column(Integer, nullable=False)

    student = relationship("Student")

    def __init__(self, queue_id, student_id, position):
        self.queue_id = queue_id
        self.student_id = student_id
        self.position = position

    def __str__(self):
        return f"{self.position}) q:{self.queue_id} s:{self.student.str()}"
