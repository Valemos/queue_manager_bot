import os
from pathlib import Path
import pickle
import tempfile
from google.oauth2 import service_account

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
        
        self.logs_email = 'programworkerbox@gmail.com'
        
        
        # try read service account file
        

if __name__ == '__main__':
    
    saver = VariableSaver()
    d = saver.load('token.data')