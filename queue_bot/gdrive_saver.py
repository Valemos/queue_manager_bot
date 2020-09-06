import enum
import pickle
import os
import json
import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from queue_bot.varsaver import FolderType


# holds file paths to folder id`s
class DriveFolder(enum.Enum):
    HelperBotData = Path('drive_folder_id.data')
    Log = Path('logs_folder_id.data')
    SubjectChoices = Path('choices_folder_id.data')


class DriveSaver:

    def __init__(self):
        self._SCOPES = ['https://www.googleapis.com/auth/drive']
        self._SERVICE_ACCOUNT_FILE = FolderType.DriveData.value / Path('queue-bot-key.json')
        self.work_email = 'programworkerbox@gmail.com'
        self._credentials = self.init_credentials()

        FolderType.Data.mkdir(parents=True, exist_ok=True)

        # must create main folder first
        self.init_drive_folder(DriveFolder.HelperBotData)
        self.init_drive_folder(DriveFolder.Log)
        self.init_drive_folder(DriveFolder.SubjectChoices)

    def init_credentials(self):
        # try read service account file
        if self._SERVICE_ACCOUNT_FILE.resolve().exists():
            return service_account.Credentials.from_service_account_file(self._SERVICE_ACCOUNT_FILE, scopes=self._SCOPES)
        elif 'GOOGLE_CREDS' in os.environ:
            return service_account.Credentials.from_service_account_info(json.loads(os.environ.get('GOOGLE_CREDS')))
        return None

    def init_drive_folder(self, drive_folder):
        if self.load_folder_id(drive_folder) is None:
            folder_id = self.create_drive_folder(drive_folder)
            self.save_folder_id(drive_folder, folder_id)

    def create_drive_folder(self, folder_type):
        folder_metadata = {
            'name': folder_type.__name__,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if folder_type is not DriveFolder.HelperBotData:  # function requests main folder id
            main_folder_id = self.load_folder_id(folder_type)
            folder_metadata['parents'] = [main_folder_id]

        service = discovery.build('drive', 'v3', credentials=self._credentials)
        cloud_folder = service.files().create(body=folder_metadata).execute()
        service.permissions().create(fileId=cloud_folder['id'], transferOwnership=True,
                                     body={'type': 'user', 'role': 'owner', 'emailAddress': self.work_email}).execute()
        return cloud_folder

    def save(self, file_path, folder: DriveFolder):

        if self._credentials is None:
            return False

        service = discovery.build('drive', 'v3', credentials=self._credentials)

        folder_id = self.load_folder_id(folder)

        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id]
        }

        upload_file = MediaFileUpload(file_path, mimetype='application/octet-stream')
        service.files().create(body=file_metadata, media_body=upload_file, fields='id').execute()

        return True

    def update_file_list(self, path_list, parent_folder):

        if self._credentials is None:
            return False

        service = discovery.build('drive', 'v3', credentials=self._credentials)

        # files list
        existing_files = service.files().list().execute()['files']

        # update if files exist
        names_dict = {p.name: p for p in path_list if p.exists()}
        for file in existing_files:
            if file['name'] in names_dict:
                update_file = MediaFileUpload(names_dict[file['name']], mimetype='application/octet-stream')
                service.files().update(fileId=file['id'], media_body=update_file).execute()
                del names_dict[file['name']]

        parent_folder = self.load_folder_id(parent_folder)
        for path in names_dict.values():
            file_metadata = {
                'name': path.name,
                'parents': [parent_folder]
            }
            upload_file = MediaFileUpload(path, mimetype='application/octet-stream')
            service.files().create(body=file_metadata, media_body=upload_file).execute()

    # if path_list not specified, all files from folder will be written to 'new_folder'
    def get_file_list(self, path_list=None, drive_folder=DriveFolder.HelperBotData, save_folder=FolderType.Data):
        if path_list is None:
            path_list = []

        if self._credentials is None:
            return False

        drive_folder_id = self.load_folder_id(drive_folder)
        if drive_folder_id is None:
            self.create_drive_folder(drive_folder)
            return False

        # create folder on local drive
        if not save_folder.value.exists():
            save_folder.value.mkdir(parents=True)

        # get only names for files in path list
        names_list = [p.name for p in path_list]

        if len(names_list) == 0:
            return False
        return self.download_drive_files(drive_folder_id, save_folder.value, names_list)

    def download_drive_files(self, folder_id, folder_type, names_list):
        service = discovery.build('drive', 'v3', credentials=self._credentials)
        existing_files = service.files().list(fields='files(id,name,parents)').execute()['files']
        for file in existing_files:

            if not file['name'] in names_list:
                continue

            # if parent folder does not match, continue
            if folder_id not in file['parents']:
                continue

            # form path for file
            result_path = folder_type.value / file['name']

            # request file and write to local drive
            request = service.files().get_media(fileId=file['id'])
            with result_path.open('wb+') as fw:
                downloader = MediaIoBaseDownload(fw, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
        return True

    def clear_drive_folder(self, folder: DriveFolder, exceptions=None):

        folder_id = self.load_folder_id(folder)
        if exceptions is None:
            exceptions = []

        service = discovery.build('drive', 'v3', credentials=self._credentials)

        # files list
        existing_files = service.files().list(fields='files(id,name,parents,mimeType)').execute()['files']

        for file in existing_files:
            if file['name'] in exceptions or (folder_id not in file['parents']):
                continue

            if file['mimeType'] != 'application/vnd.google-apps.folder':
                service.files().delete(fileId=file['id']).execute()

        return True

    def show_folder_files(self, folder: DriveFolder):
        folder_id = self.load_folder_id(folder)
        service = discovery.build('drive', 'v3', credentials=self._credentials)

        existing_files = service.files().list(fields='files(name,parents,id)').execute()['files']

        c = 1  # counter of files
        for file in existing_files:
            if folder_id in file['parents']:
                print('{0}. {1}'.format(c, file))
                c += 1

    @staticmethod
    def save_folder_id(drive_folder, folder_id):
        file = FolderType.Data.value / drive_folder.value
        if file.exists():
            try:
                with file.open('wb') as fout:
                    pickle.dump(folder_id, fout)
            except pickle.UnpicklingError:
                print('failed to load id from \"{}\"'.format(file))

    @staticmethod
    def load_folder_id(drive_folder: DriveFolder):
        cloud_id = None
        file = FolderType.Data.value / drive_folder.value
        if file.exists():
            try:
                with file.open('rb') as fr:
                    cloud_id = pickle.load(fr)
            except pickle.UnpicklingError:
                print('failed to load id from \"{}\"'.format(file))

        return cloud_id


if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] == 'clear':
            DriveSaver().clear_drive_folder(DriveFolder.HelperBotData, ['owners.data', 'registered.data'])
        elif sys.argv[1] == 'show_data':
            DriveSaver().show_folder_files(DriveFolder.HelperBotData)
        elif sys.argv[1] == 'show_logs':
            DriveSaver().show_folder_files(DriveFolder.Log)

    # saver = DriveSaver()
    # saver.save(Path('logs/log.txt'), FolderType.Logs)
    # path_list = [Path('data/owners.data'),
    #             Path('data/registered.data'),
    #             Path('data/queue.data'),
    #             Path('data/bot_state.data')]
    # lst = saver.update_file_list(path_list, FolderType.Data)

    # saver.get_file_list(path_list, new_folder=Path('test'))
