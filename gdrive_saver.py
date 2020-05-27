import pickle
from google.oauth2 import service_account
from apiclient import discovery
from apiclient.http import MediaFileUpload
from pathlib import Path

class DriveSaver:
    
    def __init__(self):
        
        self.__SCOPES = ['https://www.googleapis.com/auth/drive']
        self.__SERVICE_ACCOUNT_FILE = Path('queue-bot-key.json')
        self.work_email = 'programworkerbox@gmail.com'
        
        self.__credentials = self.init_credentials()
        self.init_drive_folder()
        
    def init_credentials(self):
        
        # try read service account file
        if self.__SERVICE_ACCOUNT_FILE.exists():
            creds = service_account.Credentials.from_service_account_file(\
                            self.__SERVICE_ACCOUNT_FILE, scopes=self.__SCOPES)
                
            return creds
        
        return None
      
    def init_drive_folder(self):
        
        file_folder_id = Path('data/drive_folder_id.data')
        file_folder_id.parent.mkdir(parents=True, exist_ok=True)
        
        cloud_folder_id = None
        if file_folder_id.exists():
            try:
                with file_folder_id.open('rb') as fr:
                    cloud_folder_id = pickle.load(fr)
            except Exception:
                print('failed to load folder id')
            
        # creates folder and saves it's id to file
        if cloud_folder_id is None:
            service = discovery.build('drive', 'v3', credentials=self.__credentials)
    
            folder_metadata = {
            'name': 'Queue Bot data',
            'mimeType': 'application/vnd.google-apps.folder'
            }
            
            cloudFolder = service.files().create(body=folder_metadata).execute()
            cloudPermissions = service.permissions().create(fileId=cloudFolder['id'],\
                            transferOwnership=True, body={'type': 'user', 'role': 'owner', 'emailAddress': self.work_email}).execute()
            
            cloud_folder_id = cloudFolder['id']
            
            try:
                with file_folder_id.open('wb+') as fw:
                    pickle.dump(cloud_folder_id, fw)
            except Exception:
                print('gdrive folder id write failed')
            
        # after all manipulations init class property
        self.cloud_folder_id = cloud_folder_id
            
    def save(self, file_name):
        
        if self.__credentials is None:
            return False
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
        
        file_metadata = {
            'name': file_name.name,
            'parents': [self.cloud_folder_id]
        }

        media = MediaFileUpload(file_name, mimetype='application/octet-stream')
        
        service.files().create(body=file_metadata,
                                media_body=media,
                                fields='id').execute()
        
        print('saved', file_name, 'to cloud')
        
        return True
    
if __name__ == '__main__':
    
    saver = DriveSaver()
    # saver.save(Path('logs/log.txt'))