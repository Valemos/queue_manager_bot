from unittest.mock import MagicMock

class DriveFolder:

    def __init__(self, name):
        """init only used to create root folders"""
        self.name = name
        self.subfolders = {}

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        """
        Overrides attribute call to create sub folders only by attribute call

        If DriveFolder already exists in subfolders, it will be returned

        :param name:
        :return: DriveFolder
        """

        if name.startswith('__'):
            return getattr(super(), name)

        if name in self.subfolders:
            return self.subfolders[name]
        else:
            new_folder = DriveFolder(name)
            self.subfolders[name] = new_folder
            return new_folder

    def get_folder_hierarchy(self):
        """
        Returns list all inner DriveFolder objects obtained recursively
        They will be located in desired order of creation
        """
        folders = [self]
        DriveFolder._subfolders_recursion(folders, 0)
        return folders

    @staticmethod
    def _subfolders_recursion(folders: list, index: int):
        """
        Recursively iterates through all folders and
        :param folders:
        :param index:
        """
        if len(folders[index].subfolders) == 0:
            return

        # todo: for each branch at first walk recursively in this branch and than continue to next branch
        folders.extend(folders[index].subfolders.values())
        index += 1
        DriveFolder._subfolders_recursion(folders, index)


if __name__ == '__main__':
    Root = DriveFolder("Root")

    print(Root.f1.f2.f3.name)
    print(Root.f1.f2.f5.name)
    print(Root.f6.f8.name)

    print(", ".join((str(i) for i in Root.get_folder_hierarchy())))
