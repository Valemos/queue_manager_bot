#  class relies on unique names, and is not suitable for multiple chats
from queue_bot.savable_interface import Savable
from queue_bot import bot_keyboards, bot_parsers as parsers

from queue_bot.students_queue import StudentsQueue


class QueuesManager(Savable):

    queues_count_limit = 10
    queues = {}
    selected_queue = None

    def __init__(self, main_bot, queues: list = None):
        if queues is None:
            self.queues = {}
        else:
            self.queues = {queue.name: queue for queue in queues}
        self.main_bot = main_bot

    def __len__(self):
        return len(self.queues)

    def __contains__(self, item):
        return item in self.queues

    def set_current_queue(self, name):
        if name in self.queues:
            self.selected_queue = self.queues[name]
            return True
        return False

    def set_default_queue(self):
        if self.main_bot.language_pack.default_queue_name in self.queues:
            self.selected_queue = self.get_queue_by_name(self.main_bot.language_pack.default_queue_name)
        else:
            self.selected_queue = StudentsQueue(self.main_bot, self.main_bot.language_pack.default_queue_name)
            self.queues[self.selected_queue.name] = self.selected_queue

    def rename_queue(self, prev_name, new_name):
        if new_name is None:
            new_name = self.main_bot.language_pack.default_queue_name

        if prev_name is None:
            prev_name = self.main_bot.language_pack.default_queue_name

        if prev_name != new_name:
            if prev_name in self.queues:
                queue = self.queues[prev_name]
                queue.name = new_name
                del self.queues[prev_name]
                self.add_queue(queue)

    @staticmethod
    def create_queue(*args):
        return StudentsQueue(*args)

    # handle queue limit
    def can_add_queue(self):
        return len(self.queues) < self.queues_count_limit

    def add_queue(self, queue):
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
            del self.queues[name]
            self.delete_queue_file(name)

            if len(self.queues) > 0:
                self.selected_queue = list(self.queues.values())[0]
            else:
                self.selected_queue = None

    def get_queue_by_name(self, find_name):
        for name, queue in self.queues.items():
            if name == find_name:
                return queue
        return None

    def get_queue(self) -> StudentsQueue:
        if self.selected_queue is None:
            self.set_default_queue()
        return self.selected_queue

    def get_queue_str(self):
        if self.selected_queue is None:
            self.set_default_queue()
        return self.selected_queue.str()

    def queue_empty(self):
        if self.selected_queue is None:
            return True
        elif len(self.selected_queue) == 0:
            return True
        return False

    def generate_choice_keyboard(self, command):
        return bot_keyboards.generate_keyboard(command, self.queues.keys())

    def clear_finished_queues(self):
        to_delete = None
        for name, queue in self.queues.items():
            if queue.get_position() >= len(queue):
                to_delete = name

        if to_delete is not None:
            del self.queues[to_delete]
            self.delete_queue_file(to_delete)

    # method used to save all queue files to drive
    def get_save_files(self):
        queues_files = []
        for queue in self.queues.values():
            queues_files.extend(queue.get_save_files())
        return queues_files

    def save_current_to_file(self):
        self.selected_queue.save_to_file(self.main_bot.object_saver)

    def delete_queue_file(self, name):
        for file in self.selected_queue.get_save_files():
            self.main_bot.object_saver.delete(file)

    def save_to_file(self, saver):
        for queue in self.queues.values():
            queue.save_to_file(saver)

    def load_file(self, saver):
        # we scan save folder to find all required files
        file_names = []
        for path in StudentsQueue.save_folder.glob('**/*'):
            file_names.append(path.name)

        queue_names = parsers.parse_valid_queue_names(file_names)

        self.queues = {}
        for name in queue_names:
            queue = StudentsQueue(self.main_bot)
            queue.name = name
            queue.load_file(saver)
            self.queues[queue.name] = queue

