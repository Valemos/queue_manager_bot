from typing import Optional

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from queue_bot.bot import keyboards
from queue_bot.database import Base, Session
from queue_bot.objects.queue import Queue
from queue_bot import language_pack


# todo finish persistence
class QueuesManager(Base):
    __tablename__ = 'queues_manager'

    chat_id = Column(Integer, primary_key=True)
    selected_id = Column(Integer)
    queues = relationship("Queue")

    queues_count_limit = 10

    def __init__(self, chat_id=None, queues: list = None):
        self.id = chat_id
        self.queues = queues

    def __len__(self):
        return len(self.queues)

    def __contains__(self, item):
        return item in self.queues

    def is_queue_selected(self):
        return self.selected_id is None

    def set_current_queue(self, name):
        queue = self.get_queue_or_none(name)
        if queue is not None:
            self.selected_id = queue.id

    def get_queue_or_none(self, name) -> Optional[Queue]:
        with Session.begin() as s:
            return s.query(Queue).filter_by(chat_id=self.chat_id, name=name)

    def rename_queue(self, prev_name, new_name):
        if new_name is None:
            new_name = language_pack.default_queue_name

        if prev_name is None:
            prev_name = language_pack.default_queue_name

        queue = self.get_queue_or_none(prev_name)
        queue.name = new_name

    @staticmethod
    def create_queue(*args):
        return Queue(*args)

    # handle queue limit
    def can_add_queue(self):
        return len(self.queues) < self.queues_count_limit

    def add_queue(self, queue):
        self.queues[queue.name] = queue
        self.selected_id = queue
        self.save_current_to_file()

    def clear_current_queue(self):
        if self.selected_id is not None:
            self.get_queue().clear()

    def remove_queue(self, name):
        if name in self.queues:
            self.delete_queue_files(self.queues[name])
            del self.queues[name]
            self.selected_id = None
        raise ValueError(f"No queue '{name}' found")

    def get_queue(self) -> Queue:
        with Session.begin() as session:
            return session.query(Queue).filter_by(id=self.selected_id).first()

    def get_queue_message(self):
        if self.selected_id is not None:
            return self.get_queue().description()
        else:
            return language_pack.queue_not_selected

    def generate_choice_keyboard(self, command):
        return keyboards.generate_keyboard(command, list(q.name for q in self.queues))

    def clear_finished_queues(self):
        # todo finish deleting queues
        pass


def get_chat_queues(chat_id) -> QueuesManager:
    with Session.begin() as session:
        queues = session.query(QueuesManager).filter_by(chat_id=chat_id).first()
        if queues is None:
            queues = QueuesManager(chat_id)
            session.add(queues)
        return queues
