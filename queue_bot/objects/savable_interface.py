class Savable:
    def get_save_files(self):
        raise NotImplementedError

    def save_to_file(self, saver):
        raise NotImplementedError

    def load_file(self, saver):
        raise NotImplementedError