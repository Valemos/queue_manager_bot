from sqlalchemy import Column, Integer, ForeignKey, String

from queue_bot.database import Base


class QueueMember(Base):
    __tablename__ = 'queue_member'

    queue_id = Column(Integer, ForeignKey('queue.id'), primary_key=True)
    name = Column(String, primary_key=True)
    position = Column(Integer)

    def __init__(self, queue_id, name, position):
        self.queue_id = queue_id
        self.name = name
        self.position = position
