#  class relies on unique names, and is not suitable for multiple chats
from pathlib import Path

from queue_bot.savable_interface import Savable
from queue_bot.varsaver import FolderType


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

    def set_cur_queue(self, name):
        if name in self._queues:
            self._selected_queue = self._queues[name]
            return True
        return False

    # handle queue limit
    def add_queue(self, queue):
        if len(self._queues) < 10:
            self._queues[queue.name] = queue
            return True
        return False

    def get_queue_by_name(self, find_name):
        for queue in self._queues:
            if queue.name == find_name:
                return queue
        return None

    def get_queue(self):
        return self._selected_queue

    def get_queue_save_file(self, name):
        return FolderType.QueuesData.value / Path(self._file_format_queue.format(name))

    # method used to save all files to drive
    def get_save_files(self):
        return [FolderType.Data.value / self._file_paths_list] + \
               [self.get_queue_save_file(queue.name) for queue in self._queues]

    def save_to_file(self, saver):
        queue_paths_list = self.get_save_files()[1:]  # except first path, all paths will be for queue data
        saver.save(queue_paths_list, self._file_paths_list)

        for queue in self._queues:
            saver.save(queue, self.get_queue_save_file(queue.name), FolderType.NoFolder)


    def load_file(self, saver):
        queue_save_files = saver.load(self._file_paths_list)
        self._queues = []
        for file in queue_save_files:
            queue = saver.load(file, FolderType.QueuesData)
            if queue is not None:
                self._queues.append(queue)
