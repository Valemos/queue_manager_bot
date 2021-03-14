from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from queue_bot.commands import help, general, create_queue, \
    modify_queue as modify_queue_m, \
    modify_registered as modify_registered_m, \
    update_queue
from queue_bot.commands import command_handler as ch

import queue_bot.languages.keyboard_names_rus as kb_names

create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=ch.query(create_queue.CreateSimple))],
    [InlineKeyboardButton(kb_names.cancel, callback_data=ch.query(general.Cancel))]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=ch.query(create_queue.CreateRandom))],
    [InlineKeyboardButton(kb_names.create_queue_from_reg, callback_data=ch.query(create_queue.CreateRandomFromRegistered))],
    [InlineKeyboardButton(kb_names.cancel, callback_data=ch.query(general.Cancel))]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.move_student_to_end, callback_data=ch.query(modify_queue_m.MoveStudentToEnd))],
    [InlineKeyboardButton(kb_names.swap_places, callback_data=ch.query(modify_queue_m.MoveSwapStudents))],
    [InlineKeyboardButton(kb_names.move_student_to_pos, callback_data=ch.query(modify_queue_m.MoveStudentPosition))],
    [InlineKeyboardButton(kb_names.remove_students, callback_data=ch.query(modify_queue_m.RemoveListStudents))],
    [InlineKeyboardButton(kb_names.add_student, callback_data=ch.query(modify_queue_m.AddStudent))],
    [InlineKeyboardButton(kb_names.set_queue_position, callback_data=ch.query(modify_queue_m.MoveQueuePosition))],
    [InlineKeyboardButton(kb_names.show_queue_for_copy, callback_data=ch.query(modify_queue_m.ShowQueueForCopy))],
    [InlineKeyboardButton(kb_names.clear_queue, callback_data=ch.query(modify_queue_m.ClearList))]
])

move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.next, callback_data=ch.query(update_queue.MoveNext))],
    [InlineKeyboardButton(kb_names.previous, callback_data=ch.query(update_queue.MovePrevious))],
    [InlineKeyboardButton(kb_names.refresh, callback_data=ch.query(update_queue.Refresh))]
])

modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.show_registered, callback_data=ch.query(modify_registered_m.ShowListUsers))],
    [InlineKeyboardButton(kb_names.register_user, callback_data=ch.query(modify_registered_m.AddUser))],
    [InlineKeyboardButton(kb_names.add_user_list, callback_data=ch.query(modify_registered_m.AddListUsers))],
    [InlineKeyboardButton(kb_names.remove_users, callback_data=ch.query(modify_registered_m.RemoveListUsers))],
    [InlineKeyboardButton(kb_names.rename_all_users, callback_data=ch.query(modify_registered_m.RenameAllUsers))]
])

help_subject_choice = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.how_to_select_subject, callback_data=ch.query(help.HowToSelectSubject))]])

set_default_queue_name = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_default_name, callback_data=ch.query(create_queue.DefaultQueueName))]])

set_empty_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_no_students, callback_data=ch.query(create_queue.SetEmptyStudents))]
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
    buttons.append([InlineKeyboardButton(kb_names.cancel, callback_data=ch.query(general.Cancel))])

    return InlineKeyboardMarkup(buttons)
