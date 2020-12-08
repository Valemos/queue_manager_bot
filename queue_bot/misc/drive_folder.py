
import json

class DriveFolder:

    def __init__(self, name, drive_id=None):
        """init only used to create root folders
        :param name: str name of new folder_type
        :param drive_id: str id generated by google api and used to access drive folder_type
        """
        self.name = name
        self.drive_id = drive_id
        self.parent = None
        self.subfolders = {}

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        """
        Overrides attribute call to create and sub folders by attribute call

        If DriveFolder already exists in subfolders, it will be returned

        each existing class attribute can be accessed as always

        :param name:
        :return: DriveFolder
        """

        if name.startswith('__'):
            return getattr(super(), name)

        if name in self.subfolders:
            return self.subfolders[name]
        else:
            new_folder = DriveFolder(name)
            return self.add_folder(new_folder)

    def add_folder(self, folder):
        """
        Performs subfolder append operation for current folder_type
        :param folder: DriveFolder object to add
        :return:
        """
        folder.parent = self
        self.subfolders[folder.name] = folder
        return folder

    def to_json_dict(self):
        """
        returns dictionary for json serialization
        :return: dict object with all necessary data
        """

        folder_dict = {
            "name": self.name,
            "drive_id": self.drive_id if self.drive_id is not None else str(None)
        }

        if len(self.subfolders) > 0:
            folder_dict["subfolders"] = [folder.to_json_dict() for folder in self.subfolders.values()]

        return folder_dict

    @staticmethod
    def validate_json_dict(json_dict: dict):
        """checks if json dictionary contains required fields"""
        if "name" not in json_dict or "drive_id" not in json_dict:
            return False
        return True

    @staticmethod
    def from_json_dict(json_dict: dict):
        """
        recursively decodes json dictionary as DriveFolder object

        :param json_dict: dictionary generated by to_json_dict function
        :return: DriveFolder object
        """

        if not DriveFolder.validate_json_dict(json_dict):
            return None

        folder_id = None if json_dict["drive_id"] == str(None) else json_dict["drive_id"]
        folder = DriveFolder(json_dict["name"], folder_id)

        if "subfolders" in json_dict:
            if isinstance(json_dict["subfolders"], list):
                for subfolder_json in json_dict["subfolders"]:
                    subfolder = DriveFolder.from_json_dict(subfolder_json)
                    subfolder.parent = folder
                    folder.subfolders[subfolder.name] = subfolder

        return folder

    def update_from_json_dict(self, json_dict):
        """
        Reads json dictionary recursively
        updates folders whose names exist in current tree

        If json dict root name does not match with object name, function stops updating
        """

        if not DriveFolder.validate_json_dict(json_dict):
            return

        # update id for current folder_type if name matches
        if self.name == json_dict["name"]:
            self.drive_id = None if json_dict["drive_id"] == str(None) else json_dict["drive_id"]
        else:
            return

        if "subfolders" in json_dict:
            if isinstance(json_dict["subfolders"], list):
                for subfolder_json in json_dict["subfolders"]:
                    if subfolder_json["name"] in self.subfolders:
                        # recursively update subfolder with data
                        self.subfolders[subfolder_json["name"]].update_from_json_dict(subfolder_json)
                    else:
                        # insert new subfolder
                        subfolder = DriveFolder.from_json_dict(subfolder_json)
                        subfolder.parent = self
                        self.subfolders[subfolder.name] = subfolder


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

    another = DriveFolder("other")

    # create folders
    Root.f1.add_folder(another)
    Root.f1.other.drive_id = "hello"

    print(Root.f1.other.drive_id)

    print(", ".join((str(i) for i in Root.get_folder_hierarchy())))

    dct = Root.to_json_dict()
    js = json.dumps(dct)
    print(js)

    ls = DriveFolder.from_json_dict(json.loads(js)).get_folder_hierarchy()
    print(", ".join((str(i) for i in ls)))
