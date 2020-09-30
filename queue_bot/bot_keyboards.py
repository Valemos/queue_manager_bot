from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from queue_bot import bot_commands as commands
import queue_bot.languages.keyboard_names_rus as kb_names


create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=commands.ManageQueues.CreateSimple.str())],
    [InlineKeyboardButton(kb_names.cancel,          callback_data=commands.General.Cancel.str())]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.create_queue, callback_data=commands.ManageQueues.CreateRandom.str())],
    [InlineKeyboardButton(kb_names.create_queue_from_reg, callback_data=commands.ManageQueues.CreateRandomFromRegistered.str())],
    [InlineKeyboardButton(kb_names.cancel,                 callback_data=commands.General.Cancel.str())]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.move_student_to_end, callback_data=commands.ModifyCurrentQueue.MoveStudentToEnd.str())],
    [InlineKeyboardButton(kb_names.swap_places, callback_data=commands.ModifyCurrentQueue.SwapStudents.str())],
    [InlineKeyboardButton(kb_names.move_student_to_pos, callback_data=commands.ModifyCurrentQueue.SetStudentPosition.str())],
    [InlineKeyboardButton(kb_names.remove_students, callback_data=commands.ModifyCurrentQueue.RemoveListStudents.str())],
    [InlineKeyboardButton(kb_names.add_student, callback_data=commands.ModifyCurrentQueue.AddStudent.str())],
    [InlineKeyboardButton(kb_names.set_queue_position, callback_data=commands.ModifyCurrentQueue.SetQueuePosition.str())],
    [InlineKeyboardButton(kb_names.show_queue_for_copy, callback_data=commands.ModifyCurrentQueue.ShowQueueForCopy.str())],
    [InlineKeyboardButton(kb_names.set_new_queue, callback_data=commands.ModifyCurrentQueue.SetStudents.str())],
    [InlineKeyboardButton(kb_names.clear_queue, callback_data=commands.ModifyCurrentQueue.ClearList.str())]
])

move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.next,  callback_data=commands.UpdateQueue.MoveNext.str())],
    [InlineKeyboardButton(kb_names.previous, callback_data=commands.UpdateQueue.MovePrevious.str())],
    [InlineKeyboardButton(kb_names.refresh,   callback_data=commands.UpdateQueue.Refresh.str())]
])

modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.show_registered,         callback_data=commands.ModifyRegistered.ShowListUsers.str())],
    [InlineKeyboardButton(kb_names.register_user,       callback_data=commands.ModifyRegistered.AddUser.str())],
    [InlineKeyboardButton(kb_names.add_user_list, callback_data=commands.ModifyRegistered.AddListUsers.str())],
    [InlineKeyboardButton(kb_names.remove_users, callback_data=commands.ModifyRegistered.RemoveListUsers.str())],
    [InlineKeyboardButton(kb_names.rename_all_users,    callback_data=commands.ModifyRegistered.RenameAllUsers.str())]
])

help_subject_choice = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.how_to_select_subject, callback_data=commands.Help.HowToSelectSubject.str())]])

set_default_queue_name = InlineKeyboardMarkup([
    [InlineKeyboardButton(kb_names.set_default_name, callback_data=commands.ManageQueues.DefaultQueueName.str())]])


def generate_keyboard(command, names, arguments=None):
    if arguments is None:
        arguments = names
    else:
        assert len(arguments) == len(names)

    buttons = []
    for name, arg in zip(names, arguments):
        if name == '':
            name = kb_names.no_name
        buttons.append([InlineKeyboardButton(name, callback_data=command.str(arg))])
    buttons.append([InlineKeyboardButton(kb_names.cancel, callback_data=commands.General.Cancel.str())])

    return InlineKeyboardMarkup(buttons)
