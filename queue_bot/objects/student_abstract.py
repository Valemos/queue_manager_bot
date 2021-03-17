from abc import ABCMeta, abstractmethod

from sqlalchemy import Integer, String, Column, Enum, PrimaryKeyConstraint, UniqueConstraint

from queue_bot.bot.access_levels import AccessLevel
from queue_bot.database import Base
from queue_bot.objects.student import Student


class AbstractStudent(Base, metaclass=ABCMeta):
    __tablename__ = "student"

    telegram_id = Column(Integer, nullable=True)
    name = Column(String(50), nullable=False)
    access_level = Column(Enum(AccessLevel))

    __table_args__ = (
        PrimaryKeyConstraint(
            telegram_id, name,
        ),
        UniqueConstraint(telegram_id)
    )

    def __init__(self, name, telegram_id):
        self.telegram_id = telegram_id
        self.name = name
        self.access_level = AccessLevel.USER

    def __eq__(self, other):
        if not isinstance(other, Student):
            return False

        if self.get_id() is not None and other.get_id() is not None:
            return self.get_id() == other.get_id()
        elif self.get_id() is None and other.get_id() is None:
            # if both are None
            return self.get_name() == other.get_name()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name_id_str()

    def __hash__(self):
        return hash(str(self.get_id()) + self.get_name())

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @classmethod
    def check_name(cls, name):
        return len(name) < 50

    def str(self, position=None):
        if position is None:
            return self.get_name()
        else:
            return f"{position} - {self.get_name()}"

    def code_str(self):
        if self.get_id() is None:
            return str(None) + self.get_name()
        else:
            return '{:0>8}'.format(hex(self.get_id())[2:]) + self.get_name()

    def name_id_str(self):
        return f"{self.get_name()}: {self.get_id()}"
