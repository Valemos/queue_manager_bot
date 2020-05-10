from pathlib import Path
import datetime
import sys

class logger:
    
    def __init__(self, log_path = None):
        if log_path is None:
            log_path = Path('logs.txt')
            
        if not log_path.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.touch(exist_ok=True)
       
        self.log_file_path = log_path
        
    def log(self, text):
        with self.log_file_path.open('a+') as fw:
            fw.write('{0}: {1}\n'.format(datetime.datetime.now(), text))
            
    def show_logs(self):
        with self.log_file_path.open('r') as fr:
            print(fr.read())
            
    def delete_logs(self):
        self.log_file_path.open('w').close()
        
    def dump_to_another_file(self, file_name):
        path = Path(file_name)
        
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        
        with self.log_file_path.open('r') as fr, path.open('w+') as fw:
            fw.write(fr.read())
            
        print('dumped into', file_name)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'show':
            print(logger().show_logs())
        elif sys.argv[1] == 'clear':
            logger().delete_logs()
        elif sys.argv[1] == 'dump':
            lg = logger()
            lg.dump_to_another_file('other_logs/log_{0}.txt'.format(datetime.datetime.now().strftime('%d-%m-%y:%H-%M')))
            lg.delete_logs()