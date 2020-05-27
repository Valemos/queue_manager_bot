import pickle
from google.oauth2 import service_account
from apiclient import discovery
from apiclient.http import MediaFileUpload
from pathlib import Path

class DriveSaver:
    
    def __init__(self, for_logs = False):
        
        self.__SCOPES = ['https://www.googleapis.com/auth/drive']
        self.__SERVICE_ACCOUNT_FILE = Path('queue-bot-key.json')
        self.work_email = 'programworkerbox@gmail.com'
        
        self.file_data_id = Path('data/drive_folder_id.data')
        self.file_logs_id = Path('data/logs_folder_id.data')
        
        self.__credentials = self.init_credentials()
        
        self.init_drive_folders()
        
        if for_logs:
            self.cloud_folder_id = self.get_logs_folder_id()
        else:
            self.cloud_folder_id = self.get_main_folder_id()
            
    def init_credentials(self):
        
        # try read service account file
        if self.__SERVICE_ACCOUNT_FILE.exists():
            creds = service_account.Credentials.from_service_account_file(\
                            self.__SERVICE_ACCOUNT_FILE, scopes=self.__SCOPES)
                
            return creds
        
        return None
      
    def get_main_folder_id(self):
        cloud_id = None
        if self.file_data_id.exists():
            try:
                with self.file_data_id.open('rb') as fr:
                    cloud_id = pickle.load(fr)
            except Exception:
                print('failed to load folder id')
        
        return cloud_id
    
    def get_logs_folder_id(self):
        cloud_id = None
        if self.file_logs_id.exists():
            try:
                with self.file_logs_id.open('rb') as fr:
                    cloud_id = pickle.load(fr)
            except Exception:
                print('failed to load folder id')
        
        return cloud_id  
    
    def init_drive_folders(self):
        
        self.file_data_id.parent.mkdir(parents=True, exist_ok=True)
        
        cloud_main_id = self.get_main_folder_id()
        cloud_logs_id = self.get_logs_folder_id()
        
        # creates folders and saves their id to file
        if cloud_main_id is None:
            service = discovery.build('drive', 'v3', credentials=self.__credentials)
    
            folder_metadata = {
            'name': 'Queue Bot data',
            'mimeType': 'application/vnd.google-apps.folder'
            }
            
            cloudFolder = service.files().create(body=folder_metadata).execute()
            service.permissions().create(fileId=cloudFolder['id'],\
                            transferOwnership=True, body={'type': 'user', 'role': 'owner', 'emailAddress': self.work_email}).execute()
            
            cloud_main_id = cloudFolder['id']
            
            try:
                with self.file_data_id.open('wb+') as fw:
                    pickle.dump(cloud_main_id, fw)
            except Exception:
                print('gdrive folder id write failed')
        
        if cloud_logs_id is None:
            service = discovery.build('drive', 'v3', credentials=self.__credentials)
    
            folder_metadata = {
            'name': 'Logs',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [cloud_main_id]
            }
            
            cloudFolder = service.files().create(body=folder_metadata).execute()
            service.permissions().create(fileId=cloudFolder['id'],\
                            transferOwnership=True, body={'type': 'user', 'role': 'owner', 'emailAddress': self.work_email}).execute()
            
            cloud_logs_id = cloudFolder['id']
            
            try:
                with self.file_logs_id.open('wb+') as fw:
                    pickle.dump(cloud_logs_id, fw)
            except Exception:
                print('gdrive folder id write failed')
            
    def save(self, file_path):
        
        if self.__credentials is None:
            return False
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
        
        file_metadata = {
            'name': file_path.name,
            'parents': [self.cloud_folder_id]
        }

        media = MediaFileUpload(file_path, mimetype='application/octet-stream')
        
        service.files().create(body=file_metadata,
                                media_body=media,
                                fields='id').execute()
        
        print('saved', file_path, 'to cloud')
        
        return True
    
    def update_file_list(self, path_lst):
        
        if self.__credentials is None:
            return False
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
                
        # files list
        existing_files = service.files().list().execute()['files']
        return existing_files
        batch = service.new_batch_http_request()
        for file in existing_files:
            batch.add(service.files().delete(fileId = file['id']))
        batch.execute()
        
        # 1 search for matches in file names
        # 2 delete those files
        # 3 load new files
        
        # return service.files().list().execute()['files']
        
    def get_file_list(self):
        pass
    
if __name__ == '__main__':
    
    saver = DriveSaver(for_logs = True)
    saver.save(Path('logs/log.txt'))
    lst = saver.update_file_list([])
    
    