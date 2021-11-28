import unittest

from queue_bot.objects.student import Student


class TestQueueObjects(unittest.TestCase):

    def test_students_equality(self):
        s1 = Student('name1', 1)
        s2 = Student('name2', 1)
        self.assertTrue(s1 == s2)

        s1 = Student('name1', None)
        s2 = Student('name1', None)
        self.assertTrue(s1 == s2)

        s1 = Student('name1', None)
        s2 = Student('name2', None)
        self.assertFalse(s1 == s2)

        s1 = Student('name1', 1)
        s2 = Student('name1', None)
        self.assertFalse(s1 == s2)

        s1 = Student('name1', 1)
        s2 = Student('name1', 3)
        self.assertFalse(s1 == s2)

        s1 = Student('name1', 1)
        s2 = Student('name2', 3)
        self.assertFalse(s1 == s2)
