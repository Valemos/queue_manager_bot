from queue_bot.student import Student
from parse import parse

from queue_bot.students_queue import StudentsQueue


def parse_positions_list(string, min_index, max_index):
    if ' ' in string:
        index_str = string.split(' ')
    else:
        index_str = [string]

    err_list = []
    correct_indexes = []

    for pos_str in index_str:
        try:
            position = int(pos_str)
            if min_index <= position <= max_index:
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
    return [name for name in names if not name == '']


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


def check_queue_name(text):
    if ' ' in text or '\n' in text or len(text) > 100:
        return False
    return True


def parse_student(argument):
    name, tg_id = parse(Student.student_format, argument)

    if tg_id == 'None':
        tg_id = None
    else:
        tg_id = int(tg_id)

    return Student(name, tg_id)


def parse_queue_message(message):
    result = parse(StudentsQueue.copy_queue_format, message)
    if result is not None:
        return result['name'], parse_names(result['students'])
    else:
        return None, None
