import os
import pathlib
from unittest.mock import MagicMock
import mock
import unittest

from queue_bot import bot_parsers
from queue_bot.bot_access_levels import AccessLevel
from queue_bot.students_queue import StudentsQueue, Student
from queue_bot.queue_telegram_bot import QueueBot
import queue_bot.bot_commands as commands

from telegram import Chat, MessageEntity


def students_compare(f, s, msg=None):
    return f.name == s.name and \
           f.telegram_id == s.telegram_id and \
           f.access_level == s.access_level


def setup_test_bot(unit_test) -> QueueBot:
    bot = QueueBot('0')
    bot.registered_manager.append_new_user('0', 0)  # god
    bot.registered_manager.set_god(0)
    bot.registered_manager.append_new_user('1', 1)  # admin
    bot.registered_manager.set_admin(1)
    bot.registered_manager.append_new_user('2', 2)  # user
    bot.registered_manager.append_new_user('3', 3)  # user
    bot.registered_manager.append_new_user('4', 4)  # user
    bot.registered_manager.append_new_user('5', 5)  # user

    unit_test.addTypeEqualityFunc(Student, students_compare)

    return bot


def setup_test_queue(bot, name, students):
    # be aware of list reference copy in students !
    queue = StudentsQueue(bot)
    queue.name = name
    queue.set_students(list(students))
    bot.queues_manager.add_queue(queue)
    return bot


def setup_bot_and_queue(unit_test):
    bot = setup_test_bot(unit_test)
    queue_students = list(bot.registered_manager.get_users())
    queue_students.insert(3, Student('t', None))
    bot = setup_test_queue(bot, 'test', queue_students)

    update = MagicMock()
    context = MagicMock()

    tg_set_user(update, 1)
    return bot, queue_students, update, context


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


def bot_request_command_send_msg(bot, command, update, context):
    if command.command_name is None:
        raise ValueError('Bot command name is None')

    tg_write_message(update, '/' + command.command_name)
    update.message.entities = [get_command_entity(0, len(command.command_name) + 1)]
    bot.handle_command_selected(update, context)


def bot_request_command(bot, command, update, context, command_additions=''):
    if command.command_name is None:
        raise ValueError('Bot command name is None')


    if command_additions != '':
        tg_write_message(update, '/' + command.command_name + ' ' + command_additions)
    else:
        tg_write_message(update, '/' + command.command_name)

    update.message.entities = [get_command_entity(0, len(command.command_name) + 1)]
    bot.handle_command_selected(update, context)


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
    bot.handle_command_selected(update, context)


class TestQueue(unittest.TestCase):

    def test_students_equality(self):
        s1 = Student('name1', 1)
        s2 = Student('name2', 1)
        self.assertTrue(s1 == s2)

        s1 = Student('name1', None)
        s2 = Student('name1', None)
        self.assertTrue(s1 == s2)

        s1 = Student('name1', None)
        s2 = Student('name2', None)
        self.assertFalse(s1 == s2)

        s1 = Student('name1', 1)
        s2 = Student('name1', None)
        self.assertFalse(s1 == s2)

        s1 = Student('name1', 1)
        s2 = Student('name1', 3)
        self.assertFalse(s1 == s2)

        s1 = Student('name1', 1)
        s2 = Student('name2', 3)
        self.assertFalse(s1 == s2)

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_no_starting_queue(self, *mocks):
        bot = setup_test_bot(self)

        self.assertEqual(0, len(bot.queues_manager))

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 2)
        bot_request_command_send_msg(bot, commands.ModifyCurrentQueue.StudentFinished, update, context)
        bot_request_command_send_msg(bot, commands.ModifyCurrentQueue.RemoveMe, update, context)


    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_create_simple(self, *mocks):
        bot = setup_test_bot(self)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        bot_request_command_send_msg(bot, commands.CreateQueue.CreateSimple, update, context)

        tg_write_message(update, '0\n1\ntest\n2')
        bot.handle_message_text(update, context)

        tg_write_message(update, 'Name')
        bot.handle_message_text(update, context)

        self.assertListEqual(bot.queues_manager.get_queue().students,
                             [Student('0', 0), Student('1', 1), Student('test', None), Student('2', 2)])

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_create_random(self, *mocks):
        bot = setup_test_bot(self)

        # check bot commands for correct queue creation
        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        bot_request_command_send_msg(bot, commands.CreateQueue.CreateRandom, update, context)

        tg_write_message(update, '0\n1\ntest\n2')
        bot.handle_message_text(update, context)

        tg_write_message(update, 'Name')
        bot.handle_message_text(update, context)

        self.assertCountEqual(bot.get_queue().students,
                              [Student('0', 0), Student('1', 1), Student('test', None), Student('2', 2)])

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_general_features(self, *mocks):
        bot = setup_test_bot(self)

        queue_students = list(bot.registered_manager.get_users())
        queue_students.insert(3, Student('t', None))

        bot = setup_test_queue(bot, 'test', queue_students)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)

        bot_request_command_send_msg(bot, commands.CreateQueue.CreateSimple, update, context)

        # write queue data
        names = '\n'.join([st.name for st in queue_students[:-2]])
        tg_write_message(update, names)
        bot.handle_message_text(update, context)

        tg_write_message(update, 'name')
        bot.handle_message_text(update, context)

        self.assertEqual(bot.get_queue().name, 'name')
        # we skipped two last elements while initializing queue
        self.assertListEqual(bot.get_queue().students, queue_students[:-2])

        # test previous queue selection
        bot.queues_manager.remove_queue('name')
        self.assertEqual(bot.get_queue().name, 'test')
        self.assertListEqual(bot.get_queue().students, queue_students)

        # 'test' rename
        tg_select_command(update, commands.ManageQueues.RenameQueue, 'test')
        bot.handle_keyboard_chosen(update, context)

        tg_write_message(update, 'new_name')
        bot.handle_message_text(update, context)
        self.assertIn('new_name', bot.queues_manager.queues)
        self.assertNotIn('test', bot.queues_manager.queues)


    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_copy(self, *mocks):
        bot, queue_students, update, context = setup_bot_and_queue(self)

        bot = setup_test_queue(bot, 'test', queue_students)
        text = bot.get_queue().get_str_for_copy()

        # delete queues and start with empty bot
        bot = setup_test_bot(self)

        bot_handle_text_command(bot, update, context, '/new_queue')
        self.assertListEqual(bot.get_queue().students, [])

        bot_handle_text_command(bot, update, context, text)
        self.assertListEqual(bot.get_queue().students, queue_students)



    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_create_with_empty_lines(self, *mocks):
        bot = setup_test_bot(self)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        bot_request_command_send_msg(bot, commands.CreateQueue.CreateSimple, update, context)

        message = '''Дурда + Козинцева

Вороной + Василюк

Люлька + Кущевой

Прокопенко + Гречко

Мотрук + Скицюк

Воловик + Комисар

Копылаш + Редька

Северян + Дорошенко'''

        tg_write_message(update, message)
        bot.handle_message_text(update, context)

        tg_select_command(update, commands.CreateQueue.DefaultQueueName)
        bot.handle_keyboard_chosen(update, context)

        self.assertListEqual([Student('Дурда + Козинцева', None),
                              Student('Вороной + Василюк', None),
                              Student('Люлька + Кущевой', None),
                              Student('Прокопенко + Гречко', None),
                              Student('Мотрук + Скицюк', None),
                              Student('Воловик + Комисар', None),
                              Student('Копылаш + Редька', None),
                              Student('Северян + Дорошенко', None)],
                             bot.queues_manager.get_queue().students)

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_add_user(self, *mocks):
        bot = setup_test_bot(self)
        queue = StudentsQueue(bot)

        queue.append_by_name('0')
        self.assertEqual(queue.students[-1], Student('0', 0))
        queue.append_by_name('Unknown')
        self.assertEqual(queue.students[-1], Student('Unknown', None))

        queue.append_to_queue(Student('0', 4))  # different name, id the same
        self.assertEqual(queue.students[2], Student('4', 4))

        prev_list = queue.students

        queue.append_to_queue(Student('0', 0))
        self.assertCountEqual(prev_list, queue.students)
        self.assertEqual(Student('0', 0), queue.get_last())

        queue.append_by_name('Unknown')
        self.assertCountEqual(prev_list, queue.students)
        self.assertEqual(Student('Unknown', None), queue.get_last())

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_delete_me(self, *mocks):
        bot = setup_test_bot(self)
        students = [bot.registered_manager.get_user_by_id(2),
                    bot.registered_manager.get_user_by_id(1),
                    Student('test', None)]
        bot = setup_test_queue(bot, 'Queue', students)

        update = MagicMock()
        context = MagicMock()

        # must not do anything
        tg_set_user(update, 3)
        tg_select_command(update, commands.ModifyCurrentQueue.RemoveMe)
        bot.handle_keyboard_chosen(update, context)

        # must delete user
        tg_set_user(update, 1)
        tg_select_command(update, commands.ModifyCurrentQueue.RemoveMe)
        bot.handle_keyboard_chosen(update, context)

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_add_me(self, *mocks):
        bot = setup_test_bot(self)
        students = [bot.registered_manager.get_user_by_id(2),
                    bot.registered_manager.get_user_by_id(1),
                    Student('test', None)]
        bot = setup_test_queue(bot, 'Queue', students)

        update = MagicMock()
        context = MagicMock()

        # must not do anything
        tg_set_user(update, 3)
        tg_select_command(update, commands.ModifyCurrentQueue.AddMe)
        bot.handle_keyboard_chosen(update, context)

        # must delete user
        tg_set_user(update, 1)
        tg_select_command(update, commands.ModifyCurrentQueue.AddMe)
        bot.handle_keyboard_chosen(update, context)

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_select_queue(self, *mocks):
        bot = setup_test_bot(self)

        bot = setup_test_queue(bot, 'test1', bot.registered_manager.get_users())
        bot = setup_test_queue(bot, 'test2', bot.registered_manager.get_users())

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.ManageQueues.SelectOtherQueue, 'test1')
        bot.handle_keyboard_chosen(update, context)

        self.assertEqual(bot.queues_manager.get_queue().name, 'test1')

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_delete_queue(self, *mocks):
        bot = setup_test_bot(self)

        bot = setup_test_queue(bot, 'test1', bot.registered_manager.get_users())
        bot = setup_test_queue(bot, 'test2', bot.registered_manager.get_users())

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.ManageQueues.DeleteQueue, 'test1')
        bot.handle_keyboard_chosen(update, context)

        self.assertNotIn('test1', bot.queues_manager)

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_correct_queue_indexes(self, *mocks):
        bot = setup_test_bot(self)
        bot = setup_test_queue(bot, 'test', bot.registered_manager.get_users())

        bot.queues_manager.get_queue().set_position(3)
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()

        # if we delete current user, next element must become current
        bot.queues_manager.get_queue().remove_by_index(3)
        self.assertNotIn(cur_stud, bot.queues_manager.get_queue())
        self.assertEqual(next_stud, bot.queues_manager.get_queue().get_current())

        # if we delete user from larger position, current student must stay
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()
        bot.queues_manager.get_queue().set_position(2)
        bot.queues_manager.get_queue().remove_by_index(3)
        self.assertEqual(cur_stud, bot.queues_manager.get_queue().get_current())

        # if we delete user before current, it must remain on it`s place
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()
        bot.queues_manager.get_queue().set_position(2)
        bot.queues_manager.get_queue().remove_by_index(1)
        self.assertEqual(cur_stud, bot.queues_manager.get_queue().get_current())

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_remove_students_list(self, *mocks):
        bot = setup_test_bot(self)
        students = [bot.registered_manager.get_user_by_id(2),
                    bot.registered_manager.get_user_by_id(1),
                    Student('test', None),
                    bot.registered_manager.get_user_by_id(4)]
        bot = setup_test_queue(bot, 'Queue', students)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.ModifyCurrentQueue.RemoveListStudents)
        bot.handle_keyboard_chosen(update, context)

        self.assertListEqual(students, bot.get_queue().students)

        tg_select_command(update, commands.ModifyCurrentQueue.RemoveListStudents, students[1])
        bot.handle_keyboard_chosen(update, context)
        self.assertNotIn(students[1], bot.get_queue().students)

        tg_select_command(update, commands.ModifyCurrentQueue.RemoveListStudents, students[2])
        bot.handle_keyboard_chosen(update, context)
        self.assertNotIn(students[2], bot.get_queue().students)


class TestRegisteredManager(unittest.TestCase):

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_bot_check_access(self, *mocks):
        bot = setup_test_bot(self)

        mock_update = MagicMock()

        # for other than private chat
        mock_update.effective_chat.type = Chat.SUPERGROUP

        mock_update.effective_user.id = 0
        self.assertFalse(bot.registered_manager.check_access(mock_update))

        mock_update.effective_user.id = 1
        self.assertFalse(bot.registered_manager.check_access(mock_update))

        mock_update.effective_user.id = 2
        self.assertFalse(bot.registered_manager.check_access(mock_update))

        # for private chat
        mock_update.effective_chat.type = Chat.PRIVATE

        mock_update.effective_user.id = 0
        self.assertTrue(bot.registered_manager.check_access(mock_update))

        mock_update.effective_user.id = 1
        self.assertTrue(bot.registered_manager.check_access(mock_update))

        mock_update.effective_user.id = 2
        self.assertFalse(bot.registered_manager.check_access(mock_update))

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_get_user(self, *mocks):
        bot = setup_test_bot(self)

        user = bot.registered_manager.get_user_by_name('0')
        self.assertEqual(user, Student('0', 0))

        user = bot.registered_manager.get_user_by_name('NoSuchName')
        self.assertIsNone(user)

        user = bot.registered_manager.get_user_by_id(4)
        self.assertEqual(Student('4', 4), user)

        user = bot.registered_manager.get_user_by_id(100)
        self.assertIsNone(user)

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_name_similarity(self, *mocks):
        bot = setup_test_bot(self)

        self.assertTrue(bot.registered_manager.is_similar('Переяславський', 'Переяславский'))
        self.assertTrue(bot.registered_manager.is_similar('Скрипник', 'Скрыпник'))
        self.assertTrue(bot.registered_manager.is_similar('Железнова', 'Желэзнова'))
        self.assertFalse(bot.registered_manager.is_similar('Железнова', 'Велескова'))
        self.assertFalse(bot.registered_manager.is_similar('Буч', 'Бучной'))  # similar start, different len
        self.assertFalse(bot.registered_manager.is_similar('Бучкичной', 'Бучновник'))  # similar start, equal len

        user = bot.registered_manager.find_similar_student('0')
        self.assertEqual(user, Student('0', 0))

        user = bot.registered_manager.find_similar_student('NoName')
        self.assertEqual(user, Student('NoName', None))

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_delete_list(self, *mocks):
        bot = setup_test_bot(self)
        students = list(bot.registered_manager.get_users())

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.ModifyRegistered.RemoveListUsers)
        bot.handle_keyboard_chosen(update, context)

        self.assertIn(students[1], bot.registered_manager.get_users())
        tg_select_command(update, commands.ModifyRegistered.RemoveListUsers, students[1].str_name_id())
        bot.handle_keyboard_chosen(update, context)
        self.assertNotIn(students[1], bot.registered_manager.get_users())

        self.assertIn(students[2], bot.registered_manager.get_users())
        tg_select_command(update, commands.ModifyRegistered.RemoveListUsers, students[2].str_name_id())
        bot.handle_keyboard_chosen(update, context)
        self.assertNotIn(students[2], bot.registered_manager.get_users())

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_add_remove_admin(self, *mocks):
        bot = setup_test_bot(self)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.ManageAccessRights.AddAdmin)
        bot.handle_keyboard_chosen(update, context)
        tg_forward_message(update, 100, '100')
        bot.handle_message_text(update, context)
        self.assertIs(bot.registered_manager.get_user_by_id(100).access_level, AccessLevel.ADMIN)

        tg_select_command(update, commands.ManageAccessRights.AddAdmin)
        bot.handle_keyboard_chosen(update, context)
        tg_forward_message(update, 3, '3')
        bot.handle_message_text(update, context)
        self.assertIs(bot.registered_manager.get_user_by_id(3).access_level, AccessLevel.ADMIN)

        test_st = bot.registered_manager.get_user_by_id(100)
        tg_select_command(update, commands.ManageAccessRights.RemoveAdmin, test_st)
        bot.handle_keyboard_chosen(update, context)
        self.assertIn(test_st, bot.registered_manager)
        self.assertIs(bot.registered_manager.get_user_by_id(100).access_level, AccessLevel.USER)

        test_st = bot.registered_manager.get_user_by_id(3)
        tg_select_command(update, commands.ManageAccessRights.RemoveAdmin, test_st)
        bot.handle_keyboard_chosen(update, context)
        self.assertIn(test_st, bot.registered_manager)
        self.assertIs(bot.registered_manager.get_user_by_id(3).access_level, AccessLevel.USER)


class TestBotCommands(unittest.TestCase):

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_cur_and_next_in_queue(self, *mocks):
        bot = setup_test_bot(self)
        bot = setup_test_queue(bot, 'test1', bot.registered_manager.get_users())

        students = bot.queues_manager.get_queue().students

        bot.queues_manager.get_queue().set_position(2)
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()

        self.assertEqual(cur_stud, students[2])
        self.assertEqual(next_stud, students[3])

        # last element
        bot.queues_manager.get_queue().set_position(5)
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()

        self.assertEqual(cur_stud, students[4])
        self.assertIsNone(next_stud)

        # after last element
        bot.queues_manager.get_queue().set_position(6)
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()

        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)

        bot.queues_manager.get_queue().set_position(100)
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()

        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)


    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_move_queue(self, *mocks):
        bot = setup_test_bot(self)

        students = bot.registered_manager.get_users() + [Student('Unknown', None)]
        bot = setup_test_queue(bot, 'test1', students)

        self.assertTrue(bot.queues_manager.get_queue().move_next())

        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()
        self.assertEqual(cur_stud, students[1])
        self.assertEqual(next_stud, students[2])

        # move from last element forward
        bot.queues_manager.get_queue().set_position(len(students) - 1)
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()
        self.assertIsNotNone(cur_stud)
        self.assertIsNone(next_stud)

        bot.queues_manager.get_queue().move_next()
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()
        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)

        bot.queues_manager.get_queue().move_next()
        cur_stud, next_stud = bot.queues_manager.get_queue().get_cur_and_next()
        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)


    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_move_to_end(self, *mocks):
        bot = setup_test_bot(self)

        students = bot.registered_manager.get_users() + [Student('Unknown', None)]
        bot = setup_test_queue(bot, 'test1', students)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.ModifyCurrentQueue.MoveStudentToEnd, Student.student_show_format.format('2', 2))
        bot.handle_keyboard_chosen(update, context)
        self.assertEqual(bot.get_queue().students[-1], bot.registered_manager.get_user_by_id(2))

        tg_select_command(update, commands.ModifyCurrentQueue.MoveStudentToEnd, str(Student('Unknown', None)))
        bot.handle_keyboard_chosen(update, context)
        self.assertEqual(Student('Unknown', None), bot.get_queue().students[-1])


    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_append_delete_user(self, *mocks):
        bot = setup_test_bot(self)
        bot.registered_manager.append_new_user('Test', 100)
        self.assertIn(Student('Test', 100), bot.registered_manager.students_reg)

        bot.registered_manager.remove_by_id(100)
        self.assertNotIn(Student('Test', 100), bot.registered_manager.students_reg)


    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_unknown_user_in_queue(self, *mocks):
        bot = setup_test_bot(self)

        bot = setup_test_queue(bot, 'test1', bot.registered_manager.get_users())
        bot.queues_manager.get_queue().append_by_name('Unknown')
        self.assertIn(Student('Unknown', None), bot.queues_manager.get_queue().students)

        # test for interactions with bot

        update = MagicMock()
        context = MagicMock()

        # unknown adds himself
        tg_set_user(update, None, 'V')
        bot_request_command_send_msg(bot, commands.ModifyCurrentQueue.AddMe, update, context)
        self.assertIn(Student('V', None), bot.get_queue().students)

        # unknown removes himself
        bot_request_command_send_msg(bot, commands.ModifyCurrentQueue.RemoveMe, update, context)
        self.assertNotIn(Student('V', None), bot.queues_manager.get_queue().students)

        bot_request_command_send_msg(bot, commands.ModifyCurrentQueue.AddMe, update, context)  # add user again
        idx = 3
        # move him to desired index
        bot.queues_manager.get_queue().move_to_index(len(bot.queues_manager.get_queue().students) - 1, idx)
        self.assertEqual(Student('V', None), bot.queues_manager.get_queue().students[idx])

        # when unknown finished, go next
        bot.queues_manager.get_queue().set_position(idx)
        bot_request_command_send_msg(bot, commands.ModifyCurrentQueue.StudentFinished, update, context)
        self.assertEqual(idx + 1, bot.queues_manager.get_queue().get_position())

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_swap_users_in_queue(self, *mocks):
        bot = setup_test_bot(self)
        bot = setup_test_queue(bot, 'test1', list(bot.registered_manager.get_users()))

        update = MagicMock()
        c = MagicMock()

        first_user = bot.registered_manager.get_users()[2]
        second_user = bot.registered_manager.get_users()[4]

        tg_set_user(update, 1)
        tg_select_command(update, commands.ModifyCurrentQueue.SwapStudents)
        bot.handle_keyboard_chosen(update, c)  # must only create keyboard

        tg_select_command(update, commands.ModifyCurrentQueue.SwapStudents, str(first_user))
        bot.handle_keyboard_chosen(update, c)
        tg_select_command(update, commands.ModifyCurrentQueue.SwapStudents, str(second_user))
        bot.handle_keyboard_chosen(update, c)

        self.assertCountEqual(bot.get_queue().students, bot.registered_manager.get_users())
        self.assertEqual(second_user, bot.get_queue().students[2])
        self.assertEqual(first_user, bot.get_queue().students[4])

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_start_bot(self, *mocks):
        bot = setup_test_bot(self)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 0, '0')
        bot_request_command_send_msg(bot, commands.General.Start, update, context)
        update.message.reply_text.assert_called_with(bot.language_pack.bot_already_running)

        bot.registered_manager.remove_by_id(0)  # remove god user
        tg_set_user(update, 0, '0')
        bot_request_command_send_msg(bot, commands.General.Start, update, context)
        update.message.reply_text.assert_called_with(bot.language_pack.first_user_added.format('0'))

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_setup_subjects(self, *mocks):
        bot = setup_test_bot(self)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        bot_request_command_send_msg(bot, commands.CollectSubjectChoices.CreateNewCollectFile, update, context)

        tg_write_message(update, 'Test')
        bot.handle_message_text(update, context)

        tg_write_message(update, '1-15')
        bot.handle_message_text(update, context)

        tg_write_message(update, '3')
        bot.handle_message_text(update, context)

        self.assertEqual('Test', bot.choice_manager.current_subjects.name)
        self.assertEqual((1, 15), bot.choice_manager.current_subjects.available_range)
        self.assertEqual(3, bot.choice_manager.current_subjects.repeat_limit)

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_get_subjects(self, *mocks):
        pass


class TestDriveSaving(unittest.TestCase):
    # todo: write test for correct loading from google drive
    pass


class TestParsers(unittest.TestCase):

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_file_names_parse(self, *mocks):
        from queue_bot.bot_parsers import parse_valid_queue_names
        from queue_bot.multiple_queues import QueuesManager

        bot = MagicMock()

        names = ['name1', 'name2', 'name3']
        test_queues = QueuesManager(bot, [StudentsQueue(bot, name) for name in names])
        save_files = test_queues.get_save_files()

        file_names = []
        for path in save_files:
            file_names.append(path.name)

        queue_names = parse_valid_queue_names(file_names)
        self.assertListEqual(names, queue_names)

    def test_students_formats(self):
        self.addTypeEqualityFunc(Student, students_compare)

        s1 = Student(''.join(['a' for i in range(50, 60)]), 2**31)
        s2 = Student(''.join(['b' for i in range(50, 130)]), None)
        s3 = Student(''.join(['c' for i in range(50, 60)]), None)
        s5 = Student('', None)
        str1 = s1.str_name_id()
        str2 = s2.str_name_id()
        str3 = s3.str_name_id()
        str4 = 'No'
        str5 = s5.str_name_id()

        self.assertEqual(s1, bot_parsers.parse_student(str1))
        self.assertIsNone(bot_parsers.parse_student(str2))
        self.assertEqual(s3, bot_parsers.parse_student(str3))
        self.assertIsNone(bot_parsers.parse_student(str4))
        self.assertEqual(s5, bot_parsers.parse_student(str5))


if __name__ == '__main__':
    unittest.main()
