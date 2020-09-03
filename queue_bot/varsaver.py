import enum
from pathlib import Path
import pickle


class Savable:
    def get_save_files(self):
        raise NotImplementedError

    def save_to_file(self, saver):
        raise NotImplementedError

    def load_file(self, saver):
        raise NotImplementedError


class FolderType(enum.Enum):
    Data = Path('../data')
    DriveData = Path('../drive_data')
    Backup = Path('../data-Copy')
    Logs = Path('../logs')


class VariableSaver:

    def __init__(self, logger=None):
        self.logger = logger

    def save(self, var, save_path, save_folder=FolderType.Data):
        save_path = save_folder.value / save_path
        if self.logger is not None:
            self.logger.log('saving ' + str(save_path))

        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.touch()

        with save_path.open('wb') as fw:
            pickle.dump(var, fw)

    def load(self, save_path, save_folder=FolderType.Data):
        save_path = save_folder.value / save_path
        if self.logger is not None:
            self.logger.log('loading ' + str(save_path))

        if not save_path.exists():
            save_path.touch()
            return None

        try:
            with save_path.open('rb') as fr:
                return pickle.load(fr)
        except pickle.UnpicklingError:
            return None
