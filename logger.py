from pathlib import Path
import datetime
import sys
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


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
            
    def show_logs(self):
        with self.log_file_path.open('r') as fr:
            print(fr.read())
            
    def delete_logs(self):
        self.log_file_path.open('w').close()
        
    def save_to_cloud(self):
        
        return # test features
        SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
        
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if self.auto_token_path.exists():
            with self.auto_token_path.open('rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.google_creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with self.auto_token_path.open('wb') as token:
                pickle.dump(creds, token)
        
        service = build('drive', 'v3', credentials=creds)
        
        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

        
    def dump_to_another_file(self, file_name):
        path = log_file_path.with_name(file_name)
        
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
            lg.dump_to_another_file('logs/log_{0}.txt'.format(datetime.datetime.now().strftime('%d-%m-%y:%H-%M')))
            lg.delete_logs()
        else:
            logger().log(sys.argv[1])