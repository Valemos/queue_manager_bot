import os
from pathlib import Path
import pickle

class VariableSaver:
    
    def __init__(self, logger = None):
        self.logger = logger
        
    def save(self, var, save_path):
        if not self.logger is None:
            self.logger.log('saving '+str(save_path))
                
        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.touch()
        
        with save_path.open('wb') as fw:
            pickle.dump(var, fw)
            
    def load(self, save_path):        
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


# if __name__ == '__main__':
    
#     saver = VariableSaver()