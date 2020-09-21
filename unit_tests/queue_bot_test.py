import unittest

import pickle
from pathlib import Path
from queue_bot.students_queue import StudentsQueue
from queue_bot.student import Student
from queue_bot.registered_manager import StudentsRegisteredManager
from queue_bot.object_file_saver import ObjectSaver, FolderType


class TestQueue(unittest.TestCase):

    def test_save_load_registered(self):
        students = [Student('Test1', 0), Student('Test2', 1)]
        reg = StudentsRegisteredManager(students)
        saver = ObjectSaver(default_folder=FolderType.Test)
        reg.save_to_file(saver)
        reg._students_reg = []
        reg.load_file(saver)
        self.assertEqual(students[0], reg._students_reg[0])
        self.assertEqual(students[1], reg._students_reg[1])

        ObjectSaver.clear_folder(FolderType.Test.value)

    def test_save_load_queue(self):
        students = [Student('Test1', 0), Student('Test2', 1)]
        reg = StudentsRegisteredManager(students)
        que = StudentsQueue(reg, None, students)
        saver = ObjectSaver(default_folder=FolderType.Test)
        que.save_to_file(saver)
        que._students = []
        que.load_file(saver)
        self.assertEqual(students[0], que._students[0])
        self.assertEqual(students[1], que._students[1])

        ObjectSaver.clear_folder(FolderType.Test.value)


    def test_create_simple(self):
        reg_manager = StudentsRegisteredManager()
        queue = StudentsQueue(reg_manager, None)



if __name__ == '__main__':
    unittest.main()
