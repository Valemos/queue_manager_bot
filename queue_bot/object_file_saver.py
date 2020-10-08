import enum
import os
from pathlib import Path
import shutil
import pickle


class FolderType(enum.Enum):
    NoFolder = Path()
    Data = Path('data')
    DataDriveFolders = Path('data/drive_folders')
    QueuesData = Path('queues_data')
    SubjectChoices = Path('subject_choices')
    DriveData = Path('drive_data')
    Backup = Path('data_backup')
    Logs = Path('logs')
    Test = Path('test_data')


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
            with save_path.open('wb') as fw:
                pickle.dump(var, fw)
        except (pickle.PickleError, TypeError) as err:
            self.log('file {0}: save failed\n{1}'.format(save_path, str(err)))
            print('file {0}: save failed\n{1}'.format(save_path, str(err)))

    def load(self, save_path):
        self.log('loading from ' + str(save_path))
        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.touch()
            return None
        try:
            with save_path.open('rb') as fr:
                return pickle.load(fr)
        except (pickle.UnpicklingError, EOFError):
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
