import os
import json
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from queue_bot.misc.object_file_saver import FolderType


# holds file paths to folder id`s
from queue_bot.misc.drive_folder import DriveFolder

HelperBotData = 0
Log = 1
SubjectChoices = 2
Queues = 3

class DriveSaver:

    folders_config_file = FolderType.Data.value / Path("google_folders_config.json")

    def __init__(self, logger=None):
        self.logger = logger

        self._SCOPES = ['https://www.googleapis.com/auth/drive']
        self._SERVICE_ACCOUNT_FILE = Path(r'/drive_data/queue-bot-key.json')
        self.work_email = 'programworkerbox@gmail.com'

        # credentials must be created after SCOPE and account file was specified
        self._credentials = self.init_credentials()

        # contains dictionary of folder type and fol
        self.folders_id_dict = {}
        # must create main folder first
        self.init_drive_folder(DriveFolder.HelperBotData)

        # than create other folders
        self.init_drive_folder(DriveFolder.Log)
        self.init_drive_folder(DriveFolder.SubjectChoices)
        self.init_drive_folder(DriveFolder.Queues)

    def log(self, string):
        if self.logger is not None:
            self.logger.log(string)

    def init_credentials(self):
        # try read service account file
        if self._SERVICE_ACCOUNT_FILE.resolve().exists():
            return service_account.Credentials.from_service_account_file(self._SERVICE_ACCOUNT_FILE, scopes=self._SCOPES)
        elif 'GOOGLE_CREDS' in os.environ:
            return service_account.Credentials.from_service_account_info(json.loads(os.environ.get('GOOGLE_CREDS')))
        return None

    def init_service(self):
        if self._credentials is None:
            print('credentials empty')
            self.log('credentials empty')
            return None

        try:
            return discovery.build('drive', 'v3', credentials=self._credentials)
        except Exception as err:
            print(err)
            print('service not initialized')
            self.log(err)
            return None

    def init_drive_folder(self, drive_folder):
        folder_id = self.load_folder_id(drive_folder)
        if folder_id is None:
            folder_id = self.create_drive_folder(drive_folder)
            self.save_folder_id(drive_folder, folder_id)
        return folder_id

    def create_drive_folder(self, folder_type):

        service = self.init_service()
        if service is None:
            return None

        if folder_type is DriveFolder.HelperBotData:
            folder_metadata = DriveSaver.get_folder_metadata(folder_type.name)
        else:
            main_folder_id = self.init_drive_folder(DriveFolder.HelperBotData)
            folder_metadata = DriveSaver.get_folder_metadata(folder_type.name, main_folder_id)

        try:
            cloud_folder = service.files().create(body=folder_metadata).execute()
            service.permissions().create(fileId=cloud_folder['id'],
                                         body={'type': 'user', 'role': 'writer',
                                               'emailAddress': self.work_email}).execute()
        except Exception as err:
            print(err)
            self.log(err)
            return None

        return cloud_folder['id']

    def save(self, file_path, folder: DriveFolder):

        service = self.init_service()
        if service is None:
            return False
        folder_id = self.init_drive_folder(folder)
        file_metadata = DriveSaver.get_file_metadata(file_path.name, folder_id)
        return self.upload_to_drive(file_path, file_metadata, service)

    def upload_to_drive(self, file_path, file_metadata, service):
        try:
            upload_file = MediaFileUpload(file_path, mimetype='application/octet-stream')
            service.files().create(body=file_metadata, media_body=upload_file, fields='id').execute()
        except Exception as err:
            print(err)
            self.log(err)
            return False
        return True

    @staticmethod
    def update_on_drive(service, file_path, file_id):
        try:
            update_file = MediaFileUpload(file_path, mimetype='application/octet-stream')
            service.files().update(fileId=file_id, media_body=update_file).execute()
        except HttpError as err:
            print(err.error_details)

    def update_file_list(self, path_list, parent_folder):

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name')

        # update if files exist
        paths_dict = {p.name: p for p in path_list if p.exists()}
        for file in existing_files:
            if file['name'] in paths_dict:
                DriveSaver.update_on_drive(service, paths_dict[file['name']], file['id'])
                del paths_dict[file['name']]

        # download to folder if file does not exists
        parent_folder = self.init_drive_folder(parent_folder)
        for path in paths_dict.values():
            file_metadata = DriveSaver.get_file_metadata(path.name, parent_folder)
            self.upload_to_drive(path, file_metadata, service)
        return True

    @staticmethod
    def get_existing_files(service, fields):
        return service.files().list(fields='files({0})'.format(fields)).execute()['files']

    # if path_list not specified, all files from folder will be written to 'new_folder'
    def get_files_from_drive(self, path_list, drive_folder):
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

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name,parents')

        names_list = {p.name: p for p in path_list}
        for file in existing_files:
            if not file['name'] in names_list:
                continue

            # if parent folder does not match, continue
            if folder_id not in file['parents']:
                continue

            # form path for file
            result_path = names_list[file['name']]
            # create if not exists
            if not result_path.parent.exists():
                result_path.parent.mkdir(parents=True)
            if not result_path.exists():
                result_path.touch(exist_ok=True)

            # request file from google drive and write to local storage
            request = service.files().get_media(fileId=file['id'])
            try:
                with result_path.open('wb+') as fw:
                    downloader = MediaIoBaseDownload(fw, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
            except HttpError:
                string = 'cannot download file \'{0}\' from drive'.format(str(result_path))
                print(string)
                self.log(string)
                continue

        return True

    def delete_all_in_folder(self, folder: DriveFolder, exceptions=None):
        if exceptions is None:
            exceptions = []
        else:
            exceptions = [exc.name for exc in exceptions]

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name,parents,mimeType')

        folder_id = self.init_drive_folder(folder)
        for file in existing_files:
            if file['name'] in exceptions:
                continue

            if 'parents' in file:
                if folder_id not in file['parents']:
                    continue

            if file['mimeType'] != 'application/vnd.google-apps.folder':
                service.files().delete(fileId=file['id']).execute()
                string = 'deleted ' + file['name']
                print(string)
                self.log(string)

        return True

    def delete_from_folder(self, files: list, folder: DriveFolder):
        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name,parents,mimeType')
        file_names = [file.name for file in files]

        folder_id = self.init_drive_folder(folder)
        for file in existing_files:
            if file['name'] in file_names:
                if 'parents' in file:
                    if folder_id not in file['parents']:
                        continue

                if file['mimeType'] != 'application/vnd.google-apps.folder':
                    service.files().delete(fileId=file['id']).execute()
                    string = 'deleted ' + file['name']
                    print(string)
                    self.log(string)

        return True

    def delete_everything_on_disk(self):

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name')

        for file in existing_files:
            try:
                result = service.files().delete(fileId=file['id']).execute()
                string = 'deleted {0}'.format(file['name'])
                print(string)
                self.log(string)
            except HttpError as err:
                string = err.content
                print(string)
                self.log(string)

    def update_all_permissions(self):

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id')

        for file in existing_files:
            try:
                service.permissions().create(fileId=file['id'],
                                             body={'type': 'user', 'role': 'writer',
                                                   'emailAddress': self.work_email}).execute()
            except HttpError as err:
                print(err.content)
                self.log(err.content)

    def show_folder_files(self, folder: DriveFolder):
        folder_id = self.init_drive_folder(folder)

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'name,parents,id')

        c = 1  # counter of files
        for file in existing_files:
            if folder_id in file['parents']:
                print('{0}. {1}'.format(c, file))
                c += 1

    def load_folder_files(self, folder: DriveFolder, output_folder: FolderType):
        folder_id = self.init_drive_folder(folder)

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'name,parents,id')

        path_list = []
        c = 1  # counter of files
        for file in existing_files:
            if folder_id in file['parents']:
                path_list.append(output_folder.value / file['name'])
                c += 1

        return self.download_drive_files(folder_id, path_list)

    def create_folders_config_file(self):
        if not self.folders_config_file.exists():
            self.folders_config_file.parent.mkdir(parents=True, exist_ok=True)
            self.folders_config_file.touch()

    def load_folders_config(self):
        """
        creates config file to store drive folders info
        :return: True if operation succeeded
        """
        self.create_folders_config_file()
        if self.folders_config_file.exists():
            try:
                # normal load of file
                with self.folders_config_file.open(encoding='utf-8') as fin:
                    self.folders_id_dict = json.load(fin)
                return True
            except json.JSONDecodeError:
                # init incorrect file with correct current dictionary
                with self.folders_config_file.open("w", encoding='utf-8') as fout:
                    json.dump(self.folders_id_dict, fout)
                return True
            except Exception:
                # handle any other error during reading
                string = f'failed to read config \"{self.folders_config_file}\"'
                print(string)
                self.log(string)
        else:
            string = f"config file not exists {self.folders_config_file}"
            print(string)
            self.log(string)

        return False

    def save_folder_id(self, drive_folder, folder_id):
        self.folders_id_dict[drive_folder.name] = folder_id
        self.create_folders_config_file()

        try:
            with self.folders_config_file.open('w', encoding='utf-8') as fout:
                json.dump(self.folders_id_dict, fout)

        except Exception:
            string = f'failed to load folder id from \"{self.folders_config_file}\"'
            print(string)
            self.log(string)

    def load_folder_id(self, drive_folder: DriveFolder):
        cloud_id = None
        if drive_folder in self.folders_id_dict:
            cloud_id = self.folders_id_dict[drive_folder.name]
        elif self.load_folders_config():  # load config if folder not found
            if drive_folder in self.folders_id_dict:
                cloud_id = self.folders_id_dict[drive_folder.name]

        return cloud_id

    @staticmethod
    def get_file_metadata(name, folder_id):
        return \
            {
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

    print()

    os.chdir(r'../../')
    # DriveSaver().show_folder_files(DriveFolder.Queues)
    # DriveSaver().load_folder_files(DriveFolder.Log, FolderType.Test)
    # DriveSaver().delete_everything_on_disk()
    # DriveSaver().delete_all_in_folder(DriveFolder.Log)
    if len(sys.argv) == 2:
        if sys.argv[1] == 'clear':
            DriveSaver().delete_everything_on_disk()
        elif sys.argv[1] == 'show_data':
            DriveSaver().show_folder_files(DriveFolder.HelperBotData)
        elif sys.argv[1] == 'show_logs':
            DriveSaver().show_folder_files(DriveFolder.Log)
