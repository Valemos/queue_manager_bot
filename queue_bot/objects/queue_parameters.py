from queue_bot.languages import bot_messages_rus as language_pack


class QueueParameters:
    def __init__(self, registered, name=None, init_students=None):
        self.registered = registered
        self.name = name if name is not None else language_pack.default_queue_name
        self.students = init_students if init_students is not None else []
