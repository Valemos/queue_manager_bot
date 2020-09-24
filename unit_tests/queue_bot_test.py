from unittest.mock import MagicMock
import mock
import unittest

from queue_bot.students_queue import StudentsQueue, Student
from queue_bot.queue_telegram_bot import QueueBot
import queue_bot.bot_commands as commands

from telegram import Chat


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


def tg_set_user(update, user_id, user_name=''):
    update.effective_user.full_name = user_name
    update.effective_user.id = user_id

    update.message.from_user.full_name = user_name
    update.message.from_user.id = user_id

    update.effective_message.user.full_name = user_name
    update.effective_message.user.id = user_id


def tg_choose_command(update, cmd_class, button_args=None):
    update.callback_query.data = cmd_class.str(button_args)


def tg_write_message(update, contents, user_id, user_name=''):
    update.message.text = contents
    tg_set_user(update, user_name, user_id)


class TestQueue(unittest.TestCase):

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_create_simple(self, *mocks):
        bot = setup_test_bot(self)

        update = MagicMock()
        context = MagicMock()

        tg_choose_command(update, commands.QueuesManage.CreateSimple, 1)
        bot._h_keyboard_chosen(update, context)

        tg_write_message(update, '0\n1\ntest\n2', 1)
        bot._h_message_text(update, context)

        tg_write_message(update, 'Name', 1)
        bot._h_message_text(update, context)

        self.assertListEqual(bot.queues_manager.get_queue()._students,
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

        tg_choose_command(update, commands.QueuesManage.CreateRandom, 1)
        bot._h_keyboard_chosen(update, context)

        tg_write_message(update, '0\n1\ntest\n2', 1)
        bot._h_message_text(update, context)

        tg_write_message(update, 'Name', 1)
        bot._h_message_text(update, context)

        self.assertCountEqual(bot.queues_manager.get_queue()._students,
                              [Student('0', 0), Student('1', 1), Student('test', None), Student('2', 2)])

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_queue_add_user(self, *mocks):
        bot = setup_test_bot(self)
        queue = StudentsQueue(bot)

        queue.append_by_name('0')
        self.assertEqual(queue._students[-1], Student('0', 0))
        queue.append_by_name('Unknown')
        self.assertEqual(queue._students[-1], Student('Unknown', None))

        queue.append_to_queue(Student('0', 4))  # different name, id the same
        self.assertEqual(queue._students[2], Student('4', 4))

        prev_list = queue._students

        queue.append_to_queue(Student('0', 0))
        self.assertCountEqual(prev_list, queue._students)
        self.assertEqual(Student('0', 0), queue.get_last())

        queue.append_by_name('Unknown')
        self.assertCountEqual(prev_list, queue._students)
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
        tg_choose_command(update, commands.ModifyCurrentQueue.RemoveMe)
        bot._h_keyboard_chosen(update, context)

        # must delete user
        tg_set_user(update, 1)
        tg_choose_command(update, commands.ModifyCurrentQueue.RemoveMe)
        bot._h_keyboard_chosen(update, context)


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
        tg_choose_command(update, commands.ModifyCurrentQueue.AddMe)
        bot._h_keyboard_chosen(update, context)

        # must delete user
        tg_set_user(update, 1)
        tg_choose_command(update, commands.ModifyCurrentQueue.AddMe)
        bot._h_keyboard_chosen(update, context)


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
        tg_choose_command(update, commands.QueuesManage.ChooseOtherQueue, 'test1')
        bot._h_keyboard_chosen(update, context)

        self.assertEqual(bot.queues_manager.get_queue().name, 'test1')

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


class TestBotCommands(unittest.TestCase):

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_cur_and_next_in_queue(self, *mocks):
        bot = setup_test_bot(self)
        bot = setup_test_queue(bot, 'test1', bot.registered_manager.get_users())

        students = bot.queues_manager.get_queue()._students

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
    def test_append_delete_user(self, *mocks):
        bot = setup_test_bot(self)
        bot.registered_manager.append_new_user('Test', 100)
        self.assertIn(Student('Test', 100), bot.registered_manager._students_reg)


    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_unknown_user_in_queue(self, *mocks):
        bot = setup_test_bot(self)

        bot = setup_test_queue(bot, 'test1', bot.registered_manager.get_users())
        bot.queues_manager.get_queue().append_by_name('Unknown')
        self.assertIn(Student('Unknown', None), bot.queues_manager.get_queue()._students)

        # test for interactions with bot

        update = MagicMock()
        context = MagicMock()

        # unknown adds himself
        tg_set_user(update, None, 'V')
        bot._h_add_me(update, context)
        self.assertIn(Student('V', None), bot.queues_manager.get_queue()._students)

        # unknown removes himself
        bot._h_remove_me(update, context)
        self.assertNotIn(Student('V', None), bot.queues_manager.get_queue()._students)

        bot._h_add_me(update, context)  # add user again
        idx = 3
        # move him to desired index
        bot.queues_manager.get_queue().move_to_index(len(bot.queues_manager.get_queue()._students) - 1, idx)
        self.assertEqual(Student('V', None), bot.queues_manager.get_queue()._students[idx])

        # when unknown finished, go next
        bot.queues_manager.get_queue().set_position(idx)
        bot._h_i_finished(update, context)
        self.assertEqual(idx + 1, bot.queues_manager.get_queue().get_position())



if __name__ == '__main__':
    unittest.main()
