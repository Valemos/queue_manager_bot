import enum
import os
from pathlib import Path
import shutil
import json


class FolderType(enum.Enum):
    Data = Path('data')
    QueuesData = Path('queues_data')
    Logs = Path('logs')


class ObjectSaver:

    def __init__(self, logger=None):
        self.logger = logger

    def log(self, content):
        if self.logger is not None:
            self.logger.log(content)

    def save(self, var, save_path):
        save_path = save_path
        self.log('saving to ' + str(save_path))

        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.touch()

        try:
            with save_path.open('w', encoding='utf-8') as fw:
                json.dump(var, fw)
        except Exception as err:
            self.log('file {0}: save failed\n{1}'.format(save_path, str(err)))
            print('file {0}: save failed\n{1}'.format(save_path, str(err)))

    def load(self, save_path):
        self.log('loading from ' + str(save_path))
        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.touch()
            return None
        try:
            with save_path.open('r', encoding='utf-8') as fr:
                return json.load(fr)
        except (json.JSONDecodeError, EOFError):
            self.log('file {0}: load failed'.format(save_path))
            return None

    def delete(self, save_path):
        if save_path.exists():
            os.remove(save_path)
            self.log('deleted ' + str(save_path))
        else:
            self.log('file does not exists ' + str(save_path))

    @staticmethod
    def clear_folder(folder: Path):
        shutil.rmtree(folder)
