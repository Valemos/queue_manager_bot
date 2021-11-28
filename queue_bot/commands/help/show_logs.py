from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class ShowLogs(Command):
    command_name = 'logs'
    description = commands_descriptions.logs_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        trim = 4090
        trimmed_msg = bot.logger.get_logs()[-trim:]
        if len(trimmed_msg) >= trim:
            trimmed_msg = "...\n" + trimmed_msg[trimmed_msg.index('\n'):]

        update.effective_chat.send_message(trimmed_msg)