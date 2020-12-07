import unittest

from queue_bot import bot_commands
from unit_tests.shared_test_functions import *


class TestQueue(unittest.TestCase):


    def setUp(self) -> None:
        self.bot = setup_test_bot(self)
        
        self.queue_students = list(self.bot.registered_manager.get_users())

        self.student_none = Student('t', None)
        self.student_none_index = 3
        self.queue_students.insert(self.student_none_index, self.student_none)

        self.bot = setup_test_queue(self.bot, 'idNone', self.queue_students)
        self.bot = setup_test_queue(self.bot, 'reg', self.bot.registered_manager.get_users())

        self.not_current_queue_name = None
        for queue_name in self.bot.queues_manager.queues:
            if queue_name != self.bot.queues_manager.get_queue().name:
                self.not_current_queue_name = queue_name
        self.assertIsNotNone(self.not_current_queue_name)

        from unittest.mock import MagicMock

        # update and context variables for every command handler in telegram api
        self.uc = MagicMock(), MagicMock()


    def test_queue_create_simple(self):
        tg_set_user(self.uc[0], 1)
        bot_request_command_send_msg(self.bot, bot_commands.CreateQueue.CreateSimple, *self.uc)
        bot_handle_message(self.bot, '0\n1\ntest\n2', *self.uc)
        bot_handle_message(self.bot, 'Name', *self.uc)

        self.assertListEqual(self.bot.queues_manager.get_queue().students,
                             [Student('0', 0), Student('1', 1), Student('test', None), Student('2', 2)])


    def test_queue_create_random(self):

        tg_set_user(self.uc[0], 1)
        bot_request_command_send_msg(self.bot, bot_commands.CreateQueue.CreateRandom, *self.uc)

        tg_write_message(self.uc[0], '0\n1\ntest\n2')
        self.bot.handle_message_reply_command(*self.uc)

        tg_write_message(self.uc[0], 'Name')
        self.bot.handle_message_reply_command(*self.uc)

        self.assertCountEqual(self.bot.get_queue().students,
                              [Student('0', 0), Student('1', 1), Student('test', None), Student('2', 2)])


    def test_queue_general_features(self):
        tg_set_user(self.uc[0], 1)

        bot_request_command_send_msg(self.bot, bot_commands.CreateQueue.CreateSimple, *self.uc)

        # write queue data
        names = '\n'.join([st.name for st in self.queue_students[:-2]])
        tg_write_message(self.uc[0], names)
        self.bot.handle_message_reply_command(*self.uc)
        
        prev_queue_name = self.bot.queues_manager.get_queue().name
        tg_write_message(self.uc[0], 'name')
        self.bot.handle_message_reply_command(*self.uc)

        self.assertEqual(self.bot.get_queue().name, 'name')
        # we skipped two last elements while initializing queue with name "name"
        self.assertListEqual(self.bot.get_queue().students, self.queue_students[:-2])

        # test previous queue selection
        self.bot.queues_manager.remove_queue('name')
        self.assertEqual(self.bot.get_queue().name, prev_queue_name)
        self.assertListEqual(self.bot.get_queue().students, self.queue_students)

        # 'test' rename
        tg_select_command(self.uc[0], bot_commands.ManageQueues.RenameQueue, prev_queue_name)
        self.bot.handle_keyboard_chosen(*self.uc)

        tg_write_message(self.uc[0], 'new_name')
        self.bot.handle_message_reply_command(*self.uc)
        self.assertIn('new_name', self.bot.queues_manager.queues)
        self.assertNotIn(prev_queue_name, self.bot.queues_manager.queues)


    def test_swap_users_in_queue(self):

        first_user = self.bot.registered_manager.get_users()[2]
        second_user = self.bot.registered_manager.get_users()[4]

        tg_set_user(self.uc[0], 1)
        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.MoveSwapStudents)
        self.bot.handle_keyboard_chosen(*self.uc)  # must only create keyboard

        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.MoveSwapStudents, str(first_user))
        self.bot.handle_keyboard_chosen(*self.uc)
        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.MoveSwapStudents, str(second_user))
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertCountEqual(self.bot.get_queue().students, self.bot.registered_manager.get_users())
        self.assertEqual(second_user, self.bot.get_queue().students[2])
        self.assertEqual(first_user, self.bot.get_queue().students[4])


    def test_queue_copy(self):
        text = self.bot.get_queue().get_str_for_copy()

        # delete queues and start with empty bot
        empty_bot = setup_test_bot(self)

        bot_handle_text_command(empty_bot, *self.uc, '/new_queue')
        self.assertIsNone(empty_bot.get_queue())

        bot_handle_text_command(empty_bot, *self.uc, text)
        # todo: fix empty_bot.get_queue() is None after bot command
        self.assertListEqual(empty_bot.get_queue().students, self.queue_students)


    def test_create_with_empty_lines(self):
        tg_set_user(self.uc[0], 1)
        bot_request_command_send_msg(self.bot, bot_commands.CreateQueue.CreateSimple, *self.uc)

        message = '''Дурда + Козинцева

Вороной + Василюк

Люлька + Кущевой

Прокопенко + Гречко

Мотрук + Скицюк

Воловик + Комисар

Копылаш + Редька

Северян + Дорошенко'''

        tg_write_message(self.uc[0], message)
        self.bot.handle_message_reply_command(*self.uc)

        tg_select_command(self.uc[0], bot_commands.CreateQueue.DefaultQueueName)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertListEqual([Student('Дурда + Козинцева', None),
                              Student('Вороной + Василюк', None),
                              Student('Люлька + Кущевой', None),
                              Student('Прокопенко + Гречко', None),
                              Student('Мотрук + Скицюк', None),
                              Student('Воловик + Комисар', None),
                              Student('Копылаш + Редька', None),
                              Student('Северян + Дорошенко', None)],
                             self.bot.queues_manager.get_queue().students)


    def test_queue_add_user(self):
        queue = StudentsQueue(self.bot)

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


    def test_queue_delete_me(self):

        students = [self.bot.registered_manager.get_user_by_id(2),
                    self.bot.registered_manager.get_user_by_id(1),
                    Student('test', None)]
        bot = setup_test_queue(self.bot, 'Queue', students)


        self.context = MagicMock()

        # must not do anything
        tg_set_user(self.uc[0], 3)
        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.RemoveMe)
        self.bot.handle_keyboard_chosen(*self.uc)

        # must delete user
        tg_set_user(self.uc[0], 1)
        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.RemoveMe)
        self.bot.handle_keyboard_chosen(*self.uc)


    def test_queue_add_me(self):

        students = [self.bot.registered_manager.get_user_by_id(2),
                    self.bot.registered_manager.get_user_by_id(1),
                    Student('test', None)]
        bot = setup_test_queue(self.bot, 'Queue', students)




        # must not do anything
        tg_set_user(self.uc[0], 3)
        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.AddMe)
        self.bot.handle_keyboard_chosen(*self.uc)

        # must delete user
        tg_set_user(self.uc[0], 1)
        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.AddMe)
        self.bot.handle_keyboard_chosen(*self.uc)


    def test_select_queue(self):
        tg_set_user(self.uc[0], 1)
        tg_select_command(self.uc[0], bot_commands.ManageQueues.SelectOtherQueue, self.not_current_queue_name)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertEqual(self.bot.queues_manager.get_queue().name, self.not_current_queue_name)


    def test_delete_queue(self):
        tg_set_user(self.uc[0], 1)
        tg_select_command(self.uc[0], bot_commands.ManageQueues.DeleteQueue, self.not_current_queue_name)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertNotIn(self.not_current_queue_name, self.bot.queues_manager)


    def test_correct_queue_indexes(self):

        bot = setup_test_queue(self.bot, 'test', self.bot.registered_manager.get_users())

        self.bot.queues_manager.get_queue().set_position(3)
        cur_stud, next_stud = self.bot.queues_manager.get_queue().get_cur_and_next()

        # if we delete current user, next element must become current
        self.bot.queues_manager.get_queue().remove_by_index(3)
        self.assertNotIn(cur_stud, self.bot.queues_manager.get_queue())
        self.assertEqual(next_stud, self.bot.queues_manager.get_queue().get_current())

        # if we delete user from larger position, current student must stay
        cur_stud, next_stud = self.bot.queues_manager.get_queue().get_cur_and_next()
        self.bot.queues_manager.get_queue().set_position(2)
        self.bot.queues_manager.get_queue().remove_by_index(3)
        self.assertEqual(cur_stud, self.bot.queues_manager.get_queue().get_current())

        # if we delete user before current, it must remain on it`s place
        cur_stud, next_stud = self.bot.queues_manager.get_queue().get_cur_and_next()
        self.bot.queues_manager.get_queue().set_position(2)
        self.bot.queues_manager.get_queue().remove_by_index(1)
        self.assertEqual(cur_stud, self.bot.queues_manager.get_queue().get_current())


    def test_remove_students_list(self):

        students = [self.bot.registered_manager.get_user_by_id(2),
                    self.bot.registered_manager.get_user_by_id(1),
                    Student('test', None),
                    self.bot.registered_manager.get_user_by_id(4)]
        bot = setup_test_queue(self.bot, 'Queue', students)

        tg_set_user(self.uc[0], 1)
        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.RemoveListStudents)
        self.bot.handle_keyboard_chosen(*self.uc)

        self.assertListEqual(students, self.bot.get_queue().students)

        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.RemoveListStudents, students[1])
        self.bot.handle_keyboard_chosen(*self.uc)
        self.assertNotIn(students[1], self.bot.get_queue().students)

        tg_select_command(self.uc[0], bot_commands.ModifyCurrentQueue.RemoveListStudents, students[2])
        self.bot.handle_keyboard_chosen(*self.uc)
        self.assertNotIn(students[2], self.bot.get_queue().students)


    def test_set_student_first_position(self):
        # todo: write this test case
        return
        selected_student = self.bot.queues_manager.get_queue()
        
        # get generated keyboard
        bot_handle_keyboard(self.bot, *self.uc, bot_commands.ModifyCurrentQueue.MoveStudentPosition)

        self.uc[0].effective_chat.send_message.assert_called_once()
        keyboard = self.uc[0].effective_chat.send_message.call_args_list
