import os
from pathlib import Path
import datetime
import sys
from queue_bot.misc.object_file_saver import FolderType
from queue_bot.misc.gdrive_saver import DriveSaver, DriveFolder


class Logger:
    
    def __init__(self, log_path=None):
        if log_path is None:
            log_path = FolderType.Logs.value / Path('log.txt')
            
        if not log_path.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.touch()
            
        self.log_file_path = log_path
        self.drive_saver = DriveSaver(self)
        
    def log(self, text):
        with self.log_file_path.open('a+', encoding='utf-8') as fw:
            fw.write('{0}: {1}\n'.format(datetime.datetime.now().isoformat(), text))

    @staticmethod
    def get_error_msg(error: Exception):
        return f'ERROR TYPE "{type(error).__name__}" args: {", ".join(error.args)}'

    def log_err(self, error: Exception):
        msg = Logger.get_error_msg(error)
        print(msg)
        self.log(msg)

    def get_logs(self):
        with self.log_file_path.open(encoding='utf-8') as fr:
            return fr.read()
            
    def delete_logs(self):
        self.log_file_path.open('w').close()

    def dump_to_file(self, file_name=None):
        if file_name is None:
            iso_time = datetime.datetime.now().strftime("%d-%b-%Y__%H-%M-%S")
            path = self.log_file_path.with_name(f"log_{iso_time}.txt")
        else:
            path = self.log_file_path.with_name(file_name)

        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.log_file_path.open(encoding='utf-8') as fr, path.open('w', encoding='utf-8') as fw:
            fw.write(fr.read())

        return path

    def save_to_cloud(self):
        self.drive_saver.save(self.log_file_path, DriveFolder.Log)


if __name__ == '__main__':
    os.chdir(r'/')
    Logger().dump_to_file()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'cloud':
            Logger().save_to_cloud()
        elif sys.argv[1] == 'dump':
            Logger().dump_to_file()
        else:
            Logger().log(sys.argv[1])
