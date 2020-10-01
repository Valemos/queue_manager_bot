#  class relies on unique names, and is not suitable for multiple chats
from pathlib import Path

from queue_bot.savable_interface import Savable
from queue_bot.object_file_saver import FolderType
from queue_bot.bot_commands import ManageQueues, General
from queue_bot import bot_keyboards

from queue_bot.students_queue import StudentsQueue


class QueuesManager(Savable):

    queues = {}
    selected_queue = None

    file_names_list = FolderType.Data.value / Path('multiple_queues_paths.data')

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
        self.selected_queue = StudentsQueue(self.main_bot)  # default queue
        self.queues[self.selected_queue.name] = self.selected_queue

    def rename_queue(self, prev_name, new_name):
        if prev_name in self.queues:
            queue = self.queues[prev_name]
            queue.name = new_name
            del self.queues[prev_name]
            self.add_queue(queue)

    @staticmethod
    def create_queue(*args):
        return StudentsQueue(*args)

    # handle queue limit
    def add_queue(self, queue):
        if len(self.queues) < 10:
            self.queues[queue.name] = queue
            self.selected_queue = queue
            self.save_current_to_file()
            self.save_queue_paths()
            return True
        return False

    def clear_current_queue(self):
        if self.selected_queue is not None:
            self.selected_queue.clear()

    def remove_queue(self, name):
        if name in self.queues:
            del self.queues[name]
            self.delete_queue_file(name)
            self.save_queue_paths()
            if self.selected_queue.name == name and len(self.queues) > 0:
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
            self.save_queue_paths()

    def get_queues_files(self, names=None):
        queues_files = []
        if names is None:
            for queue in self.queues.values():
                queues_files.extend(queue.get_save_files())
        else:
            temp_queue = StudentsQueue(self.main_bot)
            for name in names:
                temp_queue.name = name
                queues_files.extend(temp_queue.get_save_files())
        return queues_files

    # method used to save all queue files to drive
    def get_save_files(self):
        return [self.file_names_list] + self.get_queues_files()

    def save_current_to_file(self):
        self.selected_queue.save_to_file(self.main_bot.object_saver)

    def delete_queue_file(self, name):
        for file in self.selected_queue.get_save_files():
            self.main_bot.object_saver.delete(file)

    def save_queue_paths(self):
        queues_names = list(self.queues.keys())
        self.main_bot.object_saver.save(queues_names, self.file_names_list)

    def save_to_file(self, saver):
        self.save_queue_paths()
        for queue in self.queues.values():
            queue.save_to_file(saver)

    def load_file(self, saver):
        queues_names = saver.load(self.file_names_list)
        self.queues = {}
        if queues_names is not None:
            for name in queues_names:
                queue = StudentsQueue(self.main_bot)
                queue.name = name
                queue.load_file(saver)
                self.queues[queue.name] = queue

    def load_queues_from_drive(self, drive_saver, object_saver):
        from queue_bot.gdrive_saver import DriveFolder
        drive_saver.get_files_from_drive([self.file_names_list], DriveFolder.Queues)
        queues_names = object_saver.load(self.file_names_list)
        drive_saver.get_files_from_drive(self.get_queues_files(queues_names), DriveFolder.Queues)
        self.load_file(object_saver)
