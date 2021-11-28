from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import queue_bot.commands as commands
from queue_bot import keyboard_names as kb_names


create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=commands.create_queue.StartCreate.query())],
    [InlineKeyboardButton(kb_names.cancel, callback_data=commands.general.Cancel.query())]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=commands.create_queue.StartCreateRandom.query())],
    [InlineKeyboardButton(kb_names.create_queue_from_reg, callback_data=commands.create_queue.CreateRandomFromRegistered.query())],
    [InlineKeyboardButton(kb_names.cancel, callback_data=commands.general.Cancel.query())]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.move_student_to_end, callback_data=commands.modify_queue.MoveStudentToEnd.query())],
    [InlineKeyboardButton(kb_names.swap_places, callback_data=commands.modify_queue.MoveSwapStudents.query())],
    [InlineKeyboardButton(kb_names.move_student_to_pos, callback_data=commands.modify_queue.MoveSwapStudents.query())],
    [InlineKeyboardButton(kb_names.remove_students, callback_data=commands.modify_queue.RemoveListStudents.query())],
    [InlineKeyboardButton(kb_names.add_student, callback_data=commands.modify_queue.add_student.AddStudent.query())],
    [InlineKeyboardButton(kb_names.set_queue_position, callback_data=commands.modify_queue.MoveQueuePosition.query())],
    [InlineKeyboardButton(kb_names.show_queue_for_copy, callback_data=commands.modify_queue.ShowQueueForCopy.query())],
    [InlineKeyboardButton(kb_names.clear_queue, callback_data=commands.modify_queue.Clear.query())]
])

move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.next, callback_data=commands.update_queue.MoveNext.query())],
    [InlineKeyboardButton(kb_names.previous, callback_data=commands.update_queue.MovePrevious.query())],
    [InlineKeyboardButton(kb_names.refresh, callback_data=commands.update_queue.Refresh.query())]
])

modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.show_registered, callback_data=commands.modify_registered.ShowListUsers.query())],
    [InlineKeyboardButton(kb_names.register_user, callback_data=commands.modify_registered.AddUser.query())],
    [InlineKeyboardButton(kb_names.add_user_list, callback_data=commands.modify_registered.AddListUsers.query())],
    [InlineKeyboardButton(kb_names.remove_users, callback_data=commands.modify_registered.RemoveListUsers.query())],
    [InlineKeyboardButton(kb_names.rename_all_users, callback_data=commands.modify_registered.RenameAllUsers.query())]
])

set_default_queue_name = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_default_name, callback_data=commands.create_queue.DefaultQueueName.query())]])

set_empty_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_no_students, callback_data=commands.create_queue.SetEmptyStudents.query())]
])


def generate_keyboard(command, names, arguments=None):
    if arguments is None:
        arguments = names
    else:
        assert len(arguments) == len(names)

    buttons = []
    for name, arg in zip(names, arguments):
        if name == '':
            name = kb_names.no_name
        if len(name) > 30:
            name = name[:30] + '...'
        buttons.append([InlineKeyboardButton(name, callback_data=command.query(arg))])
    buttons.append([InlineKeyboardButton(kb_names.cancel, callback_data=commands.general.Cancel.query())])

    return InlineKeyboardMarkup(buttons)
