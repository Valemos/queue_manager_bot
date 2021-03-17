from queue_bot.objects.student_abstract import AbstractStudent


class StudentNoId(AbstractStudent):
    def __init__(self, name):
        super().__init__(name, None)

    def get_id(self):
        return self.name

    def get_name(self):
        return self.name

    def name_id_str(self):
        return f"{self.get_name()}: no id"
