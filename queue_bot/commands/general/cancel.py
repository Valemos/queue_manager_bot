from queue_bot.commands.command import Command


class Cancel(Command):

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_message.delete()
        bot.request_del()