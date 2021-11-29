import unittest

from queue_bot.database import Session, create_all_tables, drop_all_tables
from queue_bot.objects import Student, Queue
from queue_bot.objects.registered_manager import get_chat_registered


class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        create_all_tables()

    def tearDown(self) -> None:
        drop_all_tables()

    def test_student_inserted(self):
        with Session() as session:
            reg = get_chat_registered(1)
            session.add(reg)
            reg.add_new_user('Petyr', 1)

        with Session() as session:
            result = session.query(Student).first()

            self.assertEqual("Petyr", result.name)
            self.assertEqual(1, result.telegram_id)

    def test_queue_inserted(self):
        # queue = StudentsQueue("science", [QueueMember])
        pass
