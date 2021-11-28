from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class ShowMenu(Command):
    command_name = 'edit_queue'
    description = commands_descriptions.edit_queue_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.message.reply_text(bot.language_pack.title_edit_queue,
                                  reply_markup=bot.keyboards.modify_queue)