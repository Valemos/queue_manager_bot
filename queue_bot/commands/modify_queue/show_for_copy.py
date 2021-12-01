from queue_bot.bot import parsers
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class ShowQueueForCopy(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        if bot.check_queue_selected():
            queue = get_chat_queues(update.effective_chat.id).get_queue()
            member_names = queue.get_member_names()
            queue_name = queue.get_name()
            message = parsers.copy_queue_format.format(name=queue_name, students='\n'.join(member_names))
            update.effective_chat.send_message(message)
            update.effective_chat.send_message(language_pack.copy_queue)

            log_bot_queue(update, bot, 'showed list for copy')
        else:
            update.effective_chat.send_message(language_pack.queue_not_selected)
