#  class relies on unique names, and is not suitable for multiple chats

from queue_bot.bot import keyboards
from queue_bot.objects.queue_students import QueueStudents
import queue_bot.languages.bot_messages_rus as language_pack


class QueuesContainer:

    queues_count_limit = 10
    queues = {}
    selected_queue = None

    def __init__(self, queues: list = None):
        if queues is None:
            self.queues = {}
        else:
            self.queues = {queue.name: queue for queue in queues}

    def __len__(self):
        return len(self.queues)

    def __contains__(self, item):
        return item in self.queues

    def set_current_queue(self, name):
        if name in self.queues:
            self.selected_queue = self.queues[name]
            return True
        return False

    def rename_queue(self, prev_name, new_name):
        if new_name is None:
            new_name = language_pack.default_queue_name

        if prev_name is None:
            prev_name = language_pack.default_queue_name

        if prev_name != new_name:
            if prev_name in self.queues:
                cur_queue_name = self.selected_queue.name if self.selected_queue is not None else None
                queue = self.queues[prev_name]
                queue.name = new_name
                del self.queues[prev_name]

                if cur_queue_name == prev_name:
                    # add and update selected queue
                    self.add_queue(queue)
                else:
                    # only add queue to dictionary
                    self.queues[queue.name] = queue

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
        and updates selected queue
        :param queue: StudentsQueue object to add
        :return: True if queue add was successful
        """
        if self.can_add_queue():
            self.queues[queue.name] = queue
            self.selected_queue = queue
            self.save_current_to_file()
            return True
        return False

    def clear_current_queue(self):
        if self.selected_queue is not None:
            self.selected_queue.clear()

    def remove_queue(self, name):
        if name in self.queues:
            self.delete_queue_files(self.queues[name])
            del self.queues[name]

            if len(self.queues) > 0:
                self.selected_queue = list(self.queues.values())[0]
            else:
                self.selected_queue = None
            return True
        return False

    def get_queue_by_name(self, find_name):
        for name, queue in self.queues.items():
            if name == find_name:
                return queue
        return None

    def get_queue(self) -> QueueStudents:
        return self.selected_queue

    def get_queue_str(self):
        if self.selected_queue is not None:
            return self.selected_queue.str()
        else:
            return language_pack.queue_not_selected

    def queue_empty(self):
        if self.selected_queue is None:
            return True
        elif len(self.selected_queue) == 0:
            return True
        return False

    def generate_choice_keyboard(self, command):
        return keyboards.generate_keyboard(command, self.queues.keys())

    def clear_finished_queues(self):
        to_delete = None
        for name, queue in self.queues.items():
            if queue.get_position() >= len(queue):
                to_delete = name

        if to_delete is not None:
            del self.queues[to_delete]
            self.delete_queue_files(to_delete)