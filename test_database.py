# test queue creation and loading
from queue_bot.database import db_session, init_database
from queue_bot.objects.queue_students import QueueStudents, QueueParameters, Student
from queue_bot.objects.registered_manager import RegisteredManager

init_database()

session = db_session()
students = [Student("A", 10), Student("B", 11), Student("C", 12)]
q = QueueStudents(QueueParameters(RegisteredManager(students)))
q.generate_random(students)

for student in students:
    session.add(student)

session.add(q)
session.commit()

session = db_session()
for q in session.query(QueueStudents).all():
    print(q)

for s in session.query(Student).all():
    print(s)
