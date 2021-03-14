import pickle
import os
from queue_bot.registered_manager import StudentsRegisteredManager
from queue_bot.objects.student import Student
from queue_bot.file_saving.object_file_saver import FolderType
from queue_bot.registered_manager import AccessLevel

os.chdir('../')

mode = 1

if mode == 1:
    source_file = FolderType.Data.value / StudentsRegisteredManager._file_registered_users
    registered_file = FolderType.Data.value / StudentsRegisteredManager._file_registered_users

    with source_file.open('rb') as fin:
        print('registered')
        students = [Student(name, tel_id) for tel_id, name in pickle.load(fin).items()]
        print(students)

    with registered_file.open('wb') as fout:
        pickle.dump(students, fout)

elif mode == 2:
    access_source_file = FolderType.Data.value / StudentsRegisteredManager._file_access_levels
    access_levels_path = FolderType.Data.value / StudentsRegisteredManager._file_access_levels

    with access_levels_path.open('rb') as fin:
        access = pickle.load(fin)

    print('access')
    print(access)

    for key in access.keys():
        access[key] = AccessLevel(access[key])

    print(access)

    with access_levels_path.open('wb') as fout:
        pickle.dump(access, fout)
