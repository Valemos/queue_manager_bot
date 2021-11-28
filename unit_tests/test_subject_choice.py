import unittest

from unit_tests.shared_test_functions import *
import queue_bot.commands.command as commands



@unittest.skip("functionality is not used")
class TestSubjectChoices(unittest.TestCase):


    @mock.patch('queue_bot.subject_choice_manager.SubjectChoiceGroup.save_to_excel')
    def test_setup_subjects(self):
        bot = setup_test_bot(self)
        tg_set_user(update, 1)
        bot_request_command_send_msg(bot, commands.CollectSubjectChoices.CreateNewCollectFile, update, context)
        bot_handle_message(bot, 'Test', update, context)
        bot_handle_message(bot, '1-15', update, context)
        bot_handle_message(bot, '3', update, context)

        self.assertEqual('Test', bot.choice_manager.current_subject.name)
        self.assertEqual((1, 15), bot.choice_manager.current_subject.available_range)
        self.assertEqual(3, bot.choice_manager.current_subject.repeat_limit)


    @mock.patch('queue_bot.subject_choice_manager.SubjectChoiceGroup.save_to_excel')
    def test_show_empty(self):
        bot = setup_test_bot(self)


        bot_request_command_send_msg(bot, commands.CollectSubjectChoices.ShowCurrentChoices, update, context)
        update.effective_chat.send_message.assert_called_with(bot.language_pack.choices_collection_not_started)


    @mock.patch('queue_bot.subject_choice_manager.SubjectChoiceGroup.save_to_excel')
    def test_choose_subjects(self):
        bot = setup_test_bot(self)

        bot = setup_test_subject_choices(bot)
        bot.choice_manager.can_choose = False

        tg_set_user(update, 1)
        bot_request_command(bot, commands.CollectSubjectChoices.StartChoose, update, context)
        self.assertTrue(bot.choice_manager.can_choose)

        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 5 8 7')
        self.assertListEqual([1, 5, 8, 7], bot.choice_manager.current_subject.student_choices[-1].priority_choices)

        # can add first subjects because limit is 2 students per subject
        tg_set_user(update, 2)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 5 8 7')
        self.assertEqual(1, bot.choice_manager.current_subject.student_choices[-1].finally_chosen)

        # cannot add first subject, so adds second
        tg_set_user(update, 3)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 5 8 7')
        self.assertEqual(5, bot.choice_manager.current_subject.student_choices[-1].finally_chosen)

        # choose topic 5 second time
        tg_set_user(update, 4)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '5')

        # report, that cannot choose any
        tg_set_user(update, 5)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 5')
        update.message.reply_text.assert_called_with(bot.language_pack.cannot_choose_any_subject)
        self.assertEqual(4, len(bot.choice_manager.current_subject.student_choices))

        # must choose 6
        tg_set_user(update, 5)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 5 6 10 9')
        self.assertEqual(6, bot.choice_manager.current_subject.student_choices[-1].finally_chosen)

        tg_set_user(update, 1)
        bot_request_command(bot, commands.CollectSubjectChoices.StopChoose, update, context)
        self.assertFalse(bot.choice_manager.can_choose)


    @mock.patch('queue_bot.subject_choice_manager.SubjectChoiceGroup.save_to_excel')
    def test_unknown_choose_subjects(self):
        bot = setup_test_bot(self)

        bot = setup_test_subject_choices(bot)

        bot.choice_manager.current_subject.repeat_limit = 1

        tg_set_user(update, 1)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 5 8 7')
        self.assertEqual(1, len(bot.choice_manager.current_subject.student_choices))

        # must not add chosen subjects and current choices is none
        tg_set_user(update, None, 'Unknown')
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 8 6 10')
        self.assertEqual(Student('Unknown', None), bot.choice_manager.current_subject.student_choices[1].student)
        self.assertEqual(8, bot.choice_manager.current_subject.student_choices[1].finally_chosen)



    @mock.patch('queue_bot.subject_choice_manager.SubjectChoiceGroup.save_to_excel')
    def test_remove_subjects(self):
        bot = setup_test_bot(self)

        bot = setup_test_subject_choices(bot)

        tg_set_user(update, 1)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '1 5 8 7')

        tg_set_user(update, 2)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '6 5 11 3')

        tg_set_user(update, 3)
        bot_request_command(bot, commands.CollectSubjectChoices.Choose, update, context, '6 5 11 3')

        # must not change chosen subjects
        tg_set_user(update, 2)
        bot_request_command(bot, commands.CollectSubjectChoices.RemoveChoice, update, context)
        self.assertEqual(2, len(bot.choice_manager.current_subject.student_choices))
        self.assertEqual(bot.registered_manager.get_user_by_id(1),
                         bot.choice_manager.current_subject.student_choices[0].student)
        self.assertEqual(bot.registered_manager.get_user_by_id(3),
                         bot.choice_manager.current_subject.student_choices[1].student)
