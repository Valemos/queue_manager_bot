from pathlib import Path
from varsaver import VariableSaver

class RegisteredManager:

    file_save_path = Path('data/registered.data')
    _students_reg = []

    def __init__(self, students=None):
        if students is None:
            self._students_reg = []

    def get_registered_from_file(self, variable_loader):
        self._students_reg = variable_loader.load(self.file_save_path)

    def get_users_str(self):
        str_list = []
        i = 1
        for student in self._students_reg:
            str_list.append('{0}. {1}-{2}'.format(i, student.name, str(student.get_id())))
            i += 1

        return 'Все известные пользователи:\n' + '\n'.join(str_list)
