# test queue creation and loading
from queue_bot.database import db_session, init_database
from queue_bot.objects.queue_students import QueueStudents, QueueParameters, Student
from queue_bot.objects.registered_manager import RegisteredManager
from queue_bot.objects.student_factory import student_factory

init_database()

session = db_session()
students = [student_factory("A", 10), student_factory("B", 11), student_factory("C", 12)]
q = QueueStudents.from_params(QueueParameters(RegisteredManager(students), "test", students))

for student in students:
    session.add(student)

session.add(q)
session.commit()

session = db_session()
for q in session.query(QueueStudents).all():
    for s in q.stud_ordered:
        print(s.student)

for s in session.query(Student).all():
    print(s)

session.close()
