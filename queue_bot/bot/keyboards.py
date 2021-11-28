from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import queue_bot.commands.create_queue.create_random_from_registered
import queue_bot.commands.create_queue.default_queue_name
import queue_bot.commands.create_queue.set_empty_students
import queue_bot.commands.create_queue.start_create
import queue_bot.commands.create_queue.start_create_random
import queue_bot.commands.general.cancel
import queue_bot.commands.modify_queue.add_student
import queue_bot.commands.modify_queue.clear
import queue_bot.commands.modify_queue.move_position
import queue_bot.commands.modify_queue.move_to_end
import queue_bot.commands.modify_queue.remove_students
import queue_bot.commands.modify_queue.show_for_copy
import queue_bot.commands.modify_queue.swap_students
import queue_bot.commands.modify_registered.add_user
import queue_bot.commands.modify_registered.add_users
import queue_bot.commands.modify_registered.remove_users
import queue_bot.commands.modify_registered.rename_all
import queue_bot.commands.modify_registered.show_users
import queue_bot.commands.update_queue.move_next
import queue_bot.commands.update_queue.move_previous
import queue_bot.commands.update_queue.refresh
from queue_bot.commands import command as commands
import queue_bot.languages.keyboard_names_rus as kb_names


create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=queue_bot.commands.create_queue.start_create.StartCreate.query())],
    [InlineKeyboardButton(kb_names.cancel, callback_data=queue_bot.commands.general.cancel.Cancel.query())]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=queue_bot.commands.create_queue.start_create_random.StartCreateRandom.query())],
    [InlineKeyboardButton(kb_names.create_queue_from_reg, callback_data=queue_bot.commands.create_queue.create_random_from_registered.CreateRandomFromRegistered.query())],
    [InlineKeyboardButton(kb_names.cancel, callback_data=queue_bot.commands.general.cancel.Cancel.query())]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.move_student_to_end, callback_data=queue_bot.commands.modify_queue.move_to_end.MoveStudentToEnd.query())],
    [InlineKeyboardButton(kb_names.swap_places, callback_data=queue_bot.commands.modify_queue.swap_students.MoveSwapStudents.query())],
    [InlineKeyboardButton(kb_names.move_student_to_pos, callback_data=queue_bot.commands.modify_queue.move_position.MoveStudentPosition.query())],
    [InlineKeyboardButton(kb_names.remove_students, callback_data=queue_bot.commands.modify_queue.remove_students.RemoveListStudents.query())],
    [InlineKeyboardButton(kb_names.add_student, callback_data=queue_bot.commands.modify_queue.add_student.AddStudent.query())],
    [InlineKeyboardButton(kb_names.set_queue_position, callback_data=queue_bot.commands.modify_queue.move_position.MoveQueuePosition.query())],
    [InlineKeyboardButton(kb_names.show_queue_for_copy, callback_data=queue_bot.commands.modify_queue.show_for_copy.ShowQueueForCopy.query())],
    [InlineKeyboardButton(kb_names.clear_queue, callback_data=queue_bot.commands.modify_queue.clear.Clear.query())]
])

move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.next, callback_data=queue_bot.commands.update_queue.move_next.MoveNext.query())],
    [InlineKeyboardButton(kb_names.previous, callback_data=queue_bot.commands.update_queue.move_previous.MovePrevious.query())],
    [InlineKeyboardButton(kb_names.refresh, callback_data=queue_bot.commands.update_queue.refresh.Refresh.query())]
])

modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.show_registered, callback_data=queue_bot.commands.modify_registered.show_users.ShowListUsers.query())],
    [InlineKeyboardButton(kb_names.register_user, callback_data=queue_bot.commands.modify_registered.add_user.AddUser.query())],
    [InlineKeyboardButton(kb_names.add_user_list, callback_data=queue_bot.commands.modify_registered.add_users.AddListUsers.query())],
    [InlineKeyboardButton(kb_names.remove_users, callback_data=queue_bot.commands.modify_registered.remove_users.RemoveListUsers.query())],
    [InlineKeyboardButton(kb_names.rename_all_users, callback_data=queue_bot.commands.modify_registered.rename_all.RenameAllUsers.query())]
])

help_subject_choice = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.how_to_select_subject, callback_data=commands.Help.HowToSelectSubject.query())]])

set_default_queue_name = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_default_name, callback_data=queue_bot.commands.create_queue.default_queue_name.DefaultQueueName.query())]])

set_empty_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_no_students, callback_data=queue_bot.commands.create_queue.set_empty_students.SetEmptyStudents.query())]
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
    buttons.append([InlineKeyboardButton(kb_names.cancel, callback_data=queue_bot.commands.general.cancel.Cancel.query())])

    return InlineKeyboardMarkup(buttons)
