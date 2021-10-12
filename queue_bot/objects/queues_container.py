#  class relies on unique names, and is not suitable for multiple chats

import queue_bot.languages.bot_messages_rus as language_pack
from queue_bot.bot import keyboards
from queue_bot.database import db_session
from queue_bot.objects.queue_students import QueueStudents


class QueuesContainer:

    queues_count_limit = 10
    queues = {}
    selected_queue = None

    def __init__(self, queues: list = None):
        if queues is None:
            self.queues = self.load_all_queues()
        else:
            self.queues = {queue.name: queue for queue in queues}

    def __len__(self):
        return len(self.queues)

    def __contains__(self, item):
        return item in self.queues

    @staticmethod
    def load_all_queues():
        session = db_session()
        queues = {}
        for queue in session.query(QueueStudents).all():
            queues[queue.name] = queue
        session.close()

        return queues

    def select_queue(self, name):
        if name in self.queues:
            self.selected_queue = self.queues[name]
            return True
        return False

    @staticmethod
    def is_name_valid(name):
        return len(name) <= 50

    def rename_queue(self, prev_name, new_name):
        if prev_name == new_name:
            # previous name is already equals to target name. Operation successful
            return True

        new_name = new_name if new_name is not None else language_pack.default_queue_name
        prev_name = prev_name if prev_name is not None else language_pack.default_queue_name

        if new_name in self.queues \
           or not self.is_name_valid(new_name) \
           or not self.is_name_valid(prev_name):
            # name is already taken or name is invalid
            return False

        if prev_name in self.queues:
            selected_name = self.get_queue_name()
            queue = self.queues[prev_name]

            session = db_session()
            queue.name = new_name
            session.commit()

            del self.queues[prev_name]
            self.queues[queue.name] = queue

            if selected_name == prev_name:
                self.select_queue(new_name)

            return True

    def create_queue(self, parameters):
        new_queue = QueueStudents(parameters)
        if self.add_queue(new_queue):
            return new_queue
        return None

    # handle queue limit
    def can_add_queue(self):
        return len(self.queues) < self.queues_count_limit

    def add_queue(self, queue):
        """
        Adds new queue object to dictionary
        :param queue: StudentsQueue object to add
        :return: True if queue add was successful
        """
        session = db_session()
        if self.can_add_queue():
            self.remove_queue(queue.name)  # to delete unreachable queue with the same name
            session.add(queue)
            self.queues[queue.name] = queue
            session.commit()
            return True

        session.close()
        return False

    def clear_current_queue(self):
        if self.selected_queue is not None:
            session = db_session()
            self.selected_queue.clear()
            session.commit()

    def remove_queue(self, name):
        if name in self.queues:
            session = db_session()
            session.delete(self.queues[name])
            del self.queues[name]
            session.commit()

            if len(self.queues) > 0:
                # update selected queue only if it was deleted
                if name == self.selected_queue.name:
                    self.selected_queue = list(self.queues.values())[0]
            else:
                self.selected_queue = None

            return True
        return False

    def clear_finished_queues(self):
        session = db_session()
        updated_queues = {}

        for name, queue in self.queues.items():
            if queue.is_finished():
                session.delete(queue)
            else:
                updated_queues[name] = queue

        self.queues = updated_queues
        session.commit()

    def get_queue_by_name(self, find_name):
        for name, queue in self.queues.items():
            if name == find_name:
                return queue
        return None

    def get_queue(self) -> QueueStudents:
        return self.selected_queue

    def get_queue_name(self):
        return self.selected_queue.name if self.selected_queue is not None else None

    def get_queue_str(self):
        if self.selected_queue is not None:
            return self.selected_queue.str()
        else:
            return language_pack.queue_not_selected

    def generate_keyboard(self, command):
        return keyboards.generate_keyboard(command, self.queues.keys())
