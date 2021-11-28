from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class SaveToDrive(Command):
    command_name = 'sq'
    description = commands_descriptions.save_queues_to_drive
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_request(cls, update, bot):
        bot.save_to_cloud()
        update.effective_chat.send_message(bot.language_pack.queues_saved_to_cloud)