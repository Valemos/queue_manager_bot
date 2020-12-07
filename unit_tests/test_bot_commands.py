import os
import pathlib
from unittest.mock import MagicMock
import mock
import unittest

import queue_bot.bot_commands as commands


from unit_tests.shared_test_functions import *


class TestBotCommands(unittest.TestCase):


    def test_command_parse(self, *mocks):
        bot = setup_test_bot(self)
        update, context = MagicMock(), MagicMock()
        tg_set_user(update, 1)
        bot_handle_text_command(bot, update, context, '/new_queue@QueueBot')



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



    def test_append_delete_user(self, *mocks):
        bot = setup_test_bot(self)
        bot.registered_manager.append_new_user('Test', 100)
        self.assertIn(Student('Test', 100), bot.registered_manager.students_reg)

        bot.registered_manager.remove_by_id(100)
        self.assertNotIn(Student('Test', 100), bot.registered_manager.students_reg)



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



if __name__ == '__main__':
    unittest.main()
