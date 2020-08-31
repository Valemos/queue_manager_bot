from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from bot_commands import *

keyboard_reply_create_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Создать очередь',    callback_data=ModifyQueue.CreateSimple.str())],
    [InlineKeyboardButton('Отмена',             callback_data=ModifyQueue.Cancel.str())]])

keyboard_create_random_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Создать очередь',    callback_data=ModifyQueue.CreateRandom.str())],
    [InlineKeyboardButton('Отмена',             callback_data=ModifyQueue.Cancel())]])

keyboard_modify_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Переместить студента в конец',   callback_data=ModifyQueue.MoveStudentToEnd.str())],
    [InlineKeyboardButton('Поменять местами',               callback_data=ModifyQueue.SwapStudents.str())],
    [InlineKeyboardButton('Поставить студента на позицию',  callback_data=ModifyQueue.SetStudentPosition.str())],
    [InlineKeyboardButton('Удалить студентов',              callback_data=ModifyQueue.RemoveStudentsList.str())],
    [InlineKeyboardButton('Добавить студента',              callback_data=ModifyQueue.AddStudent.str())],
    [InlineKeyboardButton('Установить позицию очереди',     callback_data=ModifyQueue.SetQueuePosition.str())],
    [InlineKeyboardButton('Показать очередь',               callback_data=ModifyQueue.ShowList.str())],
    [InlineKeyboardButton('Установить новую очередь',       callback_data=ModifyQueue.SetStudents.str())],
    [InlineKeyboardButton('Очистить очередь',               callback_data=ModifyQueue.ClearList.str())]
])

keyboard_move_queue = InlineKeyboardMarkup([
    [InlineKeyboardButton('Следующий',  callback_data=UpdateQueue.MoveNext.str())],
    [InlineKeyboardButton('Предыдущий', callback_data=UpdateQueue.MovePrevious.str())],
    [InlineKeyboardButton('Обновить',   callback_data=UpdateQueue.Refresh.str())]
])

keyboard_modify_registered = InlineKeyboardMarkup([
    [InlineKeyboardButton('Показать зарегистрированных',            callback_data=ModifyRegistered.ShowListUsers.str())],
    [InlineKeyboardButton('Зарегистрировать пользователя',          callback_data=ModifyRegistered.AddUser.str())],
    [InlineKeyboardButton('Добавить список пользователей(с ID)',    callback_data=ModifyRegistered.AddListUsers.str())],
    [InlineKeyboardButton('Удалить несколько пользователей',        callback_data=ModifyRegistered.RemoveListUsers.str())],
    [InlineKeyboardButton('Переименовать всех пользователей',       callback_data=ModifyRegistered.RenameAllUsers.str())]
])