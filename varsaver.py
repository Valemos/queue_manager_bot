import os
from pathlib import Path
import pickle

class VariableSaver:
    
    def __init__(self, save_folder = None, logger = None):
        
        if save_folder is None:
            save_folder = Path('data')
            save_folder.mkdir(parents = True, exist_ok = True)
            
        self.save_folder = save_folder
        
    def save(self, var, file_name):
        
        save_path = self.save_folder/file_name
        
        if not save_path.exists():
            save_path.touch()
        
        with save_path.open('wb') as fw:
            pickle.dump(var, fw)
        
    def load(self, file_name):
        
        save_path = self.save_folder/file_name
        if not save_path.exists():
            save_path.touch()
            return None
        
        try:
            with save_path.open('rb') as fr:
                return pickle.load(fr)
        except Exception:
            return None
            

if __name__ == '__main__':
    
    dct = {1:'hello',2:'not hello'}
    
    saver = VariableSaver()
    