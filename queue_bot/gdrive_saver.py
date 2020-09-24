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
from queue_bot.object_file_saver import FolderType


# holds file paths to folder id`s
class DriveFolder(enum.Enum):
    HelperBotData = Path('drive_folder_id.data')
    Log = Path('logs_folder_id.data')
    SubjectChoices = Path('choices_folder_id.data')
    Queues = Path('queues_folder_id.data')


class DriveSaver:

    def __init__(self):
        self._SCOPES = ['https://www.googleapis.com/auth/drive']
        self._SERVICE_ACCOUNT_FILE = Path(r'D:\coding\Python_codes\Queue_Bot\drive_data\queue-bot-key.json')
        self.work_email = 'programworkerbox@gmail.com'

        # credentials must be created after SCOPE and account file was specified
        self._credentials = self.init_credentials()

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
        folder_id = self.load_folder_id(drive_folder)
        if folder_id is None:
            folder_id = self.create_drive_folder(drive_folder)
            self.save_folder_id(drive_folder, folder_id)
        return folder_id

    def create_drive_folder(self, folder_type):
        if (FolderType.Data.value / folder_type.value).exists():
            return self.load_folder_id(folder_type)

        folder_metadata = self.get_folder_metadata(folder_type.name)  # use name of enum as folder name

        if folder_type is not DriveFolder.HelperBotData:  # function requests main folder id
            main_folder_id = self.load_folder_id(DriveFolder.HelperBotData)
            if main_folder_id is None:
                main_folder_id = self.create_drive_folder(DriveFolder.HelperBotData)
            folder_metadata = self.get_folder_metadata(folder_type.name, main_folder_id)

        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
            cloud_folder = service.files().create(body=folder_metadata).execute()
            service.permissions().create(fileId=cloud_folder['id'],
                                         body={'type': 'user', 'role': 'writer',
                                               'emailAddress': self.work_email}).execute()
        except Exception as err:
            print(err)
            return None

        return cloud_folder['id']

    def save(self, file_path, folder: DriveFolder):

        if self._credentials is None:
            return False

        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
        except Exception as err:
            print(err)
            return False

        folder_id = self.init_drive_folder(folder)
        file_metadata = DriveSaver.get_file_metadata(file_path.name, folder_id)

        try:
            upload_file = MediaFileUpload(file_path, mimetype='application/octet-stream')
            service.files().create(body=file_metadata, media_body=upload_file, fields='id').execute()
        except Exception as err:
            print(err)
            return False

        return True

    def update_file_list(self, path_list, parent_folder):

        if self._credentials is None:
            return False

        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
            existing_files = service.files().list(fields='files(id,name)').execute()['files']
        except Exception as err:
            print(err)
            return False

        # update if files exist
        names_dict = {p.name: p for p in path_list if p.exists()}
        for file in existing_files:
            if file['name'] in names_dict:
                try:
                    update_file = MediaFileUpload(names_dict[file['name']], mimetype='application/octet-stream')
                    service.files().update(fileId=file['name'], media_body=update_file).execute()
                except HttpError as err:
                    print(err.error_details)
                finally:
                    del names_dict[file['name']]  # we delete from dict no matter what error happened

        # download to folder if file does not exists
        parent_folder = self.init_drive_folder(parent_folder)
        for path in names_dict.values():
            file_metadata = DriveSaver.get_file_metadata(path.name, parent_folder)
            try:
                upload_file = MediaFileUpload(path, mimetype='application/octet-stream')
                file = service.files().create(body=file_metadata, media_body=upload_file).execute()
                # service.permissions().create(fileId=file['id'],
                #                              body={'type': 'user', 'role': 'writer',
                #                                    'emailAddress': self.work_email}).execute()
            except HttpError as err:
                print(err.error_details)

    # if path_list not specified, all files from folder will be written to 'new_folder'
    def get_file_list(self, path_list, drive_folder):
        if len(path_list) == 0:
            return True

        if self._credentials is None:
            return False

        drive_folder_id = self.init_drive_folder(drive_folder)
        if drive_folder_id is None:
            self.init_drive_folder(drive_folder)
            return False

        # create folders on local drive
        for path in path_list:
            if not path.parent.exists():
                path.parent.mkdir(parents=True)

        return self.download_drive_files(drive_folder_id, path_list)

    def download_drive_files(self, folder_id, path_list):
        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
            existing_files = service.files().list(fields='files(id,name,parents)').execute()['files']
        except Exception as err:
            print(err)
            return False

        names_list = {p.name: p for p in path_list}

        for file in existing_files:

            if not file['name'] in names_list:
                continue

            # if parent folder does not match, continue
            if folder_id not in file['parents']:
                continue

            # form path for file
            result_path = names_list[file['name']]

            # request file from google drive and write to local storage
            request = service.files().get_media(fileId=file['id'])
            try:
                with result_path.open('wb+') as fw:
                    downloader = MediaIoBaseDownload(fw, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
            except HttpError as err:
                print('cannot download file \'{0}\' from drive'.format(str(result_path)))
                continue

        return True

    def clear_drive_folder(self, folder: DriveFolder, exceptions=None):

        folder_id = self.init_drive_folder(folder)
        if exceptions is None:
            exceptions = []

        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
            existing_files = service.files().list(fields='files(id,name,parents,mimeType)').execute()['files']
        except Exception as err:
            print(err)
            return False

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
                result = service.files().delete(fileId=file['id']).execute()
                print('deleted {0}'.format(result['name']))
            except HttpError as err:
                print(err.content)

    def update_all_permissions(self):
        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
            existing_files = service.files().list(fields='files(id)').execute()['files']
        except Exception as err:
            print(err)
            return False

        for file in existing_files:
            try:
                service.permissions().create(fileId=file['id'],
                                             body={'type': 'user', 'role': 'writer',
                                                   'emailAddress': self.work_email}).execute()
            except HttpError as err:
                print(err.content)

    def show_folder_files(self, folder: DriveFolder):
        folder_id = self.init_drive_folder(folder)

        try:
            service = discovery.build('drive', 'v3', credentials=self._credentials)
            existing_files = service.files().list(fields='files(name,parents,id)').execute()['files']
        except Exception as err:
            print(err)
            return False

        c = 1  # counter of files
        for file in existing_files:
            if folder_id in file['parents']:
                print('{0}. {1}'.format(c, file))
                c += 1

    @staticmethod
    def save_folder_id(drive_folder, folder_id):
        file = FolderType.DataDriveFolders.value / drive_folder.value
        if not file.exists():
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch()

        try:
            with file.open('w', encoding='utf-8') as fout:
                fout.write(folder_id)
        except Exception:
            print('failed to load id from \"{}\"'.format(file))

    @staticmethod
    def load_folder_id(drive_folder: DriveFolder):
        if drive_folder is None:
            return None

        cloud_id = None
        file = FolderType.DataDriveFolders.value / drive_folder.value
        if file.exists():
            try:
                with file.open('r', encoding='utf-8') as fr:
                    cloud_id = fr.read()
            except Exception:
                print('failed to load id from \"{}\"'.format(file))

        return cloud_id

    @staticmethod
    def get_file_metadata(name, folder_id):
        return {
            'name': name,
            'parents': [folder_id]
        }

    @staticmethod
    def get_folder_metadata(name, parent_folder=None):
        if parent_folder is None:
            return \
                {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
        else:
            return \
                {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_folder]
                }


if __name__ == '__main__':
    os.chdir(r'D:\coding\Python_codes\Queue_Bot')
    DriveSaver().delete_everything_on_disk()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'clear':
            DriveSaver().delete_everything_on_disk()
        elif sys.argv[1] == 'show_data':
            DriveSaver().show_folder_files(DriveFolder.HelperBotData)
        elif sys.argv[1] == 'show_logs':
            DriveSaver().show_folder_files(DriveFolder.Log)
