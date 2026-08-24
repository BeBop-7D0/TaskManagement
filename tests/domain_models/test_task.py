import copy
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta

import pytest
import pydantic

from domain_models.Task import TimeRecord, Deadline, Task

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
    task = Task.create(
        **REQUIRED_PARAMS,
        deadline=datetime.now(tz=timezone.utc) + timedelta(days=1)
    )
    assert isinstance(task, Task)
    assert task.id is not None


def test_task_creates_with_wrong_required_params():
    for param in REQUIRED_PARAMS:
        with pytest.raises(ValueError):
            target_params = copy.deepcopy(REQUIRED_PARAMS)
            target_params[param] = ""
            Task.create(**target_params)


def test_task_creates_with_wrong_spend_time():
    with pytest.raises(pydantic.ValidationError):
        Task.create(
            **REQUIRED_PARAMS,
            spent_hours=-1
        )

    with pytest.raises(pydantic.ValidationError):
        Task.create(
            **REQUIRED_PARAMS,
            spent_minutes=-1
        )

def test_task_creates_with_wrong_estimated_time():
    with pytest.raises(pydantic.ValidationError):
        Task.create(
            **REQUIRED_PARAMS,
             estimated_hours=-1
        )

    with pytest.raises(pydantic.ValidationError):
        Task.create(
            **REQUIRED_PARAMS,
             estimated_minutes=-1
        )

@pytest.fixture
def simple_task():
    return Task.create(**REQUIRED_PARAMS)


def test_task_change_title_correct_value(simple_task):
    simple_task.change_title("new title")
    assert simple_task.title == "new title"


def test_task_change_title_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.change_title("      ")


def test_task_change_description_correct_value(simple_task):
    simple_task.change_description("new description")
    assert simple_task.description == "new description"


def test_task_change_description_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.change_description("      ")


def test_task_change_executor_correct_value(simple_task):
    simple_task.change_executor("new executor")
    assert simple_task.executor_id == "new executor"


def test_task_change_executor_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.change_executor("      ")


def test_task_change_status_correct_value(simple_task):
    simple_task.change_status("new status")
    assert simple_task.status == "new status"


def test_task_change_status_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.change_status("      ")


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