
class Translatable:
    def get_language_pack(self):
        raise NotImplementedError


class BotMessages:
    permission_denied = None
    code_not_valid = None
    not_owner = None
    enter_students_list = None
    set_registered_students = None
    del_registered_students = None
    get_user_message = None
    queue_finished = None
    unknown_user = None
    all_known_users = None
    queue_commands = None
    error_in_values = None
    was_not_forwarded = None
    user_register_successfull = None
    queue_not_exists_create_new = None
    create_new_queue = None
    title_edit_queue = None
    title_edit_registered = None
    queue_not_exists = None
    first_user_added = None
    already_requested_send_message = None
    admins_added = None
    bot_already_running = None
    bot_stopped = None
    your_turn_not_now = None
    you_deleted = None
    you_not_found = None
    you_added_to_queue = None
    student_not_found = 'student {0} not found'
    send_student_number_and_new_position = None
    users_deleted = None
    error_in_this_values = None
    send_student_numbers_with_space = None
    not_index_from_queue = None
    student_added_to_end = None
    send_student_number = None
    queue_deleted = None
    position_set = None
    send_new_position = None
    students_set = None
    student_set = None
    students_moved = None
    student_moved = None
    send_student_name_to_end = None
    admin_set = None
    admin_deleted = None
    users_added = None
    enter_new_list_in_order = None
    send_two_positions_students_space = None
    names_more_than_users = None

    def __init__(self):
        for attr in dir(self):
            if not (attr.startswith('__') and attr.endswith('__')):
                if getattr(self, attr) is None:
                    raise NotImplementedError('Message {0} not filled in'.format(attr))
