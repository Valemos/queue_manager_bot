import unittest

import queue_bot.commands as commands
from queue_bot.objects.access_level import AccessLevel
from unit_tests.shared_test_functions import *


class TestRegisteredManager(unittest.TestCase):

    def test_bot_check_access(self):
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

    def test_get_user(self):
        bot = setup_test_bot(self)

        user = bot.registered_manager.get_user_by_name('0')
        self.assertEqual(user, Student('0', 0))

        user = bot.registered_manager.get_user_by_name('NoSuchName')
        self.assertIsNone(user)

        user = bot.registered_manager.get_user_by_id(4)
        self.assertEqual(Student('4', 4), user)

        user = bot.registered_manager.get_user_by_id(100)
        self.assertIsNone(user)

    def test_name_similarity(self):
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

    def test_delete_list(self):
        bot = setup_test_bot(self)
        students = list(bot.registered_manager.get_users())

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.modify_registered.RemoveListUsers)
        bot.handle_keyboard_chosen(update, context)

        self.assertIn(students[1], bot.registered_manager.get_users())
        tg_select_command(update, commands.modify_registered.RemoveListUsers,
                          students[1].str_name_id())
        bot.handle_keyboard_chosen(update, context)
        self.assertNotIn(students[1], bot.registered_manager.get_users())

        self.assertIn(students[2], bot.registered_manager.get_users())
        tg_select_command(update, commands.modify_registered.RemoveListUsers,
                          students[2].str_name_id())
        bot.handle_keyboard_chosen(update, context)
        self.assertNotIn(students[2], bot.registered_manager.get_users())

    def test_add_remove_admin(self):
        bot = setup_test_bot(self)

        update = MagicMock()
        context = MagicMock()

        tg_set_user(update, 1)
        tg_select_command(update, commands.manage_access.AddAdmin)
        bot.handle_keyboard_chosen(update, context)
        tg_forward_message(update, 100, '100')
        bot.handle_message_reply_command(update, context)
        self.assertIs(bot.registered_manager.get_user_by_id(100).access_level, AccessLevel.ADMIN)

        tg_select_command(update, commands.manage_access.AddAdmin)
        bot.handle_keyboard_chosen(update, context)
        tg_forward_message(update, 3, '3')
        bot.handle_message_reply_command(update, context)
        self.assertIs(bot.registered_manager.get_user_by_id(3).access_level, AccessLevel.ADMIN)

        test_st = bot.registered_manager.get_user_by_id(100)
        tg_select_command(update, commands.manage_access.RemoveAdmin, test_st)
        bot.handle_keyboard_chosen(update, context)
        self.assertIn(test_st, bot.registered_manager)
        self.assertIs(bot.registered_manager.get_user_by_id(100).access_level, AccessLevel.USER)

        test_st = bot.registered_manager.get_user_by_id(3)
        tg_select_command(update, commands.manage_access.RemoveAdmin, test_st)
        bot.handle_keyboard_chosen(update, context)
        self.assertIn(test_st, bot.registered_manager)
        self.assertIs(bot.registered_manager.get_user_by_id(3).access_level, AccessLevel.USER)
