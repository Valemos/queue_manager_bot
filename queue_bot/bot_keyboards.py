from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from queue_bot import bot_commands as commands

create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Создать очередь',    callback_data=commands.QueuesManage.CreateSimple.str())],
    [InlineKeyboardButton('Отмена',             callback_data=commands.General.Cancel.str())]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Создать очередь',        callback_data=commands.QueuesManage.CreateRandom.str())],
    [InlineKeyboardButton('Создать из записаных',   callback_data=commands.QueuesManage.CreateRandomFromRegistered.str())],
    [InlineKeyboardButton('Отмена',                 callback_data=commands.General.Cancel.str())]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Переместить студента в конец', callback_data=commands.ModifyCurrentQueue.MoveStudentToEnd.str())],
    [InlineKeyboardButton('Поменять местами', callback_data=commands.ModifyCurrentQueue.SwapStudents.str())],
    [InlineKeyboardButton('Поставить студента на позицию', callback_data=commands.ModifyCurrentQueue.SetStudentPosition.str())],
    [InlineKeyboardButton('Удалить студентов', callback_data=commands.ModifyCurrentQueue.RemoveStudentsList.str())],
    [InlineKeyboardButton('Добавить студента', callback_data=commands.ModifyCurrentQueue.AddStudent.str())],
    [InlineKeyboardButton('Установить позицию очереди', callback_data=commands.ModifyCurrentQueue.SetQueuePosition.str())],
    [InlineKeyboardButton('Показать очередь', callback_data=commands.ModifyCurrentQueue.ShowList.str())],
    [InlineKeyboardButton('Установить новую очередь', callback_data=commands.ModifyCurrentQueue.SetStudents.str())],
    [InlineKeyboardButton('Очистить очередь', callback_data=commands.ModifyCurrentQueue.ClearList.str())]
])

move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Следующий',  callback_data=commands.UpdateQueue.MoveNext.str())],
    [InlineKeyboardButton('Предыдущий', callback_data=commands.UpdateQueue.MovePrevious.str())],
    [InlineKeyboardButton('Обновить',   callback_data=commands.UpdateQueue.Refresh.str())]
])

modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton('Показать зарегистрированных',         callback_data=commands.ModifyRegistered.ShowListUsers.str())],
    [InlineKeyboardButton('Зарегистрировать пользователя',       callback_data=commands.ModifyRegistered.AddUser.str())],
    [InlineKeyboardButton('Добавить список пользователей(с ID)', callback_data=commands.ModifyRegistered.AddListUsers.str())],
    [InlineKeyboardButton('Удалить несколько пользователей',     callback_data=commands.ModifyRegistered.RemoveListUsers.str())],
    [InlineKeyboardButton('Переименовать всех пользователей',    callback_data=commands.ModifyRegistered.RenameAllUsers.str())]
])

help_subject_choice = InlineKeyboardMarkup([
    [InlineKeyboardButton('Как выбрать тему?', callback_data=commands.Help.HowToChooseSubject.str())]])

set_default_queue_name = InlineKeyboardMarkup([
    [InlineKeyboardButton('Оставить пустое имя', callback_data=commands.QueuesManage.DefaultQueueName.str())]])
