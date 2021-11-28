from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class Stop(Command):
    command_name = 'stop'
    description = commands_descriptions.stop_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        update.message.reply_text(bot.language_pack.bot_stopped)
        bot.stop()