import enum
from pathlib import Path
import shutil
import pickle


class Savable:
    def get_save_files(self):
        raise NotImplementedError

    def save_to_file(self, saver):
        raise NotImplementedError

    def load_file(self, saver):
        raise NotImplementedError


class FolderType(enum.Enum):
    NoFolder = Path()
    Data = Path('data')
    SubjectChoices = Path('subject_choices')
    DriveData = Path('drive_data')
    Backup = Path('data_backup')
    Logs = Path('logs')
    Test = Path('test_data')


class VariableSaver:

    def __init__(self, logger=None, default_folder=FolderType.Data):
        self.logger = logger
        self.default_folder = default_folder

    def log(self, content):
        if self.logger is not None:
            self.logger.log(content)

    def save(self, var, save_path, save_folder=FolderType.Data):
        if save_folder is None:
            save_folder = self.default_folder
        save_path = save_folder.value / save_path
        self.log('saving to ' + str(save_path))

        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.touch()
        try:
            with save_path.open('wb') as fw:
                pickle.dump(var, fw)
        except pickle.PickleError:
            self.log('file {0}: save failed'.format(save_path))

    def load(self, save_path, save_folder=FolderType.Data):
        if save_folder is None:
            save_folder = self.default_folder
        save_path = save_folder.value / save_path
        self.log('loading from ' + str(save_path))

        if not save_path.exists():
            save_path.touch()
            return None

        try:
            with save_path.open('rb') as fr:
                return pickle.load(fr)
        except pickle.UnpicklingError:
            self.log('file {0}: load failed'.format(save_path))
            return None

    @staticmethod
    def clear_folder(folder: Path):
        shutil.rmtree(folder)
