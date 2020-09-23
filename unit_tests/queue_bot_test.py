from unittest.mock import MagicMock
import mock
import unittest

from queue_bot.students_queue import StudentsQueue, Student
from queue_bot.queue_telegram_bot import QueueBot

from telegram import Chat


def students_compare(f, s, msg=None):
    return f.name == s.name and \
           f.telegram_id == s.telegram_id and \
           f.access_level == s.access_level


class TestQueue(unittest.TestCase):

    @mock.patch('queue_bot.queue_telegram_bot.QueueBot')
    def test_queue_create_simple(self, mock_bot):
        queue = StudentsQueue(mock_bot)
        self.assertListEqual(queue._students, [])

        students = [Student(name='A', telegram_id=0), Student(name='B', telegram_id=1)]
        queue.generate_simple(students)

        self.addTypeEqualityFunc(Student, students_compare)
        self.assertListEqual(queue._students, students)

    @mock.patch('queue_bot.queue_telegram_bot.QueueBot')
    def test_queue_create_random(self, mock_bot):
        queue = StudentsQueue(mock_bot)
        self.assertListEqual(queue._students, [])

        students = [Student(name='A', telegram_id=0), Student(name='B', telegram_id=1)]
        queue.generate_random(students)

        self.addTypeEqualityFunc(Student, students_compare)
        self.assertCountEqual(queue._students, students)


class TestBotCommands(unittest.TestCase):

    @mock.patch('queue_bot.queue_telegram_bot.DriveSaver')
    @mock.patch('queue_bot.queue_telegram_bot.ObjectSaver')
    @mock.patch('queue_bot.queue_telegram_bot.Logger')
    @mock.patch('queue_bot.queue_telegram_bot.Updater')
    def test_bot_check_access(self, mock_drive_saver, mock_object_saver, mock_logger, mock_updater):
        bot = QueueBot('0')

        mock_update = MagicMock()

        bot.registered_manager.append_new_user('A', 0)  # god
        bot.registered_manager.set_god(0)
        bot.registered_manager.append_new_user('B', 1)  # admin
        bot.registered_manager.set_admin(1)
        bot.registered_manager.append_new_user('C', 2)  # user

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


if __name__ == '__main__':
    unittest.main()
