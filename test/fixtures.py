from unittest import mock

from pytest import fixture

from queue_bot.bot.main_bot import QueueBot
from queue_bot.objects.queue_students import QueueStudents, QueueParameters
from queue_bot.objects.student import Student
from queue_bot.database import reset_database, db_session


@fixture()
@mock.patch('queue_bot.bot.main_bot.Updater')
def bot(*mocks):
    bot = QueueBot('0')
    bot.registered_manager.add_user('0', 0)  # god
    bot.registered_manager.set_god(0)
    bot.registered_manager.add_user('1', 1)  # admin
    bot.registered_manager.set_admin(1)
    bot.registered_manager.add_user('2', 2)  # user
    bot.registered_manager.add_user('3', 3)  # user
    bot.registered_manager.add_user('4', 4)  # user
    bot.registered_manager.add_user('5', 5)  # user
    return bot

@fixture()
def queue(bot) -> QueueStudents:
    return bot.new_queue(bot.registered_manager.get_users() + [student_factory("No id", None)], "test")

@fixture()
def session():
    reset_database()
    return db_session()
