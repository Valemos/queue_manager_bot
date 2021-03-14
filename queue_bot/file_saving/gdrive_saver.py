import enum
import os
import json
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from queue_bot.file_saving.object_file_saver import FolderType

# holds file paths to folder_type id`s
from queue_bot.file_saving.drive_folder import DriveFolder


"""
to improve outside of class code readability and have flexible folder_type objects
for each index of this enum user MUST place corresponding DriveFolder object in 
self.drive_folder_type_tuple of DriveSaver object instance

or else possible KeyErrors due to non existent folder_type objects
"""
class DriveFolderType(enum.Enum):
    Root = 0
    Log = 1
    Queues = 2


class DriveSaver:

    folders_config_file = FolderType.Data.value / Path("google_drive_folders.json")

    def __init__(self, logger=None):
        self.logger = logger

        # _SERVICE_ACCOUNT_FILE usage can be replaced with environment variable
        self._SERVICE_ACCOUNT_FILE = Path(r'drive_data/queue-bot-key.json')

        self._SCOPES = ['https://www.googleapis.com/auth/drive']
        self.work_email = 'programworkerbox@gmail.com'

        # credentials must be created after SCOPE and account file was specified
        self._credentials = self.init_credentials()

        # these variables correspond to
        self.drive_folder_root = DriveFolder("HelperBot")
        self.drive_folder_queues = self.drive_folder_root.Queues
        self.drive_folder_log = self.drive_folder_root.Log

        """DriveFolderType constant enum tuple to get DriveFolder objects from it"""
        self.drive_folder_type_tuple = (self.drive_folder_root,
                                        self.drive_folder_log,
                                        self.drive_folder_queues)

        # load DriveFolder tree from json file
        self.load_folders_config()

    def log(self, string):
        print(string)
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
            self.log('credentials empty')
            return None

        try:
            return discovery.build('drive', 'v3', credentials=self._credentials)
        except Exception as err:
            print(err)
            print('service not initialized')
            self.log(err)
            return None

    def get_folder_for_type(self, folder_type: DriveFolderType):
        return self.drive_folder_type_tuple[folder_type.value]

    def get_folder_type_id(self, folder_type: DriveFolderType):
        """Performs check for folder_type object drive id and if None, creates new folder_type on google drive for it"""
        folder = self.get_folder_for_type(folder_type)
        if folder.drive_id is None:
            folder.drive_id = self.create_drive_folder(folder)
            self.save_folders_config()
        return folder.drive_id

    def create_drive_folder(self, folder: DriveFolder):
        """
        Does not check if folder_type already exists on drive

        Creates parent folder_type with this function if it needed

        Creates folder_type for current DriveFolder object on Google Drive and returns resulting id

        :param folder:
        :return: id of newly created folder_type
        """
        service = self.init_service()
        if service is None:
            return None

        parent_id = None
        if folder.parent is not None:  # skip if it is root folder
            if folder.parent.drive_id is None:
                folder.parent.drive_id = self.create_drive_folder(folder.parent)
            parent_id = folder.parent.drive_id

        folder_metadata = DriveSaver.get_folder_metadata(folder.name, parent_id)

        try:
            cloud_folder = service.files().create(body=folder_metadata).execute()
            service.permissions().create(fileId=cloud_folder['id'],
                                         body={'type': 'user', 'role': 'writer',
                                               'emailAddress': self.work_email}).execute()
        except Exception as err:
            self.log(err.args)
            return None

        self.log(f"created folder {folder.name} with id {cloud_folder['id']}")
        return cloud_folder['id']

    def save(self, file_path, folder_type: DriveFolderType):

        service = self.init_service()
        if service is None:
            return False
        folder_id = self.get_folder_type_id(folder_type)
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

    def update_file_list(self, path_list, folder_type: DriveFolderType):

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

        # download to folder_type if file does not exists
        folder_id = self.get_folder_type_id(folder_type)
        for path in paths_dict.values():
            file_metadata = DriveSaver.get_file_metadata(path.name, folder_id)
            self.upload_to_drive(path, file_metadata, service)
        return True

    @staticmethod
    def get_existing_files(service, fields):
        return service.files().list(fields='files({0})'.format(fields)).execute()['files']

    # if path_list not specified, all files from folder_type will be written to 'new_folder'
    def get_folder_files(self, path_list, folder_type: DriveFolderType):
        if len(path_list) == 0:
            return True

        if self._credentials is None:
            return False

        folder_id = self.get_folder_type_id(folder_type)
        if folder_id is None:
            return False

        # create folders on local drive
        for path in path_list:
            if not path.parent.exists():
                path.parent.mkdir(parents=True)

        return self.download_drive_files(folder_id, path_list)

    def download_drive_files(self, folder_id, path_list):

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name,parents')

        names_list = {p.name: p for p in path_list}
        for file in existing_files:
            if not file['name'] in names_list:
                continue

            # if parent folder_type does not match, continue
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
                string = f"cannot download file '{result_path}' from drive"
                self.log(string)
                continue

        return True

    def delete_all_in_folder(self, folder_type: DriveFolderType, exceptions=None):
        if exceptions is None:
            exceptions = []
        else:
            exceptions = [exc.name for exc in exceptions]

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name,parents,mimeType')

        folder_id = self.get_folder_type_id(folder_type)
        for file in existing_files:
            if file['name'] in exceptions:
                continue

            if 'parents' in file:
                if folder_id not in file['parents']:
                    continue

            if file['mimeType'] != 'application/vnd.google-apps.folder_type':
                service.files().delete(fileId=file['id']).execute()
                self.log(f"deleted {file['name']}")


        return True

    def delete_from_folder(self, files: list, folder_type: DriveFolderType):
        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name,parents,mimeType')
        file_names = [file.name for file in files]

        folder_id = self.get_folder_type_id(folder_type)
        for file in existing_files:
            if file['name'] in file_names:
                if 'parents' in file:
                    if folder_id not in file['parents']:
                        continue

                if file['mimeType'] != 'application/vnd.google-apps.folder_type':
                    service.files().delete(fileId=file['id']).execute()
                    self.log(f"deleted {file['name']}")

        return True

    def delete_everything_on_disk(self):

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'id,name')

        for file in existing_files:
            try:
                result = service.files().delete(fileId=file['id']).execute()
                self.log(f"deleted {file['name']}")
            except HttpError as err:
                if err.resp.status == 404:
                    continue
                else:
                    self.log(err.resp.status)

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

    def show_folder_files(self, folder_type: DriveFolderType):
        folder_id = self.get_folder_type_id(folder_type)

        service = self.init_service()
        if service is None:
            return False

        existing_files = DriveSaver.get_existing_files(service, 'name,parents,id')

        c = 1  # counter of files
        for file in existing_files:
            if folder_id in file['parents']:
                print('{0}. {1}'.format(c, file))
                c += 1

    def get_all_folder_files(self, folder_type: DriveFolderType, output_folder: FolderType):
        folder_id = self.get_folder_type_id(folder_type)

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
                    self.drive_folder_root.update_from_json_dict(json.load(fin))
                    return True

            except json.JSONDecodeError:
                # init incorrect file with correct current dictionary
                with self.folders_config_file.open("w+", encoding='utf-8') as fout:
                    json.dump(self.drive_folder_root.to_json_dict(), fout)
                    return True

            except Exception:
                # handle any other error during reading
                string = f'failed to read config file "{self.folders_config_file}"'

            self.log(string)
        else:
            string = f'config file not exists "{self.folders_config_file}"'
            self.log(string)

        return False

    def save_folders_config(self):
        self.create_folders_config_file()
        try:
            with self.folders_config_file.open('w', encoding='utf-8') as fout:
                json.dump(self.drive_folder_root.to_json_dict(), fout)

        except Exception:
            string = f'failed to save folder_type config \"{self.folders_config_file}\"'
            self.log(string)

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
    os.chdir(r'D:\coding\Python_codes\Queue_Bot')

    # DriveSaver().show_folder_files(DriveSaver().drive_folder_queues)
    # DriveSaver().load_folder_files(DriveFolder.drive_folder_log, FolderType.Test)
    # DriveSaver().delete_everything_on_disk()
    DriveSaver().delete_all_in_folder(DriveFolderType.Log)
    DriveSaver().delete_all_in_folder(DriveFolderType.Queues)
