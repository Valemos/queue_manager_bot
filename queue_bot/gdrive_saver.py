import enum
import pickle
import os
import json
import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
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
        # credentials mus be created after SCOPE and account file was specified
        self._credentials = self.init_credentials()

        FolderType.Data.value.mkdir(parents=True, exist_ok=True)

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
        if (FolderType.Data.value / folder_type.value).exists():
            return self.load_folder_id(folder_type)

        folder_metadata = {
            'name': folder_type.name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if folder_type is not DriveFolder.HelperBotData:  # function requests main folder id
            main_folder_id = self.load_folder_id(DriveFolder.HelperBotData)
            if main_folder_id is None:
                main_folder_id = self.create_drive_folder(DriveFolder.HelperBotData)
            folder_metadata['parents'] = [main_folder_id]

        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
            cloud_folder = service.files().create(body=folder_metadata).execute()
            service.permissions().create(fileId=cloud_folder['id'], transferOwnership=True,
                                         body={'type': 'user', 'role': 'owner', 'emailAddress': self.work_email}).execute()
        except Exception as err:
            print(err)
            return None

        return cloud_folder['id']

    def save(self, file_path, folder: DriveFolder):

        if self._credentials is None:
            return False

        service = discovery.build('drive', 'v3', credentials=self._credentials)

        folder_id = self.load_folder_id(folder)

        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id]
        }

        try:
            upload_file = MediaFileUpload(file_path, mimetype='application/octet-stream')
            service.files().create(body=file_metadata, media_body=upload_file, fields='id').execute()
        except Exception as err:
            print(err)
            return None

        return True

    def update_file_list(self, path_list, parent_folder=DriveFolder.HelperBotData):

        if self._credentials is None:
            return False

        service = discovery.build('drive', 'v3', credentials=self._credentials)

        # files list
        existing_files = service.files().list(fields='files(id,name)').execute()['files']

        # update if files exist
        names_dict = {p.name: p for p in path_list if p.exists()}
        for file in existing_files:
            if file['name'] in names_dict:
                update_file = MediaFileUpload(names_dict[file['name']], mimetype='application/octet-stream')
                service.files().update(fileId=file['id'], media_body=update_file).execute()
                del names_dict[file['name']]

        # download to folder if file does not exists
        parent_folder = self.load_folder_id(parent_folder)
        for path in names_dict.values():
            file_metadata = {
                'name': path.name,
                'parents': [parent_folder]
            }
            upload_file = MediaFileUpload(path, mimetype='application/octet-stream')
            file = service.files().create(body=file_metadata, media_body=upload_file).execute()
            try:
                service.permissions().create(fileId=file['id'], transferOwnership=True,
                                             body={'type': 'user', 'role': 'owner',
                                                   'emailAddress': self.work_email}).execute()
            except HttpError as err:
                print(err.error_details)

        return True

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

        return self.download_drive_files(drive_folder_id, save_folder, names_list)

    def download_drive_files(self, folder_id, folder_type, names_list):
        service = discovery.build('drive', 'v3', credentials=self._credentials)

        try:
            existing_files = service.files().list(fields='files(id,name,parents)').execute()['files']
        except HttpError as err:
            print(err.error_details)
            return

        for file in existing_files:

            if not file['name'] in names_list:
                continue

            # if parent folder does not match, continue
            if folder_id not in file['parents']:
                continue

            # form path for file
            result_path = folder_type.value / file['name']

            # request file and write to local drive
            try:
                request = service.files().get_media(fileId=file['id'])
            except HttpError as err:
                print(err.error_details)
                return

            # download if request successful
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
            if file['name'] in exceptions:
                continue

            if 'parents' in file:
                if folder_id not in file['parents']:
                    continue

            if file['mimeType'] != 'application/vnd.google-apps.folder':
                service.files().remove(fileId=file['id']).execute()

        return True

    def delete_everything_on_disk(self):
        service = discovery.build('drive', 'v3', credentials=self._credentials)
        existing_files = service.files().list(fields='files(id)').execute()['files']

        for file in existing_files:
            try:
                service.files().delete(fileId=file['id']).execute()
            except HttpError as err:
                print(err.content)

    def update_all_permissions(self):
        service = discovery.build('drive', 'v3', credentials=self._credentials)
        existing_files = service.files().list(fields='files(id)').execute()['files']

        for file in existing_files:
            try:
                service.permissions().create(fileId=file['id'], transferOwnership=True,
                                             body={'type': 'user', 'role': 'owner',
                                                   'emailAddress': self.work_email}).execute()
            except HttpError as err:
                print(err.content)

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
        if not file.exists():
            file.touch()

        try:
            with file.open('wb') as fout:
                pickle.dump(folder_id, fout)
        except pickle.UnpicklingError:
            print('failed to load id from \"{}\"'.format(file))

    @staticmethod
    def load_folder_id(drive_folder: DriveFolder):
        if drive_folder is None:
            return None

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
    os.chdir('../')
    if len(sys.argv) == 2:
        if sys.argv[1] == 'clear':
            DriveSaver().delete_everything_on_disk()
        elif sys.argv[1] == 'show_data':
            DriveSaver().show_folder_files(DriveFolder.HelperBotData)
        elif sys.argv[1] == 'show_logs':
            DriveSaver().show_folder_files(DriveFolder.Log)
