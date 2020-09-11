from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from queue_bot import bot_commands as commands

create_simple_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Создать очередь',    callback_data=commands.ModifyQueue.CreateSimple.str())],
    [InlineKeyboardButton('Отмена',             callback_data=commands.ModifyQueue.Cancel.str())]])

create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Создать очередь',        callback_data=commands.ModifyQueue.CreateRandom.str())],
    [InlineKeyboardButton('Создать из записаных',   callback_data=commands.ModifyQueue.CreateRandomFromRegistered.str())],
    [InlineKeyboardButton('Отмена',                 callback_data=commands.ModifyQueue.Cancel.str())]])

modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Переместить студента в конец',   callback_data=commands.ModifyQueue.MoveStudentToEnd.str())],
    [InlineKeyboardButton('Поменять местами',               callback_data=commands.ModifyQueue.SwapStudents.str())],
    [InlineKeyboardButton('Поставить студента на позицию',  callback_data=commands.ModifyQueue.SetStudentPosition.str())],
    [InlineKeyboardButton('Удалить студентов',              callback_data=commands.ModifyQueue.RemoveStudentsList.str())],
    [InlineKeyboardButton('Добавить студента',              callback_data=commands.ModifyQueue.AddStudent.str())],
    [InlineKeyboardButton('Установить позицию очереди',     callback_data=commands.ModifyQueue.SetQueuePosition.str())],
    [InlineKeyboardButton('Показать очередь',               callback_data=commands.ModifyQueue.ShowList.str())],
    [InlineKeyboardButton('Установить новую очередь',       callback_data=commands.ModifyQueue.SetStudents.str())],
    [InlineKeyboardButton('Очистить очередь',               callback_data=commands.ModifyQueue.ClearList.str())]
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
    [InlineKeyboardButton('Как выбрать тему?', callback_data=commands.Help.HowToChooseSubject.str())]
])
