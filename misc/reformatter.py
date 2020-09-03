import pickle
from pathlib import Path
from queue_bot.registered_manager import StudentsRegisteredManager, Student
from queue_bot.varsaver import FolderType
from queue_bot.registered_manager import AccessLevel

mode = 1

if mode == 1:
    source_file = FolderType.Backup.value / StudentsRegisteredManager._file_registered_users
    registered_file = FolderType.Data.value / FolderType.Data.value / StudentsRegisteredManager._file_registered_users

    with source_file.open('rb') as fin:
        print('registered')
        students = [Student(name, tel_id) for tel_id, name in pickle.load(fin).items()]
        print(students)

    with registered_file.open('wb') as fout:
        pickle.dump(students, fout)

elif mode == 2:
    access_source_file = FolderType.Data.value / Path('owners.data')
    access_levels_path = FolderType.Data.value / StudentsRegisteredManager._file_access_levels

    with access_levels_path.open('rb') as fin:
        access = pickle.load(fin)

    print('access')
    print(access)

    for key in access.keys():
        access[key] = AccessLevel(access[key])

    with access_levels_path.open('wb') as fout:
        pickle.dump(access, fout)
