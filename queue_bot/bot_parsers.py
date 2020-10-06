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
    parse_results = parse(Student.student_format, argument)

    if parse_results is not None:
        name, tg_id = parse_results[0], parse_results[1]

        if tg_id == 'None':
            tg_id = None
        else:
            tg_id = int(tg_id)

        return Student(name, tg_id)
    else:
        return None


def parse_queue_message(message_text):
    result = parse(StudentsQueue.copy_queue_format, message_text)
    if result is not None:
        return result['name'], parse_names(result['students'])
    else:
        # trim command if present
        if message_text.startswith('/new_queue'):
            message_text = message_text[len('/new_queue') + 1:]
        return None, parse_names(message_text)


def parse_valid_queue_names(all_names):
    result_names = []

    # for each file format we write in dict true
    parsed_names = {}

    def handle_name(parced_value, format):
        if parced_value not in parsed_names:
            parsed_names[parced_value] = {}
        parsed_names[parced_value][format] = True

    # for each file there are some complementary files with other format
    for name in all_names:
        parse_result = parse(StudentsQueue.file_format_queue, name)
        if parse_result is not None:
            handle_name(parse_result[0], StudentsQueue.file_format_queue)
        else:
            parse_result = parse(StudentsQueue.file_format_queue_state, name)
            if parse_result is not None:
                handle_name(parse_result[0], StudentsQueue.file_format_queue_state)

    for name, parsed in parsed_names.items():
        if parsed[StudentsQueue.file_format_queue] and \
           parsed[StudentsQueue.file_format_queue_state]:
            result_names.append(name)

    return result_names
