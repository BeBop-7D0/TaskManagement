import copy
from datetime import datetime, timezone, timedelta

import pytest
import pydantic

from domain.task.task import Task, TaskLifecycle
from domain.task.deadline import Deadline
from domain.task.time_record import TimeRecord


def test_time_record_creates_valid_value():
    tr = TimeRecord(hours=2, minutes=30)

    assert tr.hours == 2
    assert tr.minutes == 30


def test_time_record_normalizes_minutes():
    tr = TimeRecord(minutes=130)

    assert tr.hours == 2
    assert tr.minutes == 10


def test_time_record_cannot_have_negative_hours():
    with pytest.raises(pydantic.ValidationError):
        TimeRecord(hours=-2)


def test_time_record_cannot_have_negative_minutes():
    with pytest.raises(pydantic.ValidationError):
        TimeRecord(minutes=-30)


def test_time_record_add_valid():
    tr1 = TimeRecord(hours=1, minutes=30)
    tr2 = TimeRecord(hours=2, minutes=30)
    assert tr1 + tr2 == TimeRecord(hours=4)


def test_time_record_sub_valid():
    tr1 = TimeRecord(hours=2, minutes=40)
    tr2 = TimeRecord(hours=1, minutes=30)
    assert tr1 - tr2 == TimeRecord(hours=1, minutes=10)


def test_time_record_sub_result_cannot_be_negative():
    with pytest.raises(ValueError):
        TimeRecord(hours=1, minutes=30) - TimeRecord(hours=1, minutes=40)


def test_time_record_not_mutable():
    tr1 = TimeRecord(hours=2, minutes=40)
    tr2 = TimeRecord(hours=1, minutes=30)

    result_tr = tr1 + tr2

    assert tr1.hours == 2
    assert tr1.minutes == 40

    assert tr2.hours == 1
    assert tr2.minutes == 30

    assert result_tr.hours == 4
    assert result_tr.minutes == 10



def test_deadline_creates_valid_value():
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    dl = Deadline(deadline=dt)

    assert dl.deadline == dt


def test_deadline_cannot_be_in_past():
    dt = datetime.now(tz=timezone.utc) - timedelta(days=1)

    with pytest.raises(ValueError):
        Deadline(deadline=dt)


def test_deadline_cannot_create_without_utc_timezone():
    dt = datetime.now() + timedelta(days=1)
    with pytest.raises(ValueError):
        Deadline(deadline=dt)


REQUIRED_PARAMS = {
    "title": "Title of task",
    "description": "Do better",
    "creator_id": "Aboba the creator",
    "executor_id": "Aboba the executor",
    "project_id": "SomeProjectId",
    "status": "Backlog",
}


def test_task_creates_valid_value():
    task = Task.create(
        **REQUIRED_PARAMS
    )
    assert task.id is not None
    assert task.title == REQUIRED_PARAMS["title"]
    assert task.description == REQUIRED_PARAMS["description"]
    assert task.creator_id == REQUIRED_PARAMS["creator_id"]
    assert task.executor_id == REQUIRED_PARAMS["executor_id"]
    assert task.project_id == REQUIRED_PARAMS["project_id"]
    assert task.status == REQUIRED_PARAMS["status"]


def test_task_creates_with_correct_deadline_value():
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    task = Task.create(
        **REQUIRED_PARAMS,
        deadline=dt
    )

    assert task.id is not None
    assert task.deadline == Deadline(deadline=dt)


@pytest.mark.parametrize("param_name", REQUIRED_PARAMS)
def test_task_creates_with_wrong_required_params(param_name):
    with pytest.raises(ValueError):
        target_params = copy.deepcopy(REQUIRED_PARAMS)
        target_params[param_name] = ""
        Task.create(**target_params)


@pytest.mark.parametrize("kwarg_name, wrong_value", [("spent_hours", -1), ("spent_minutes", -30)])
def test_task_creates_with_wrong_spend_time(kwarg_name, wrong_value):
    target_params = {
        **REQUIRED_PARAMS,
        kwarg_name: wrong_value
    }
    with pytest.raises(pydantic.ValidationError):
        Task.create(
            **target_params
        )


@pytest.mark.parametrize("kwarg_name, wrong_value", [("estimated_hours", -2),("estimated_minutes", -30)])
def test_task_creates_with_wrong_estimated_time(kwarg_name, wrong_value):
    target_params = {
        **REQUIRED_PARAMS,
        kwarg_name: wrong_value
    }
    with pytest.raises(pydantic.ValidationError):
        Task.create(
            **target_params
        )


@pytest.fixture
def simple_task():
    return Task.create(**REQUIRED_PARAMS)


def test_task_change_title_correct_value(simple_task):
    simple_task.change_title("new title")
    assert simple_task.title == "new title"



def test_task_change_description_correct_value(simple_task):
    simple_task.change_description("new description")
    assert simple_task.description == "new description"


def test_task_change_executor_correct_value(simple_task):
    simple_task.change_executor("new executor")
    assert simple_task.executor_id == "new executor"


def test_task_change_status_correct_value(simple_task):
    simple_task.change_status("new status")
    assert simple_task.status == "new status"


@pytest.mark.parametrize(
    "method_name, wrong_value",
    [
        ("change_title", "   "),
        ("change_description", "   "),
        ("change_executor", "   "),
        ("change_status", "   ")
    ],
    ids=["title", "description", "executor", "status"]
)
def test_task_change_wrong_value(simple_task, method_name, wrong_value):
    method = getattr(simple_task, method_name)
    with pytest.raises(ValueError):
        method(wrong_value)


def test_task_set_deadline_correct_value(simple_task):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    simple_task.set_deadline(dt)

    assert simple_task.deadline == Deadline(deadline=dt)


def test_task_set_deadline_with_past_value(simple_task):
    dt = datetime.now(tz=timezone.utc) - timedelta(days=1)
    with pytest.raises(ValueError):
        simple_task.set_deadline(dt)


def test_task_set_estimated_time_correct_value(simple_task):
    simple_task.set_estimated_time(hours=12, minutes=30)

    assert simple_task.estimated_time == TimeRecord(hours=12, minutes=30)


def test_task_set_estimated_time_with_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.set_estimated_time(hours=1.2, minutes=30)


def test_task_add_spend_time_correct_value(simple_task):
    simple_task.add_spend_time(hours=1, minutes=30)
    simple_task.add_spend_time(hours=1, minutes=30)

    assert simple_task.spent_time == TimeRecord(hours=3, minutes=00)


def test_task_add_spend_time_with_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.add_spend_time(hours=-3, minutes=00)


def test_task_active_to_pause(simple_task):
    simple_task.pause()
    assert simple_task.lifecycle == TaskLifecycle.PAUSED


def test_task_active_to_close(simple_task):
    simple_task.close()
    assert simple_task.lifecycle == TaskLifecycle.CLOSED


def test_task_active_to_active(simple_task):
    with pytest.raises(Exception):
        simple_task.resume()


@pytest.mark.parametrize(
    "method_name, value",
    [
        ("change_title", "new_title"),
        ("change_description", "new_description"),
        ("change_executor", "new_executor_id"),
        ("change_status", "DONE"),
        ("add_spend_time", 1)
    ],
    ids=["title", "description", "executor", "status", "spend_time"]
)
def test_task_active_required_with_active(simple_task, method_name, value):
    method = getattr(simple_task, method_name)
    method(value)


def test_task_pause_to_active(simple_task):
    simple_task.pause()
    simple_task.resume()
    assert simple_task.lifecycle == TaskLifecycle.ACTIVE


def test_task_pause_to_close(simple_task):
    simple_task.pause()
    simple_task.close()
    assert simple_task.lifecycle == TaskLifecycle.CLOSED


def test_task_pause_to_pause(simple_task):
    simple_task.pause()
    with pytest.raises(Exception):
        simple_task.pause()


@pytest.mark.parametrize(
    "method_name, value",
    [
        ("change_title", "new_title"),
        ("change_description", "new_description"),
        ("change_executor", "new_executor_id"),
        ("change_status", "DONE"),
        ("add_spend_time", 1)
    ],
    ids=["title", "description", "executor", "status", "spend_time"]
)
def test_task_active_required_with_paused(simple_task, method_name, value):
    simple_task.pause()
    method = getattr(simple_task, method_name)
    with pytest.raises(Exception):
        method(value)


def test_task_close_to_active(simple_task):
    simple_task.close()
    with pytest.raises(Exception):
        simple_task.resume()


def test_task_close_to_pause(simple_task):
    simple_task.pause()
    with pytest.raises(Exception):
        simple_task.pause()


def test_task_close_to_close(simple_task):
    simple_task.close()
    with pytest.raises(Exception):
        simple_task.pause()


@pytest.mark.parametrize(
    "method_name, value",
    [
        ("change_title", "new_title"),
        ("change_description", "new_description"),
        ("change_executor", "new_executor_id"),
        ("change_status", "DONE"),
        ("add_spend_time", 1)
    ],
    ids=["title", "description", "executor", "status", "spend_time"]
)
def test_task_active_required_with_closed(simple_task, method_name, value):
    simple_task.close()
    method = getattr(simple_task, method_name)
    with pytest.raises(Exception):
        method(value)


def test_task_set_deadline_when_closed(simple_task):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    simple_task.close()
    simple_task.set_deadline(dt)

    assert simple_task.deadline == Deadline(deadline=dt)


def test_task_set_deadline_when_paused(simple_task):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    simple_task.pause()
    simple_task.set_deadline(dt)

    assert simple_task.deadline == Deadline(deadline=dt)


def test_task_set_estimated_time_when_closed(simple_task):
    simple_task.close()
    simple_task.set_estimated_time(hours=12, minutes=30)

    assert simple_task.estimated_time == TimeRecord(hours=12, minutes=30)


def test_task_set_estimated_time_when_paused(simple_task):
    simple_task.pause()
    simple_task.set_estimated_time(hours=12, minutes=30)

    assert simple_task.estimated_time == TimeRecord(hours=12, minutes=30)