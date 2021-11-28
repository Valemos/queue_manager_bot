import queue_bot.commands
from queue_bot.bot.parsers import check_queue_single_command
from queue_bot.commands.misc.logging import log_bot_queue


def handle_queue_create_single_command(update, bot, generate_function):
    # todo refactor queue creation
    queue_name, names = parsers.parse_queue_message(update.message.text)
    students = bot.registered_manager.get_registered_students(names)
    queue = bot.queues_manager.create_queue(bot)

    if queue_name is None:
        queue_name = bot.language_pack.default_queue_name

    queue.name = queue_name
    generate_function(queue, students)

    handle_add_queue(update, bot, queue)


def handle_queue_create_message(cmd, update, bot, generate_function):
    # simple command runs chain of callbacks
    if bot.queues_manager.can_add_queue():
        if check_queue_single_command(update.message.text):
            queue_bot.commands.create_queue.misc.handle_queue_create_single_command(update, bot, generate_function)
        else:
            CreateQueue.queue_generate_function = generate_function
            queue_bot.commands.create_queue.select_students.SelectStudents.handle_reply(update, bot)
    else:
        update.effective_chat.send_message(bot.language_pack.queue_limit_reached)


def handle_add_queue(update, bot, queue):
    if bot.queues_manager.can_add_queue():
        bot.queues_manager.add_queue(queue)
        queue_bot.commands.create_queue.finish_creation.FinishCreation.handle_reply(update, bot)
    else:
        update.effective_chat.send_message(bot.language_pack.queue_limit_reached)
        bot.request_del()
        log_bot_queue(update, bot, 'queue limit reached')