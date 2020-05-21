from pathlib import Path
import datetime
import sys
import pickle


class logger:
    
    def __init__(self, log_path = None):
        if log_path is None:
            log_path = Path('logs/log.txt')
            
        if not log_path.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.touch(exist_ok=True)
            
        self.log_file_path = log_path
        self.google_creds_path = Path('logs/drive_credentials.json')
        self.auto_token_path = Path('token.pickle')
        
    def log(self, text):
        with self.log_file_path.open('a+') as fw:
            fw.write('{0}: {1}\n'.format(datetime.datetime.now(), text))
            
    def get_logs(self):
        with self.log_file_path.open('r') as fr:
            return fr.read()
            
    def delete_logs(self):
        self.log_file_path.open('w').close()
        
    def dump_to_another_file(self, file_name):
        path = self.log_file_path.with_name(file_name)
        
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        
        with self.log_file_path.open('r') as fr, path.open('w+') as fw:
            fw.write(fr.read())
            
        print('dumped into', file_name)
        
    def save_to_cloud(self):
        pass

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'show':
            print(logger().get_logs())
        elif sys.argv[1] == 'clear':
            logger().delete_logs()
        elif sys.argv[1] == 'dump':
            lg = logger()
            lg.dump_to_another_file('logs/log_{0}.txt'.format(datetime.datetime.now().strftime('%d-%m-%y:%H-%M')))
            lg.delete_logs()
        else:
            logger().log(sys.argv[1])