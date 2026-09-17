import copy
from datetime import datetime, timezone, timedelta

import pytest
import pydantic

from domain.task.deadline import Deadline
from domain.task.history import HistoryAction, HistoryEntry, BaseActionData, ChangeDescriptionData
from domain.task.time_record import TimeRecord
from domain.task.task import Task, TaskLifecycle

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
    simple_task.change_title("new title", "actor_id")
    assert simple_task.title == "new title"



def test_task_change_description_correct_value(simple_task):
    simple_task.change_description("new description", "actor_id")
    assert simple_task.description == "new description"


def test_task_change_executor_correct_value(simple_task):
    simple_task.change_executor("new executor", "actor_id")
    assert simple_task.executor_id == "new executor"


def test_task_change_status_correct_value(simple_task):
    simple_task.change_status("new status", "actor_id")
    assert simple_task.status == "new status"


@pytest.mark.parametrize(
    "method_name, wrong_value",
    [
        ("change_title", ("   ", "actor_id")),
        ("change_description", ("   ", "actor_id")),
        ("change_executor", ("   ", "actor_id")),
        ("change_status", ("   ", "actor_id"))
    ],
    ids=["title", "description", "executor", "status"]
)
def test_task_change_wrong_value(simple_task, method_name, wrong_value):
    method = getattr(simple_task, method_name)
    with pytest.raises(ValueError):
        method(*wrong_value)


def test_task_set_deadline_correct_value(simple_task):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    simple_task.set_deadline(dt, "actor_id")

    assert simple_task.deadline == Deadline(deadline=dt)


def test_task_set_deadline_with_past_value(simple_task):
    dt = datetime.now(tz=timezone.utc) - timedelta(days=1)
    with pytest.raises(ValueError):
        simple_task.set_deadline(dt, "actor_id")


def test_task_set_estimated_time_correct_value(simple_task):
    simple_task.set_estimated_time("actor_id", hours=12, minutes=30)

    assert simple_task.estimated_time == TimeRecord(hours=12, minutes=30)


def test_task_set_estimated_time_with_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.set_estimated_time("actor_id", hours=1.2, minutes=30)


def test_task_add_spend_time_correct_value(simple_task):
    simple_task.add_spend_time("actor_id", hours=1, minutes=30)
    simple_task.add_spend_time("actor_id", hours=1, minutes=30)

    assert simple_task.spent_time == TimeRecord(hours=3, minutes=00)


def test_task_add_spend_time_with_wrong_value(simple_task):
    with pytest.raises(ValueError):
        simple_task.add_spend_time("actor_id", hours=-3, minutes=00)


def test_task_active_to_pause(simple_task):
    simple_task.pause("actor_id")
    assert simple_task.lifecycle == TaskLifecycle.PAUSED


def test_task_active_to_close(simple_task):
    simple_task.close("actor_id")
    assert simple_task.lifecycle == TaskLifecycle.CLOSED


def test_task_active_to_active(simple_task):
    with pytest.raises(Exception):
        simple_task.resume("actor_id")


@pytest.mark.parametrize(
    "method_name, value",
    [
        ("change_title", ("new_title", "actor_id")),
        ("change_description", ("new_description", "actor_id")),
        ("change_executor", ("new_executor_id", "actor_id")),
        ("change_status", ("DONE", "actor_id")),
        ("add_spend_time", ("actor_id", 1))
    ],
    ids=["title", "description", "executor", "status", "spend_time"]
)
def test_task_active_required_with_active(simple_task, method_name, value):
    method = getattr(simple_task, method_name)
    method(*value)


def test_task_pause_to_active(simple_task):
    simple_task.pause("actor_id")
    simple_task.resume("actor_id")
    assert simple_task.lifecycle == TaskLifecycle.ACTIVE


def test_task_pause_to_close(simple_task):
    simple_task.pause("actor_id")
    simple_task.close("actor_id")
    assert simple_task.lifecycle == TaskLifecycle.CLOSED


def test_task_pause_to_pause(simple_task):
    simple_task.pause("actor_id")
    with pytest.raises(Exception):
        simple_task.pause("actor_id")


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
    simple_task.pause("actor_id")
    method = getattr(simple_task, method_name)
    with pytest.raises(Exception):
        method(value, "actor_id")


def test_task_close_to_active(simple_task):
    simple_task.close("actor_id")
    with pytest.raises(Exception):
        simple_task.resume("actor_id")


def test_task_close_to_pause(simple_task):
    simple_task.pause("actor_id")
    with pytest.raises(Exception):
        simple_task.pause("actor_id")


def test_task_close_to_close(simple_task):
    simple_task.close("actor_id")
    with pytest.raises(Exception):
        simple_task.pause("actor_id")


@pytest.mark.parametrize(
    "method_name, value",
    [
        ("change_title", ("new_title", "actor_id")),
        ("change_description", ("new_description", "actor_id")),
        ("change_executor", ("new_executor_id", "actor_id")),
        ("change_status", ("DONE", "actor_id")),
        ("add_spend_time", ("actor_id", 1))
    ],
    ids=["title", "description", "executor", "status", "spend_time"]
)
def test_task_active_required_with_closed(simple_task, method_name, value):
    simple_task.close("actor_id")
    method = getattr(simple_task, method_name)
    with pytest.raises(Exception):
        method(*value)


def test_task_set_deadline_when_closed(simple_task):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    simple_task.close("actor_id")
    simple_task.set_deadline(dt, "actor_id")

    assert simple_task.deadline == Deadline(deadline=dt)


def test_task_set_deadline_when_paused(simple_task):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=1)
    simple_task.pause("actor_id")
    simple_task.set_deadline(dt, "actor_id")

    assert simple_task.deadline == Deadline(deadline=dt)


def test_task_set_estimated_time_when_closed(simple_task):
    simple_task.close("actor_id")
    simple_task.set_estimated_time("actor_id", hours=12, minutes=30)

    assert simple_task.estimated_time == TimeRecord(hours=12, minutes=30)


def test_task_set_estimated_time_when_paused(simple_task):
    simple_task.pause("actor_id")
    simple_task.set_estimated_time("actor_id", hours=12, minutes=30)

    assert simple_task.estimated_time == TimeRecord(hours=12, minutes=30)


def test_task_add_comment_with_correct_data(simple_task):
    comment_id = simple_task.add_comment(
        author_id="some_author_id",
        content="some content",
    )

    assert len(simple_task.comments) == 1

    comment = simple_task.comments[0]

    assert comment.comment_id == comment_id
    assert comment.author_id == "some_author_id"
    assert comment.content == "some content"



@pytest.mark.parametrize(
    "params_value",
    [("  ", "some content"),("some_author_id", "")],
    ids=["empty_author", "empty_content"]
)
def test_task_add_comment_with_wrong_data(simple_task, params_value):
    with pytest.raises(ValueError):
        simple_task.add_comment(*params_value)


def test_task_delete_exist_comment(simple_task):
    comment_id = simple_task.add_comment(
        author_id="some_author_id",
        content="some content"
    )
    simple_task.remove_comment(comment_id)
    target_comment = next((x.comment_id for x in simple_task.comments if x.comment_id == comment_id), None)

    assert target_comment is None


def test_task_delete_not_exist_comment(simple_task):
    simple_task.add_comment(
        author_id="some_author_id",
        content="some content"
    )
    with pytest.raises(KeyError):
        simple_task.remove_comment("non exist id")


def test_history_create_valid():
    history_entry = HistoryEntry(
        actor_id="123",
        action=HistoryAction.TASK_CREATE
    )
    assert history_entry.history_id is not None and isinstance(history_entry.history_id, str)
    assert isinstance(history_entry.data, BaseActionData)
    assert isinstance(history_entry.created_at, datetime)
    assert history_entry.created_at.tzinfo == timezone.utc


def test_history_different_id():
    history_entry_1 = HistoryEntry(
        actor_id="123",
        action=HistoryAction.TASK_CREATE
    )

    history_entry_2 = HistoryEntry(
        actor_id="123",
        action=HistoryAction.TASK_CREATE
    )
    assert history_entry_1.history_id != history_entry_2.history_id


def test_history_wrong_actor():
    with pytest.raises(ValueError):
        HistoryEntry(
            actor_id="    ",
            action=HistoryAction.TASK_CREATE
        )


def test_history_wrong_data_type():
    with pytest.raises(ValueError):
        HistoryEntry(
            actor_id="123",
            action=HistoryAction.CHANGE_TITLE
        )

    with pytest.raises(ValueError):
        HistoryEntry(
            actor_id="123",
            action=HistoryAction.CHANGE_TITLE,
            data=ChangeDescriptionData(
                old_description="some_desc",
                new_description="some_new_desc"
            )
        )


def test_task_cannot_change_history(simple_task):
    with pytest.raises(AttributeError):
        simple_task.history = [
            HistoryEntry(
                actor_id="123",
                action=HistoryAction.TASK_CREATE
            )
        ]


def test_task_create_history(simple_task):
    history = simple_task.history
    assert len(history) == 1
    entry_of_create = history[0]
    assert entry_of_create.action == HistoryAction.TASK_CREATE
    assert entry_of_create.actor_id == simple_task.creator_id


def test_task_change_title_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.change_title("new_title", actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.CHANGE_TITLE


def test_task_change_description_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.change_description("new_descr", actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.CHANGE_DESCRIPTION


def test_task_change_executor_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.change_executor("new_executor_id", actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.CHANGE_EXECUTOR


def test_task_change_status_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.change_status("DONE", actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.CHANGE_STATUS


def test_task_change_deadline_history_entry(simple_task):
    actor_id = "actor_1"
    dt = datetime.now(tz=timezone.utc) + timedelta(days=3)
    simple_task.set_deadline(dt, actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.CHANGE_DEADLINE
    assert target_entry.data.new_deadline == Deadline(deadline=dt)


def test_task_change_estimated_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.set_estimated_time(actor_id, hours=1)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.CHANGE_ESTIMATED_TIME
    assert target_entry.data.new_estimated == TimeRecord(hours=1)


def test_task_add_spent_time_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.add_spend_time(actor_id, hours=1)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.CHANGE_SPENT_TIME
    assert target_entry.data.old_spent == TimeRecord(hours=0, minutes=0)
    assert target_entry.data.new_spent== TimeRecord(hours=1, minutes=0)


def test_task_paused_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.pause(actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.TASK_PAUSE
    assert target_entry.data.old_lifecycle == TaskLifecycle.ACTIVE
    assert target_entry.data.new_lifecycle == TaskLifecycle.PAUSED


def test_task_close_history_entry(simple_task):
    actor_id = "actor_1"
    simple_task.close(actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == actor_id
    assert target_entry.action == HistoryAction.TASK_CLOSE
    assert target_entry.data.old_lifecycle == TaskLifecycle.ACTIVE
    assert target_entry.data.new_lifecycle == TaskLifecycle.CLOSED


def test_task_resume_history_entry(simple_task):
    pause_actor_id = "actor_1"
    simple_task.pause(pause_actor_id)

    resume_actor_id = "actor_2"
    simple_task.resume(resume_actor_id)

    target_entry = next((x for x in simple_task.history if x.actor_id == resume_actor_id), None)

    assert target_entry is not None
    assert target_entry.actor_id == resume_actor_id
    assert target_entry.action == HistoryAction.TASK_RESUME
    assert target_entry.data.old_lifecycle == TaskLifecycle.PAUSED
    assert target_entry.data.new_lifecycle == TaskLifecycle.ACTIVE