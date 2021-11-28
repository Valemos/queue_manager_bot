
# todo add persistence to usages
class QueueCreateDialogState:
    def __init__(self):
        self.new_queue_name = None
        self.new_queue_students = None
        self.queue_generate_function = None

    def is_valid(self):
        return self.new_queue_name is not None and \
               self.new_queue_students is not None and \
               self.queue_generate_function is not None
