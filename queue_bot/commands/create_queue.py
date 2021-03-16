from typing import Type

from queue_bot.bot import parsers as parsers
from queue_bot.bot.access_levels import AccessLevel
from queue_bot.languages import command_descriptions_rus as commands_descriptions

from .abstract_command import AbstractCommand
from .logging_shortcuts import log_bot_queue, log_bot_user
from .inrerface_settings_builder import ISettingsBuilderCommand


def create_queue(update, bot):
    new_queue = bot.new_queue()
    if new_queue is not None:
        return new_queue
    else:
        update.effective_chat.send_message(bot.language_pack.queue_limit_reached)
        bot.request_del()
        log_bot_queue(update, bot, 'queue limit reached')
        return None


def handle_create_queue_dialog(cmd: Type[ISettingsBuilderCommand], update, bot):
    # simple command runs chain of callbacks
    if bot.queues.can_add_queue():
        if parsers.is_single_queue_command(update.message.text):
            handle_create_queue_instant(update, bot, cmd.settings)
        else:
            SelectStudentList.handle_reply_settings(update, bot, cmd.settings)
    else:
        update.effective_chat.send_message(bot.language_pack.queue_limit_reached)


def handle_create_queue_instant(update, bot, is_random):
    queue_name, names = parsers.parse_queue_message(update.message.text)
    students = bot.registered_manager.get_registered_students(names)

    queue = create_queue(update, bot)
    if queue is None:
        return

    queue.name = queue_name if queue_name is not None else bot.language_pack.default_queue_name
    queue.generate(students, is_random)


class CreateSimple(AbstractCommand, ISettingsBuilderCommand):
    command_name = 'new_queue'
    description = commands_descriptions.new_queue_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        cls.settings.is_random = False
        handle_create_queue_dialog(cls, update, bot)

    @classmethod
    def handle_request(cls, update, bot):
        handle_create_queue_instant(update, bot, is_random=False)


class CreateRandom(AbstractCommand, ISettingsBuilderCommand):
    command_name = 'new_random_queue'
    description = commands_descriptions.new_random_queue_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        cls.settings.is_random = True
        handle_create_queue_dialog(cls, update, bot)

    @classmethod
    def handle_request(cls, update, bot):
        handle_create_queue_instant(update, bot, is_random=True)


class SelectStudentList(AbstractCommand, ISettingsBuilderCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.enter_students_list,
                                           reply_markup=bot.keyboards.set_empty_queue)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        names = parsers.parse_names(update.message.text)
        cls.settings.students = bot.registered_manager.get_registered_students(names)

        AddNameToQueue.handle_reply_settings(update, bot, cls.settings)


class SetEmptyStudents(AbstractCommand, ISettingsBuilderCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        cls.settings.students = []
        AddNameToQueue.handle_reply_settings(update, bot, cls.settings)


class AddNameToQueue(AbstractCommand, ISettingsBuilderCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        # TODO check if settings working correctly
        if cls.settings.name is not None:
            update.effective_chat.send_message(bot.language_pack.enter_queue_name,
                                               reply_markup=bot.keyboards.set_default_queue_name)
            bot.request_set(cls)
        else:
            bot.request_del()
            log_bot_queue(update, bot, 'in AddNameToQueue queue is None. Error')

    @classmethod
    def handle_request(cls, update, bot):
        if parsers.check_queue_name(update.message.text):
            cls.settings.name = update.message.text
            FinishQueueCreation.handle_request(update, bot)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)
            AddNameToQueue.handle_reply_settings(update, bot, cls.settings)

        log_bot_queue(update, bot, 'queue name set {0}', update.message.text)


class DefaultQueueName(AbstractCommand, ISettingsBuilderCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        cls.settings.name = bot.language_pack.default_queue_name
        log_bot_user(update, bot, 'queue set default name')
        FinishQueueCreation.settings = cls.settings
        FinishQueueCreation.handle_request(update, bot)


class FinishQueueCreation(AbstractCommand, ISettingsBuilderCommand):
    access_requirement = AccessLevel.ADMIN

    # this function only shows message about queue finished creation
    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.queue_set)

    # this function handles end of dialog chain
    @classmethod
    def handle_request(cls, update, bot):
        if cls.settings.is_valid():
            queue = create_queue(bot, update)
            if queue is None:
                return

            queue.name = cls.settings.name
            queue.generate(cls.settings.students, cls.settings.is_random)

            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'queue set')

            FinishQueueCreation.handle_reply(update, bot)
        else:
            log_bot_user(update, bot, 'Fatal error: cannot finish queue creation')
        bot.request_del()


class CreateRandomFromRegistered(AbstractCommand, ISettingsBuilderCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        queue = create_queue(update, bot)
        if queue is None:
            return

        queue.generate_random(bot.registered.get_users())  # we specify parameter in "self"

        if not bot.queues.add_queue(queue):
            update.effective_chat.send_message(bot.language_pack.queue_limit_reached)
            bot.request_del()
            log_bot_queue(update, bot, 'queue limit reached')
        else:
            err_msg = bot.last_queue_message.update_contents(bot.queues.get_queue_str(),
                                                             update.effective_chat)
            if err_msg is not None:
                log_bot_queue(update, bot, err_msg)

            update.effective_chat.send_message(bot.language_pack.queue_set)
            log_bot_queue(update, bot, 'queue added')
            AddNameToQueue.handle_reply_settings(update, bot, cls.settings)
