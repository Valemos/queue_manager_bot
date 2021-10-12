from queue_bot.database import db_session, init_database
from queue_bot.objects.student_abstract import AbstractStudent


class Student(AbstractStudent):

    def __init__(self, name, telegram_id):
        super().__init__(name, telegram_id)

    def get_id(self):
        return self.telegram_id

    def get_name(self):
        return self.name


if __name__ == '__main__':
    init_database()

    session = db_session()
    session.add(student_factory("Dmytro", 228))
    session.commit()

    for student in session.query(Student).all():
        print(student)
