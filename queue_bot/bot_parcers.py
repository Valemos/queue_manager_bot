from queue_bot.students_queue import Student


# find students
def parse_students(students_str):
    if '\n' in students_str:
        names = students_str.split('\n')
    else:
        names = [students_str]

    students = []
    for name in names:
        user = self.main_bot.registered_manager.get_user_by_name(name)
        if user is None:
            students.append(self.main_bot.registered_manager.find_similar_student(name))
        else:
            students.append(user)
    return students


def parse_positions_list(string, max_index, min_index=0):
    if ' ' in string:
        index_str = string.split(' ')
    else:
        index_str = [string]

    err_list = []
    correct_indexes = []

    for pos_str in index_str:
        try:
            position = int(pos_str)
            if min_index < position <= max_index:
                correct_indexes.append(position)
            else:
                err_list.append(pos_str)
        except ValueError:
            err_list.append(pos_str)

    return correct_indexes, err_list


def parse_users(string: str):
    if '\n' in string:
        new_users_str_lines = string.split('\n')
    else:
        new_users_str_lines = [string]

    err_list = []
    new_users = []

    for line in new_users_str_lines:
        try:
            user_temp = line.split('-')
            new_users.append(Student(user_temp[0], int(user_temp[1])))
        except ValueError:
            err_list.append(line)

    return new_users, err_list


def parse_names(string):
    if '\n' in string:
        names = string.split('\n')
    else:
        names = [string]
    return names


def parce_number_range(text):
    if '-' in text:
        try:
            parts = text.split('-')
            return int(parts[0]), int(parts[1])
        except ValueError:
            return None, None


def parce_integer(text):
    try:
        return int(text)
    except ValueError:
        return None
