from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class ShowMenu(Command):
    command_name = 'edit_registered'
    description = commands_descriptions.edit_registered_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.title_edit_registered,
                                           reply_markup=bot.keyboards.modify_registered)