import unittest

import queue_bot.bot_commands as commands

from unit_tests.shared_test_functions import *


class TestBotCommands(unittest.TestCase):

    def setUp(self) -> None:
        self.bot = setup_test_bot(self)

        self.bot = setup_test_queue(self.bot, "reg", self.bot.registered_manager.get_users())

        self.uc = MagicMock(), MagicMock()
        self.u = self.uc[0]
        self.c = self.uc[0]

        # set default admin user
        tg_set_user(self.u, 1)

    def test_command_parse(self):
        tg_set_user(self.u, 1)
        bot_handle_text_command(self.bot, *self.uc, '/new_queue@QueueBot')

    def test_cur_and_next_in_queue(self):
        students = self.bot.get_queue().students

        self.bot.queues_manager.get_queue().set_position(2)
        cur_stud, next_stud = self.bot.queues_manager.get_queue().get_cur_and_next()

        self.assertEqual(cur_stud, students[2])
        self.assertEqual(next_stud, students[3])

        # last element
        self.bot.queues_manager.get_queue().set_position(5)
        cur_stud, next_stud = self.bot.queues_manager.get_queue().get_cur_and_next()

        self.assertEqual(cur_stud, students[4])
        self.assertIsNone(next_stud)

        # after last element
        self.bot.queues_manager.get_queue().set_position(6)
        cur_stud, next_stud = self.bot.queues_manager.get_queue().get_cur_and_next()

        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)

        self.bot.queues_manager.get_queue().set_position(100)
        cur_stud, next_stud = self.bot.queues_manager.get_queue().get_cur_and_next()

        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)

    def test_move_to_end(self):
        tg_select_command(self.u, commands.ModifyCurrentQueue.MoveStudentToEnd, str(Student('2', 2)))
        self.bot.handle_keyboard_chosen(*self.uc)
        self.assertEqual(self.bot.get_queue().students[-1], self.bot.registered_manager.get_user_by_id(2))

        tg_select_command(self.u, commands.ModifyCurrentQueue.MoveStudentToEnd, str(Student('Unknown', None)))
        self.bot.handle_keyboard_chosen(*self.uc)
        self.assertEqual(Student('Unknown', None), self.bot.get_queue().students[-1])

    def test_append_delete_user(self):
        self.bot.registered_manager.append_new_user('Test', 100)
        self.assertIn(Student('Test', 100), self.bot.registered_manager.students_reg)

        self.bot.registered_manager.remove_by_id(100)
        self.assertNotIn(Student('Test', 100), self.bot.registered_manager.students_reg)

    def test_unknown_user_in_queue(self):
        bot = setup_test_queue(self.bot, 'test1', self.bot.registered_manager.get_users())
        self.bot.queues_manager.get_queue().append_by_name('Unknown')
        self.assertIn(Student('Unknown', None), self.bot.queues_manager.get_queue().students)

        # test for interactions with bot

        # unknown adds himself
        tg_set_user(self.u, None, 'V')
        bot_request_command_send_msg(self.bot, commands.ModifyCurrentQueue.AddMe, *self.uc)
        self.assertIn(Student('V', None), self.bot.get_queue().students)

        # unknown removes himself
        bot_request_command_send_msg(self.bot, commands.ModifyCurrentQueue.RemoveMe, *self.uc)
        self.assertNotIn(Student('V', None), self.bot.queues_manager.get_queue().students)

        bot_request_command_send_msg(self.bot, commands.ModifyCurrentQueue.AddMe, *self.uc)  # add user again
        idx = 3
        # move him to desired index
        self.bot.queues_manager.get_queue().move_to_index(len(self.bot.queues_manager.get_queue().students) - 1, idx)
        self.assertEqual(Student('V', None), self.bot.queues_manager.get_queue().students[idx])

        # when unknown finished, go next
        self.bot.queues_manager.get_queue().set_position(idx)
        bot_request_command_send_msg(self.bot, commands.ModifyCurrentQueue.StudentFinished, *self.uc)
        self.assertEqual(idx + 1, self.bot.queues_manager.get_queue().get_position())

    def test_start_bot(self):
        tg_set_user(self.u, 0, '0')
        bot_request_command_send_msg(self.bot, commands.General.Start, *self.uc)
        self.u.message.reply_text.assert_called_with(self.bot.language_pack.bot_already_running)

        self.bot.registered_manager.remove_by_id(0)  # remove god user
        tg_set_user(self.u, 0, '0')
        bot_request_command_send_msg(self.bot, commands.General.Start, *self.uc)
        self.u.message.reply_text.assert_called_with(self.bot.language_pack.first_user_added.format('0'))


if __name__ == '__main__':
    unittest.main()
