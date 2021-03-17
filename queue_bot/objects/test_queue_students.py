from test.fixtures import *


def test_move_prev(queue):
    assert queue.position == 0

    queue.move_prev()
    assert queue.position == 0

    queue.set_position(3)
    assert queue.position == 3

    queue.move_prev()
    assert queue.position == 2


def test_move_next():
    assert False


def test_update_positions(queue):
    assert False


def test_move_to_index():
    assert False


def test_move_to_end():
    assert False


def test_swap_students():
    assert False


def test_append():
    assert False


def test_set_students():
    assert False


def test_clear():
    assert False


def test_remove_student():
    assert False


def test_remove_by_index():
    assert False


def test_remove_by_id():
    assert False


def test_remove_by_name():
    assert False


def test_get_student_position():
    assert False


def test_set_student_position():
    assert False
