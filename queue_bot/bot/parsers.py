from queue_bot.objects.student import Student
from parse import parse

import queue_bot.languages.bot_messages_rus as language_pack


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
    return [name for name in names if name != '' and check_student_name(name)]


def parse_number_range(text):
    result = parse('{0}-{1}', text)
    if result is not None:
        try:
            return int(result[0]), int(result[1])
        except ValueError:
            return None, None
    else:
        return None, None


def parse_integer(text):
    try:
        return int(text)
    except ValueError:
        return None


def check_queue_name(text):
    return not (' ' in text or '\n' in text or len(text) > 60)


def check_student_name(text):
    return len(text) <= 40


def parse_student(string: str):
    if string is not None:
        if string[:4] == 'None':
            if check_student_name(string[4:]):
                return Student(str(string[4:]), None)
        elif len(string) >= 8:
            if check_student_name(string[8:]):
                return Student(string[8:], int(string[:8], 16))
    return None


def parse_queue_message(message_text):
    result = parse(language_pack.copy_queue_format, message_text)
    if result is not None:
        return result['name'], parse_names(result['students'])
    else:
        # trim command if present
        if message_text.startswith('/new_queue'):
            message_text = message_text[len('/new_queue') + 1:]
            return None, parse_names(message_text)
        else:
            return None, None


def is_single_queue_command(message_text):
    return parse(language_pack.copy_queue_format, message_text) is not None
