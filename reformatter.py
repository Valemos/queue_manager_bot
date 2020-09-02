import pickle
from pathlib import Path
from registered_manager import StudentsRegisteredManager, Student
from varsaver import FolderType
from bot_access_levels import AccessLevel


registered_file = FolderType.Data.value / StudentsRegisteredManager._file_registered_users

with registered_file.open('rb') as fin:
    print('registered')
    students = [Student(name, st_id) for st_id, name in pickle.load(fin).items()]
    print(students)

with registered_file.open('wb') as fout:
    pickle.dump(students, fout)

access_source_file = FolderType.Data.value / Path('owners.data')
access_levels_path = FolderType.Data.value / StudentsRegisteredManager._file_access_levels

with access_levels_path.open('rb') as fin:
    access = pickle.load(fin)

print('access')
print(access)

# for key in access.keys():
#     access[key] = AccessLevel(access[key])
#
# with access_levels_path.open('wb') as fout:
#     pickle.dump(access, fout)
