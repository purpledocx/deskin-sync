import pytest
from types import SimpleNamespace

from app.strategies.role_strategy import (
    AdminStrategy, StudentStrategy, TeacherStrategy, get_strategy,
)



def make_user(user_id, role):
    return SimpleNamespace(id=user_id, role=SimpleNamespace(name=role))


def make_booking(user_id):
    return SimpleNamespace(user_id=user_id)


@pytest.mark.parametrize("role, cls", [
    ("Student", StudentStrategy),
    ("Teacher", TeacherStrategy),
    ("Admin", AdminStrategy),
])
def test_get_strategy_returns_class_for_role(role, cls):
    assert isinstance(get_strategy(make_user(1, role)), cls)


def test_unknown_role_falls_back_to_student():
    assert isinstance(get_strategy(make_user(1, "Hacker")), StudentStrategy)


def test_student_manages_only_own_bookings():
    s = StudentStrategy()
    assert s.can_manage_booking(make_booking(1), make_user(1, "Student"))
    assert not s.can_manage_booking(make_booking(2), make_user(1, "Student"))
    assert not s.can_view_all()


def test_teacher_views_all_but_manages_only_own():
    t = TeacherStrategy()
    assert t.can_view_all()
    assert t.can_manage_booking(make_booking(1), make_user(1, "Teacher"))
    assert not t.can_manage_booking(make_booking(2), make_user(1, "Teacher"))


def test_admin_views_and_manages_all():
    a = AdminStrategy()
    assert a.can_view_all()
    assert a.can_manage_booking(make_booking(2), make_user(1, "Admin"))


def test_time_limits_per_role():
    assert StudentStrategy().min_mins_before_change == 30
    assert TeacherStrategy().min_mins_before_change == 30
    assert AdminStrategy().min_mins_before_change == 0