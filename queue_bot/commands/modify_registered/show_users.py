from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel


class ShowListUsers(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.registered_manager.get_users_str())