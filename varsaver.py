import os
from pathlib import Path
import pickle

import tempfile
from google.oauth2 import service_account
from apiclient import discovery
from apiclient.http import MediaFileUpload

class VariableSaver:
    
    def __init__(self, save_folder = None, logger = None):
        
        if save_folder is None:
            save_folder = Path('data')
            save_folder.mkdir(parents = True, exist_ok = True)
            
        self.save_folder = save_folder
        self.logger = logger
        
    def save(self, var, file_name):
        
        save_path = self.save_folder/file_name
        
        if not self.logger is None:
            self.logger.log('saving '+str(save_path))
                
        if not save_path.exists():
            save_path.touch()
        
        with save_path.open('wb') as fw:
            pickle.dump(var, fw)
    def load(self, file_name):        
        save_path = self.save_folder/file_name

        if not self.logger is None:
            self.logger.log('loading '+str(save_path))

        if not save_path.exists():
            save_path.touch()
            return None
        
        
        try:
            with save_path.open('rb') as fr:
                return pickle.load(fr)
        except Exception:
            return None
            
class DriveSaver:
    
    def __init__(self):
        
        self.__SCOPES = ['https://www.googleapis.com/auth/drive']
        self.__SERVICE_ACCOUNT_FILE = Path('queue-bot-key.json')
        self.work_email = 'programworkerbox@gmail.com'
        
        self.__credentials = self.init_credentials()
        
    def init_credentials(self):
        
        # try read service account file
        if self.__SERVICE_ACCOUNT_FILE.exists():
            creds = service_account.Credentials.from_service_account_file(\
                            self.__SERVICE_ACCOUNT_FILE, scopes=self.__SCOPES)
                
            return creds
        
        return None
      
    def init_drive_folder(self):
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
        
        folder_metadata = {
        'name': 'Queue Bot data',
        'mimeType': 'application/vnd.google-apps.folder'
        }
        self.cloud_folder = service.files().create(body=folder_metadata).execute()
        cloudPermissions = service.permissions().create(fileId=cloudFolder['id'],\
                            body={'type': 'user', 'role': 'reader', 'emailAddress': self.work_email}).execute()
        
      
    def save(self, file_name):
        
        if self.__credentials is None:
            return False
        
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
        
        
        return True

if __name__ == '__main__':
    
    saver = DriveSaver()
    d = saver.save('logs/log.txt')
    print(d)