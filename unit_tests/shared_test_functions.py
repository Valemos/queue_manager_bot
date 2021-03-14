from unittest import mock
from unittest.mock import MagicMock

from telegram import MessageEntity, Chat

from queue_bot.bot.main_bot import QueueBot
from queue_bot.objects.student import Student
from queue_bot.objects.students_queue import StudentsQueue


# generate patched test bot
@mock.patch('queue_bot.bot_telegram_queue.DriveSaver')
@mock.patch('queue_bot.bot_telegram_queue.ObjectSaver')
@mock.patch('queue_bot.bot_telegram_queue.Logger')
@mock.patch('queue_bot.bot_telegram_queue.Updater')
def setup_test_bot(unit_test, *mocks) -> QueueBot:
    bot = QueueBot('0')
    bot.registered_manager.add_user('0', 0)  # god
    bot.registered_manager.set_god(0)
    bot.registered_manager.add_user('1', 1)  # admin
    bot.registered_manager.set_admin(1)
    bot.registered_manager.add_user('2', 2)  # user
    bot.registered_manager.add_user('3', 3)  # user
    bot.registered_manager.add_user('4', 4)  # user
    bot.registered_manager.add_user('5', 5)  # user

    unit_test.addTypeEqualityFunc(Student, students_compare)

    return bot


def students_compare(f, s, msg=None):
    return f.name == s.name and \
           f.telegram_id == s.telegram_id and \
           f.access_level == s.access_level


def setup_test_queue(bot, name, students):
    # be aware of list reference copy in students !
    queue = StudentsQueue(bot)
    queue.name = name
    queue.set_students(list(students))
    bot.queues_manager.add_queue(queue)
    return bot


def setup_test_subject_choices(bot: QueueBot):
    bot.choice_manager.set_choice_group('Name', (1, 15), 2)
    bot.choice_manager.can_choose = True
    return bot


def tg_set_user(update, user_id, user_name=''):
    update.effective_user.full_name = user_name
    update.effective_user.id = user_id

    update.message.from_user.full_name = user_name
    update.message.from_user.username = user_name
    update.message.from_user.id = user_id

    update.effective_message.user.full_name = user_name
    update.effective_message.user.id = user_id

    update.effective_chat.type = Chat.PRIVATE

    update.callback_query = None


def tg_select_command(update, cmd_class, button_args=None):
    update.callback_query = MagicMock()
    update.callback_query.data = cmd_class.query(button_args)


def tg_write_message(update, contents):
    update.message.text = contents
    update.callback_query = None


def tg_forward_message(update, user_id, user_name):
    update.message.forward_from.id = user_id
    update.message.forward_from.full_name = user_name


def tg_set_callback_query(update, query):
    update.callback_query = MagicMock()
    update.callback_query.data = query


def get_command_entity(start, length):
    entity = MagicMock()
    entity.type = MessageEntity.BOT_COMMAND
    entity.offset = start
    entity.length = length
    return entity


def bot_handle_message(bot, contents, update, context):
    tg_write_message(update, contents)
    bot.handle_message_reply_command(update, context)


def bot_request_command_send_msg(bot, command, update, context):
    if command.command_name is None:
        raise ValueError('Bot command name is None')

    tg_write_message(update, '/' + command.command_name)
    update.message.entities = [get_command_entity(0, len(command.command_name) + 1)]
    bot.handle_text_command(update, context)


def bot_request_command(bot, command, update, context, command_additions=''):

    if command.command_name is not None:
        if command_additions != '':
            tg_write_message(update, '/' + command.command_name + ' ' + command_additions)
        else:
            tg_write_message(update, '/' + command.command_name)

        update.message.entities = [get_command_entity(0, len(command.command_name) + 1)]

    bot.handle_text_command(update, context)


def bot_handle_text_command(bot, update, context, text):

    # find command
    start = text.index('/')
    command_len = 0
    for i in range(start, len(text)):
        if text[i] != ' ':
            command_len += 1
        else:
            break

    tg_write_message(update, text)
    update.message.entities = [get_command_entity(start, command_len)]
    bot.handle_text_command(update, context)


def bot_handle_keyboard(bot: QueueBot, update, context, command, args=None):
    tg_select_command(update, command, args)
    bot.handle_keyboard_chosen(update, context)
