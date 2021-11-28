from queue_bot.misc.gdrive_saver import DriveSaver

# DriveSaver().update_all_permissions()
# DriveSaver().show_folder_files(DriveSaver().drive_folder_root.Queues)
# DriveSaver().load_folder_files(DriveFolder.drive_folder_log, FolderType.Test)
# DriveSaver().delete_everything_on_disk()
# DriveSaver().delete_all_in_folder(DriveFolderType.Log)
# DriveSaver().delete_all_in_folder(DriveFolderType.Queues)


# exit(0)

# delete with prompt

saver = DriveSaver()
existing_files = saver.get_existing_files('id,name,parents')


def ask_for_files(existing_files):
    for file in existing_files:
        if file['name'].startswith('log'):
            yield file["id"], file["name"]
        else:
            print(file)
            answer = input(f'Want to delete file? [Y/n]')
            if answer == '' or answer.lower() == 'y':
                yield file["id"], file["name"]


files_to_delete = {file_id: name for file_id, name in ask_for_files(existing_files)}


answer = input(f'Confirm deletion of {len(files_to_delete)} files [Y/n]')
if answer == '' or answer.lower() == 'y':
    for file_id, file_name in files_to_delete.items():
        try:
            saver.init_service().files().delete(fileId=file_id).execute()
            print(f'Deleted {file_name} ({file_id})')
        except Exception:
            print(f'Cannot delete {file_name} ({file_id})')
