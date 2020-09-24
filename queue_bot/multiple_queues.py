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

    _file_names_list = FolderType.Data.value / Path('multiple_queues_paths.data')

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
        self._queues[self._selected_queue.name] = self._selected_queue

    def rename_queue(self, prev_name, new_name):
        if prev_name in self._queues:
            queue = self._queues[prev_name]
            queue.name = new_name

            del self._queues[prev_name]
            self.add_queue(queue)

    # handle queue limit
    def add_queue(self, queue):
        if len(self._queues) < 10:
            self._queues[queue.name] = queue
            self._selected_queue = queue
            self.save_current_to_file()
            self.save_queue_paths()
            return True
        return False

    def clear_current_queue(self):
        if self._selected_queue is not None:
            self._selected_queue.clear()

    def remove_queue(self, name):
        if name in self._queues:
            del self._queues[name]
            self.delete_queue_file(name)
            self.save_queue_paths()

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

    def generate_choice_keyboard(self, command):
        buttons = []

        for name in self._queues.keys():
            if name == '':
                name = '*нет имени*'
            buttons.append([InlineKeyboardButton(name, callback_data=command.str(name))])
        buttons.append([InlineKeyboardButton('Отменить', callback_data=General.Cancel.str())])
        return InlineKeyboardMarkup(buttons)

    def clear_finished_queues(self):
        to_delete = None
        for name, queue in self._queues.items():
            if queue.get_position() >= len(queue):
                to_delete = name

        if to_delete is not None:
            del self._queues[to_delete]
            self.delete_queue_file(to_delete)
            self.save_queue_paths()

    # method used to save all queue files to drive
    def get_save_files(self):
        queues_files = []
        for queue in self._queues.values():
            queues_files.extend(queue.get_save_files())

        return [FolderType.Data.value / self._file_names_list] + queues_files

    def save_current_to_file(self):
        self._selected_queue.save_to_file(self.main_bot.object_saver)

    def delete_queue_file(self, name):
        for file in self._selected_queue.get_save_files():
            self.main_bot.object_saver.delete(file)

    def save_queue_paths(self):
        queues_names = list(self._queues.keys())
        self.main_bot.object_saver.save(queues_names, self._file_names_list)

    def save_to_file(self, saver):
        self.save_queue_paths()
        for queue in self._queues.values():
            queue.save_to_file(saver)

    def load_file(self, saver):
        queues_names = saver.load(self._file_names_list)
        self._queues = {}
        if queues_names is not None:
            for name in queues_names:
                queue = StudentsQueue(self.main_bot)
                queue.name = name
                queue.load_file(saver)
                self._queues[queue.name] = queue
