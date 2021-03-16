import unittest

import queue_bot.commands.classes.create_queue as create_queue
import queue_bot.commands.classes.manage_queues as manage_queues
import queue_bot.commands.classes.modify_queue as modify_queue

from unit_tests.shared_test_functions import *


class TestQueue(unittest.TestCase):

    def setUp(self) -> None:
        self.bot = setup_test_bot(self)

        self.queue_students_with_none = list(self.bot.registered_manager.get_users())

        self.student_none = Student('t', None)
        self.student_none_index = 3
        self.queue_students_with_none.insert(self.student_none_index, self.student_none)

        self.bot = setup_test_queue(self.bot, 'idNone', self.queue_students_with_none)
        self.bot = setup_test_queue(self.bot, 'reg', self.bot.registered.get_users())
        self.current_queue_students = self.bot.get_queue().students

        self.not_current_queue_name = None
        for queue_name in self.bot.queues.queues:
            if queue_name != self.bot.get_queue().name:
                self.not_current_queue_name = queue_name
        self.assertIsNotNone(self.not_current_queue_name)

        from unittest.mock import MagicMock

        # update and context variables for every command handler in telegram api
        self.uc = MagicMock(), MagicMock()
        self.u = self.uc[0]
        self.c = self.uc[0]

        # set default admin user
        tg_set_user(self.u, 1)

    def test_queue_create_simple(self):
        bot_request_command_send_msg(self.bot, create_queue.CreateSimple, *self.uc)
        bot_handle_message(self.bot, '0\n1\ntest\n2', *self.uc)
        bot_handle_message(self.bot, 'Name', *self.uc)

        self.assertListEqual(self.bot.get_queue().students,
                             [Student('0', 0), Student('1', 1), Student('test', None), Student('2', 2)])

    def test_queue_create_random(self):
        bot_request_command_send_msg(self.bot, create_queue.CreateRandom, *self.uc)

        tg_write_message(self.u, '0\n1\ntest\n2')
        self.bot.handle_message_reply_command(*self.uc)

        tg_write_message(self.u, 'Name')
        self.bot.handle_message_reply_command(*self.uc)

        self.assertCountEqual(self.bot.get_queue().students,
                              [Student('0', 0), Student('1', 1), Student('test', None), Student('2', 2)])

    def test_rename_queue(self):
        prev_queue_name = self.not_current_queue_name
        tg_select_command(self.u, manage_queues.RenameQueue, prev_queue_name)
        self.bot.handle_keyboard_chosen(*self.uc)

        tg_write_message(self.u, 'new_name')
        self.bot.handle_message_reply_command(*self.uc)
        self.assertIn('new_name', self.bot.queues.queues)
        self.assertNotIn(prev_queue_name, self.bot.queues.queues)

    def test_swap_users_in_queue(self):

        first_user = self.bot.registered.get_users()[2]
        second_user = self.bot.registered.get_users()[4]

        tg_select_command(self.u, modify_queue.MoveSwapStudents)
        self.bot.handle_keyboard_chosen(*self.uc)  # must only create keyboard

        tg_select_command(self.u, modify_queue.MoveSwapStudents, str(first_user))
        self.bot.handle_keyboard_chosen(*self.uc)
        tg_select_command(self.u, modify_queue.MoveSwapStudents, str(second_user))
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertCountEqual(self.bot.get_queue().students, self.bot.registered.get_users())
        self.assertEqual(second_user, self.bot.get_queue().students[2])
        self.assertEqual(first_user, self.bot.get_queue().students[4])

    def test_queue_copy(self):
        text = self.bot.get_queue().get_str_for_copy()
        initial_students = self.bot.get_queue().students

        # delete queues and start with empty bot
        empty_bot = setup_test_bot(self)

        tg_set_user(self.u, 1, '1')
        bot_handle_text_command(empty_bot, *self.uc, '/new_queue')
        self.assertIsNone(empty_bot.get_queue())

        bot_handle_text_command(empty_bot, *self.uc, text)
        self.assertListEqual(empty_bot.get_queue().students, initial_students)

    def test_create_with_empty_lines(self):
        bot_request_command_send_msg(self.bot, create_queue.CreateSimple, *self.uc)

        message = '''Дурда + Козинцева

Вороной + Василюк

Люлька + Кущевой

Прокопенко + Гречко

Мотрук + Скицюк

Воловик + Комисар

Копылаш + Редька

Северян + Дорошенко'''

        tg_write_message(self.u, message)
        self.bot.handle_message_reply_command(*self.uc)

        tg_select_command(self.u, create_queue.DefaultQueueName)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertListEqual([Student('Дурда + Козинцева', None),
                              Student('Вороной + Василюк', None),
                              Student('Люлька + Кущевой', None),
                              Student('Прокопенко + Гречко', None),
                              Student('Мотрук + Скицюк', None),
                              Student('Воловик + Комисар', None),
                              Student('Копылаш + Редька', None),
                              Student('Северян + Дорошенко', None)],
                             self.bot.get_queue().students)

    def test_queue_add_user(self):
        queue = QueueStudents(self.bot)

        queue.append_by_name('0')
        self.assertEqual(queue.students[-1], Student('0', 0))
        queue.append_by_name('Unknown')
        self.assertEqual(queue.students[-1], Student('Unknown', None))

        queue.append(Student('0', 4))  # different name, id the same
        self.assertEqual(queue.students[2], Student('4', 4))

        prev_list = queue.students

        queue.append(Student('0', 0))
        self.assertCountEqual(prev_list, queue.students)
        self.assertEqual(Student('0', 0), queue.get_last())

        queue.append_by_name('Unknown')
        self.assertCountEqual(prev_list, queue.students)
        self.assertEqual(Student('Unknown', None), queue.get_last())

    def test_queue_delete_me(self):

        students = [self.bot.registered.get_user_by_id(2),
                    self.bot.registered.get_user_by_id(1),
                    Student('test', None)]
        setup_test_queue(self.bot, 'Queue', students)

        self.context = MagicMock()

        # must not do anything
        tg_set_user(self.u, 3)
        tg_select_command(self.u, modify_queue.RemoveMe)
        self.bot.handle_keyboard_chosen(*self.uc)

        # must delete user
        tg_set_user(self.u, 1)
        tg_select_command(self.u, modify_queue.RemoveMe)
        self.bot.handle_keyboard_chosen(*self.uc)

    def test_queue_add_me(self):

        # must place user to the end
        tg_set_user(self.u, 15, "15")
        tg_select_command(self.u, modify_queue.AddMe)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertEqual(self.bot.get_queue().students[-1], Student("15", 15))

        # must delete user and place him to the end
        existing = Student("3", 3)
        tg_set_user(self.u, existing.id, existing.name)
        prev_pos = self.bot.get_queue().get_student_position(existing)
        tg_select_command(self.u, modify_queue.AddMe)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertEqual(self.bot.get_queue().students[-1], existing)
        self.assertNotEqual(self.bot.get_queue().students[prev_pos], existing)

    def test_select_queue(self):
        tg_select_command(self.u, manage_queues.SelectOtherQueue, self.not_current_queue_name)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertEqual(self.bot.get_queue().name, self.not_current_queue_name)

    def test_delete_queue(self):
        tg_select_command(self.u, manage_queues.DeleteQueue, self.not_current_queue_name)
        self.bot.handle_keyboard_chosen(*self.uc)
        self.assertNotIn(self.not_current_queue_name, self.bot.queues)

    def test_move_queue(self):
        # can move next
        self.bot.get_queue().set_position(0)
        self.assertTrue(self.bot.get_queue().move_next())

        cur_stud, next_stud = self.bot.get_queue().get_cur_and_next()
        self.assertEqual(cur_stud, self.current_queue_students[1])
        self.assertEqual(next_stud, self.current_queue_students[2])

        # move from last element forward
        self.bot.get_queue().set_position(len(self.current_queue_students) - 1)
        cur_stud, next_stud = self.bot.get_queue().get_cur_and_next()
        self.assertIsNotNone(cur_stud)
        self.assertIsNone(next_stud)

        self.bot.get_queue().move_next()
        cur_stud, next_stud = self.bot.get_queue().get_cur_and_next()
        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)

        self.bot.get_queue().move_next()
        cur_stud, next_stud = self.bot.get_queue().get_cur_and_next()
        self.assertIsNone(cur_stud)
        self.assertIsNone(next_stud)

    def test_move_students_command(self):
        pos1 = 5
        pos2 = 3
        prev_students = list(self.bot.get_queue().students)
        s1 = prev_students[pos1 - 1]
        s2 = prev_students[pos2 - 1]

        bot_handle_keyboard(self.bot, *self.uc, modify_queue.MoveStudentPosition, str(s1))
        bot_handle_keyboard(self.bot, *self.uc, modify_queue.MoveStudentPosition, str(s2))

        self.assertCountEqual(prev_students, self.bot.get_queue().students)
        self.assertEqual(self.bot.get_queue().students[pos2 - 1], s1)
        self.assertEqual(self.bot.get_queue().students[pos2 - 2], s2)

    def test_remove_students_list(self):
        tg_select_command(self.u, modify_queue.RemoveListStudents)
        self.bot.handle_keyboard_chosen(*self.uc)

        tg_select_command(self.u, modify_queue.RemoveListStudents, self.queue_students_with_none[1])
        self.bot.handle_keyboard_chosen(*self.uc)
        self.assertNotIn(self.queue_students_with_none[1], self.bot.get_queue().students)

        tg_select_command(self.u, modify_queue.RemoveListStudents, self.queue_students_with_none[2])
        self.bot.handle_keyboard_chosen(*self.uc)
        self.assertNotIn(self.queue_students_with_none[2], self.bot.get_queue().students)
