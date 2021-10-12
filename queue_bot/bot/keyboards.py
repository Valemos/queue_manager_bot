from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import queue_bot.languages.keyboard_names_rus as kb_names
from queue_bot.command_handling import command_handler as ch
from queue_bot.commands import *

create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=ch.query(CreateSimple))],
    [InlineKeyboardButton(kb_names.cancel, callback_data=ch.query(Cancel))]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=ch.query(CreateRandom))],
    [InlineKeyboardButton(kb_names.create_queue_from_reg, callback_data=ch.query(CreateRandomFromRegistered))],
    [InlineKeyboardButton(kb_names.cancel, callback_data=ch.query(Cancel))]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.move_student_to_end, callback_data=ch.query(MoveStudentToEnd))],
    [InlineKeyboardButton(kb_names.swap_places, callback_data=ch.query(MoveSwapStudents))],
    [InlineKeyboardButton(kb_names.move_student_to_pos, callback_data=ch.query(MoveStudentPosition))],
    [InlineKeyboardButton(kb_names.remove_students, callback_data=ch.query(RemoveListStudents))],
    [InlineKeyboardButton(kb_names.add_student, callback_data=ch.query(AddStudent))],
    [InlineKeyboardButton(kb_names.set_queue_position, callback_data=ch.query(MoveQueuePosition))],
    [InlineKeyboardButton(kb_names.show_queue_for_copy, callback_data=ch.query(ShowQueueForCopy))],
    [InlineKeyboardButton(kb_names.clear_queue, callback_data=ch.query(ClearList))]
])

move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.next, callback_data=ch.query(MoveNext))],
    [InlineKeyboardButton(kb_names.previous, callback_data=ch.query(MovePrevious))],
    [InlineKeyboardButton(kb_names.refresh, callback_data=ch.query(Refresh))]
])

modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.show_registered, callback_data=ch.query(ShowListUsers))],
    [InlineKeyboardButton(kb_names.register_user, callback_data=ch.query(AddUser))],
    [InlineKeyboardButton(kb_names.add_user_list, callback_data=ch.query(AddListUsers))],
    [InlineKeyboardButton(kb_names.remove_users, callback_data=ch.query(RemoveListUsers))],
    [InlineKeyboardButton(kb_names.rename_all_users, callback_data=ch.query(RenameAllUsers))]
])

set_default_queue_name = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_default_name, callback_data=ch.query(DefaultQueueName))]])

set_empty_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_no_students, callback_data=ch.query(SetEmptyStudents))]
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
        buttons.append([InlineKeyboardButton(name, callback_data=ch.query(command, arg))])
    buttons.append([InlineKeyboardButton(kb_names.cancel, callback_data=ch.query(Cancel))])

    return InlineKeyboardMarkup(buttons)
