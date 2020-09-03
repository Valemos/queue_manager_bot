# this class controls telegram message, that must be located somewhere in chat
# this message must be updated, or destroyed and created again

class UpdatableMessage:
    def __init__(self, message=None):
        self.message = message

    def send_new(self, chat, contents, keyboard):
        if self.message is not None:
            self.message.delete()
        self.message = chat.send_message(contents, reply_markup=keyboard)

    def update_contents(self, chat, contents, keyboard):
        if self.message is not None:
            new_text = contents
            if self.message.text != new_text:
                self.message = self.message.edit_text(new_text, reply_markup=keyboard)
        else:
            self.send_new(chat, contents, keyboard)
