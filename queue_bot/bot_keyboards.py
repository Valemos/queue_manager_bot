from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from queue_bot import bot_commands as commands
import queue_bot.languages.keyboard_names_rus as kb_names


create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=commands.CreateQueue.CreateSimple.query())],
    [InlineKeyboardButton(kb_names.cancel, callback_data=commands.General.Cancel.query())]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=commands.CreateQueue.CreateRandom.query())],
    [InlineKeyboardButton(kb_names.create_queue_from_reg, callback_data=commands.CreateQueue.CreateRandomFromRegistered.query())],
    [InlineKeyboardButton(kb_names.cancel, callback_data=commands.General.Cancel.query())]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.move_student_to_end, callback_data=commands.ModifyCurrentQueue.MoveStudentToEnd.query())],
    [InlineKeyboardButton(kb_names.swap_places, callback_data=commands.ModifyCurrentQueue.SwapStudents.query())],
    [InlineKeyboardButton(kb_names.move_student_to_pos, callback_data=commands.ModifyCurrentQueue.SetStudentPosition.query())],
    [InlineKeyboardButton(kb_names.remove_students, callback_data=commands.ModifyCurrentQueue.RemoveListStudents.query())],
    [InlineKeyboardButton(kb_names.add_student, callback_data=commands.ModifyCurrentQueue.AddStudent.query())],
    [InlineKeyboardButton(kb_names.set_queue_position, callback_data=commands.ModifyCurrentQueue.SetQueuePosition.query())],
    [InlineKeyboardButton(kb_names.show_queue_for_copy, callback_data=commands.ModifyCurrentQueue.ShowQueueForCopy.query())],
    [InlineKeyboardButton(kb_names.set_new_queue, callback_data=commands.ModifyCurrentQueue.SetStudents.query())],
    [InlineKeyboardButton(kb_names.clear_queue, callback_data=commands.ModifyCurrentQueue.ClearList.query())]
])

move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.next, callback_data=commands.UpdateQueue.MoveNext.query())],
    [InlineKeyboardButton(kb_names.previous, callback_data=commands.UpdateQueue.MovePrevious.query())],
    [InlineKeyboardButton(kb_names.refresh, callback_data=commands.UpdateQueue.Refresh.query())]
])

modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.show_registered, callback_data=commands.ModifyRegistered.ShowListUsers.query())],
    [InlineKeyboardButton(kb_names.register_user, callback_data=commands.ModifyRegistered.AddUser.query())],
    [InlineKeyboardButton(kb_names.add_user_list, callback_data=commands.ModifyRegistered.AddListUsers.query())],
    [InlineKeyboardButton(kb_names.remove_users, callback_data=commands.ModifyRegistered.RemoveListUsers.query())],
    [InlineKeyboardButton(kb_names.rename_all_users, callback_data=commands.ModifyRegistered.RenameAllUsers.query())]
])

help_subject_choice = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.how_to_select_subject, callback_data=commands.Help.HowToSelectSubject.query())]])

set_default_queue_name = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_default_name, callback_data=commands.CreateQueue.DefaultQueueName.query())]])


def generate_keyboard(command, names, arguments=None):
    if arguments is None:
        arguments = names
    else:
        assert len(arguments) == len(names)

    buttons = []
    for name, arg in zip(names, arguments):
        if name == '':
            name = kb_names.no_name
        buttons.append([InlineKeyboardButton(name, callback_data=command.query(arg))])
    buttons.append([InlineKeyboardButton(kb_names.cancel, callback_data=commands.General.Cancel.query())])

    return InlineKeyboardMarkup(buttons)
