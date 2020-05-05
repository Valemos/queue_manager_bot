from pathlib import Path
import datetime

class logger:
    
    def __init__(self, log_path = None):
        if log_path is None:
            log_path = Path('logs.txt')
       
        self.log_file_path = log_path
        
    def log(self, text):
        with self.log_file_path.open('a+') as fw:
            fw.write('{0}: {1}\n'.format(datetime.datetime.now(), text))
            
    def show_logs(self):
        with self.log_file_path.open('r') as fr:
            print(fr.read())
            
    def delete_logs(self):
        self.log_file_path.open('w').close()