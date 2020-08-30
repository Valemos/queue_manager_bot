import pickle
from google.oauth2 import service_account
from apiclient import discovery
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from pathlib import Path
import enum
import io
import os
import json
import sys
from varsaver import FolderType


class DriveSaver:

    def __init__(self):
        self.__SCOPES = ['https://www.googleapis.com/auth/drive']
        self.__SERVICE_ACCOUNT_FILE = Path('queue-bot-key.json')
        self.work_email = 'programworkerbox@gmail.com'
        
        self.file_data_id = Path('data/drive_folder_id.data')
        self.file_logs_id = Path('data/logs_folder_id.data')
        
        self.__credentials = self.init_credentials()
        
        self.init_drive_folders()
        
    def get_folder_id(self, folder):
        
        if folder is FolderType.Data:
            return self.get_main_folder_id()
            
        elif folder is FolderType.Logs:
            return self.get_logs_folder_id()
        
    def init_credentials(self):
        
        # try read service account file
        if self.__SERVICE_ACCOUNT_FILE.exists():
            creds = service_account.Credentials.from_service_account_file(\
                            self.__SERVICE_ACCOUNT_FILE, scopes=self.__SCOPES)
                
            return creds
        elif 'GOOGLE_CREDS' in os.environ:
            creds = service_account.Credentials.from_service_account_info(json.loads(os.environ.get('GOOGLE_CREDS')))
            print(creds)
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
            
    def save(self, file_path, folder):
        
        if self.__credentials is None:
            return False
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
        
        folder_id = self.get_folder_id(folder)
        
        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id]
        }

        upload_file = MediaFileUpload(file_path, mimetype='application/octet-stream')
        service.files().create(body=file_metadata, media_body=upload_file, fields='id').execute()['id']
        
        return True
    
    def update_file_list(self, path_list, parent_folder):
        
        if self.__credentials is None:
            return False
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
                
        # files list
        existing_files = service.files().list().execute()['files']
        
        # update if files exist
        names_dict = {p.name:p for p in path_list if p.exists()}
        for file in existing_files:
            if file['name'] in names_dict:
                update_file = MediaFileUpload(names_dict[file['name']], mimetype = 'application/octet-stream')
                service.files().update(fileId=file['id'], media_body=update_file).execute()
                del names_dict[file['name']]
        
        parent_folder = self.get_folder_id(parent_folder)
        for path in names_dict.values():
            file_metadata = {
            'name': path.name,
            'parents': [parent_folder]
            }
            upload_file = MediaFileUpload(path, mimetype='application/octet-stream')
            service.files().create(body=file_metadata, media_body=upload_file).execute()

    # if path_list not specified, all files from folder will be written to 'new_folder'
    def get_file_list(self, path_list=None, folder=FolderType.Data):
        
        if self.__credentials is None:
            return False
        
        
        folder_id = self.get_folder_id(folder)
        
        folder_path = Path('') if new_folder is None else new_folder
        # create folder on local drive
        if not folder_path.exists(): folder_path.mkdir(parents=True)    
        
        # get only names for files in path list
        names_list = []
        if path_list is not None:
            names_list = [p.name for p in path_list]
            
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
        existing_files = service.files().list(fields = 'files(id,name,parents)').execute()['files']
        
        for file in existing_files:
            
            # if path list is None, ignore name check
            if path_list is not None:
                if not file['name'] in names_list:
                    continue
            
            # if parent folder does not match, continue
            if not folder_id in file['parents']: continue
                
            # form path for file
            result_path = folder_path/file['name']
            
            # request file and write to local drive
            request = service.files().get_media(fileId=file['id'])
            with result_path.open('wb+') as fw:
                downloader = MediaIoBaseDownload(fw, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()    
            
        return True
    
    def clear_drive_folder(self, folder, exceptions = None):

        folder_id = self.get_folder_id(folder)
        if exceptions is None: exceptions = []
        
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
                
        # files list
        existing_files = service.files().list(fields = 'files(id,name,parents,mimeType)').execute()['files']
        
        for file in existing_files:
            if file['name'] in exceptions or (not folder_id in file['parents']):
                continue
            
            if file['mimeType'] != 'application/vnd.google-apps.folder':
                service.files().delete(fileId = file['id']).execute()
    
        return True
    
    def show_folder_files(self, folder):
        folder_id = self.get_folder_id(folder)
        service = discovery.build('drive', 'v3', credentials=self.__credentials)
        
        existing_files = service.files().list(fields = 'files(name,parents,id)').execute()['files']
        
        c = 1 # counter of files
        for file in existing_files:
            if folder_id in file['parents']:
                print('{0}. {1}'.format(c, file))
                c+=1
        
if __name__ == '__main__':
    
    if len(sys.argv) == 2:
        if sys.argv[1] == 'clear':
            DriveSaver().clear_drive_folder(FolderType.Data, ['owners.data', 'registered.data'])
        elif sys.argv[1] == 'show_data':
            DriveSaver().show_folder_files(FolderType.Data)
        elif sys.argv[1] == 'show_logs':
            DriveSaver().show_folder_files(FolderType.Logs)
    
    # saver = DriveSaver()
    # saver.save(Path('logs/log.txt'), FolderType.Logs)
    # path_list = [Path('data/owners.data'),
    #             Path('data/registered.data'),
    #             Path('data/queue.data'),
    #             Path('data/bot_state.data')]
    # lst = saver.update_file_list(path_list, FolderType.Data)
    
    # saver.get_file_list(path_list, new_folder=Path('test'))