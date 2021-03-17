# this class controls telegram message, that must be located somewhere in chat
# this message must be updated, or destroyed and created again


class UpdatableMessage:
    def __init__(self, default_keyboard=None):
        self.chat_message = {}
        self.default_keyboard = default_keyboard

    def message_exists(self, chat):
        if chat.telegram_id in self.chat_message:
            if self.chat_message[chat.telegram_id] is not None:
                return True
        return False

    def resend(self, contents, chat, keyboard=None):
        if keyboard is None:
            keyboard = self.default_keyboard

        if chat.telegram_id in self.chat_message:
            # delete message in current chat
            self.chat_message[chat.telegram_id].delete()
            del self.chat_message[chat.telegram_id]

        self.chat_message[chat.telegram_id] = chat.send_message(contents, reply_markup=keyboard)

    def update_contents(self, contents, chat, keyboard=None):
        """Returns error message if update was not successful"""
        try:
            if chat.telegram_id not in self.chat_message:
                self.resend(contents, chat, keyboard)

            for chat_id in self.chat_message.keys():
                if self.chat_message[chat_id].text != contents:
                    self.chat_message[chat_id] = \
                        self.chat_message[chat_id].edit_text(contents, reply_markup=self.chat_message[chat_id].reply_markup)
            return None
        except Exception as exc:
            return f"ERROR {str(type(exc))}: {exc.args}"