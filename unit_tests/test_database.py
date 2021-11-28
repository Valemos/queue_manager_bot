import unittest

from queue_bot.database import SessionFactory, Session, create_all_tables, drop_all_tables
from queue_bot.objects.student import Student


class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        create_all_tables()

    def tearDown(self) -> None:
        drop_all_tables()

    def test_student_inserted(self):
        with SessionFactory() as session:
            student = Student("Name", 1)
            session.add(student)
            session.commit()

        with SessionFactory() as session:
            result = session.query(Student).first()

            self.assertEqual("Name", result.name)
            self.assertEqual(1, result.telegram_id)
