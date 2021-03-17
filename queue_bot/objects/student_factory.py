from queue_bot.objects.student_abstract import AbstractStudent
from queue_bot.objects.student import Student
from queue_bot.objects.student_no_id import StudentNoId


def student_factory(obj, telegram_id=None):
    if isinstance(obj, AbstractStudent):
        obj, telegram_id = obj.name, obj.telegram_id

    if telegram_id is not None:
        return Student(obj, telegram_id)
    else:
        return StudentNoId(obj)
