import unittest
from unittest.mock import MagicMock

from queue_bot.bot import parsers
from queue_bot.objects.student import Student
from queue_bot.objects.queue import Queue
from unit_tests.shared_test_functions import students_compare


class TestParsers(unittest.TestCase):

    def test_students_formats(self):
        self.addTypeEqualityFunc(Student, students_compare)

        s1 = Student(''.join(['a' for i in range(50, 60)]), 2**31)
        s2 = Student(''.join(['b' for i in range(50, 130)]), None)
        s3 = Student(''.join(['c' for i in range(50, 60)]), None)
        s5 = Student('', None)
        str1 = s1.str_name_id()
        str2 = s2.str_name_id()
        str3 = s3.str_name_id()
        str4 = 'No'
        str5 = s5.str_name_id()

        self.assertEqual(s1, parsers.parse_student(str1))
        self.assertIsNone(parsers.parse_student(str2))
        self.assertEqual(s3, parsers.parse_student(str3))
        self.assertIsNone(parsers.parse_student(str4))
        self.assertEqual(s5, parsers.parse_student(str5))
