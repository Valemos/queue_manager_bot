#  class relies on unique names, and is not suitable for multiple chats
from pathlib import Path

from queue_bot.savable_interface import Savable
from queue_bot.object_file_saver import FolderType
from queue_bot.bot_commands import QueuesManage, General
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from queue_bot.students_queue import StudentsQueue


class QueuesManager(Savable):

    _queues = {}
    _selected_queue = None

    _file_paths_list = Path('multiple_queues_paths.data')
    _file_format_queue = 'queue_{0}.data'

    def __init__(self, main_bot, queues: list = None):
        if queues is None:
            self._queues = {}
        else:
            self._queues = {queue.name: queue for queue in queues}

        self.main_bot = main_bot
        self.add_queue(StudentsQueue(main_bot))

    def set_current_queue(self, name):
        if name in self._queues:
            self._selected_queue = self._queues[name]
            return True
        return False

    def set_default_queue(self):
        self._selected_queue = StudentsQueue(self.main_bot)  # default queue
        if self._selected_queue.name not in self._queues:
            self._queues[self._selected_queue.name] = self._selected_queue
        else:
            self._selected_queue = self._queues[self._selected_queue.name]

    # handle queue limit, but ignore default queue
    # (with default value limit of queues really is 11)
    def add_queue(self, queue):
        if len(self._queues) < 10:
            self._queues[queue.name] = queue
            self._selected_queue = queue
            return True
        return False

    def clear_current_queue(self):
        if self._selected_queue is not None:
            self._selected_queue.clear()

    def remove_queue(self, name):
        if name in self._queues:
            del self._queues[name]

    def get_queue_by_name(self, find_name):
        for queue in self._queues:
            if queue.name == find_name:
                return queue
        return None

    def get_queue(self):
        if self._selected_queue is None:
            self.set_default_queue()
        return self._selected_queue

    def get_queue_str(self):
        if self._selected_queue is None:
            self.set_default_queue()
        return self._selected_queue.str()

    def queue_empty(self):
        if self._selected_queue is None:
            self.set_default_queue()
            return True
        elif len(self._selected_queue) == 0:
            return True
        return False

    def get_queue_save_file(self, name):
        return FolderType.QueuesData.value / Path(self._file_format_queue.format(name))

    def generate_choice_keyboard(self, command):
        buttons = []

        for queue in self._queues:
            buttons.append(InlineKeyboardButton(queue.name, callback_data=command.str(queue.name)))

        buttons.append(InlineKeyboardButton('', callback_data=General.Cancel))

        return InlineKeyboardMarkup(buttons)

    def clear_finished_queues(self):
        for name, queue in self._queues.items():
            if queue.get_position() >= len(queue):
                del self._queues[name]

    # method used to save all queue files to drive
    def get_save_files(self):
        return [FolderType.Data.value / self._file_paths_list] + \
               [self.get_queue_save_file(name) for name in self._queues.keys()]

    def save_current_to_file(self, saver):
        saver.save(self._selected_queue, self.get_queue_save_file(self._selected_queue.name))

    def save_to_file(self, saver):
        queue_paths_list = self.get_save_files()[1:]  # except first path, all paths will be for queue data
        saver.save(queue_paths_list, self._file_paths_list, FolderType.Data)

        for queue in self._queues:
            saver.save(queue, self.get_queue_save_file(queue.name))

    def load_file(self, saver):
        queue_save_files = saver.load(self._file_paths_list, FolderType.Data)
        self._queues = {}
        if queue_save_files is not None:
            for file in queue_save_files:
                queue = saver.load(file, FolderType.QueuesData)
                if queue is not None:
                    self._queues[queue.name] = queue
