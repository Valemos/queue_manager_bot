import os
from pathlib import Path
import datetime
import sys
from queue_bot.object_file_saver import FolderType
from queue_bot.gdrive_saver import DriveSaver, DriveFolder


class Logger:
    
    def __init__(self, log_path=None):
        if log_path is None:
            log_path = FolderType.Logs.value / Path('log.txt')
            
        if not log_path.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.touch()
            
        self.log_file_path = log_path
        self.drive_saver = DriveSaver()
        
    def log(self, text):
        with self.log_file_path.open('a+', encoding='utf-8') as fw:
            fw.write('{0}: {1}\n'.format(datetime.datetime.now(), text))
            
    def get_logs(self):
        with self.log_file_path.open(encoding='utf-8') as fr:
            return fr.read()
            
    def delete_logs(self):
        self.log_file_path.open('w').close()
        
    def dump_to_file(self, file_name=None):
        if file_name is None:
            path = self.log_file_path.with_name('log_{0}.txt'.format(datetime.datetime.now().strftime('%d-%m-%y_%H-%M')))    
        else:
            path = self.log_file_path.with_name(file_name)

        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.log_file_path.open(encoding='utf-8') as fr, path.open('w', encoding='utf-8') as fw:
            fw.write(fr.read())

        os.remove(self.log_file_path)
        return path
        
    def save_to_cloud(self):
        
        new_name = Path('log_{0}.txt'.format(datetime.date.today()))
        
        path = self.dump_to_file(new_name)
        self.drive_saver.save(path, DriveFolder.Log)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'cloud':
            Logger().save_to_cloud()
        elif sys.argv[1] == 'dump':
            lg = Logger()
            lg.dump_to_file()
        else:
            Logger().log(sys.argv[1])