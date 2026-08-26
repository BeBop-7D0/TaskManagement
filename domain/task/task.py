from enum import Enum
from uuid import uuid4
from datetime import datetime
from functools import wraps

from domain.task.deadline import Deadline
from domain.task.time_record import TimeRecord


class TaskLifecycle(str, Enum):
    ACTIVE = 'active'
    PAUSED = "paused"
    CLOSED = "closed"




def check_active(funk):
    @wraps(funk)
    def wrapper(self, *args, **kwargs):
        if self.lifecycle != TaskLifecycle.ACTIVE:
            raise Exception("Task is not active")
        return funk(self, *args, **kwargs)
    return wrapper


class Task:

    LIFECYCLE_SWITCH_RULES = {
        TaskLifecycle.ACTIVE: {TaskLifecycle.CLOSED, TaskLifecycle.PAUSED},
        TaskLifecycle.PAUSED: {TaskLifecycle.ACTIVE, TaskLifecycle.CLOSED},
        TaskLifecycle.CLOSED: {}
    }

    def __init__(
            self,
            title: str,
            description: str,
            creator_id: str,
            executor_id: str,
            project_id: str,
            status: str,
            deadline: datetime = None,
            estimated_hours: int = 0,
            estimated_minutes: int = 0,
            spent_hours: int = 0,
            spent_minutes: int = 0

    ):
        self.id = str(uuid4())
        self.lifecycle = TaskLifecycle.ACTIVE
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.executor_id = executor_id
        self.project_id = project_id
        self.status = status
        self.deadline = Deadline(deadline=deadline) if deadline else None
        self.estimated_time = TimeRecord(hours=estimated_hours, minutes=estimated_minutes)
        self.spent_time = TimeRecord(hours=spent_hours, minutes=spent_minutes)


    @classmethod
    def create(
            cls,
            title: str,
            description: str,
            creator_id: str,
            executor_id: str,
            project_id: str,
            status: str,
            deadline: datetime = None,
            estimated_hours: int = 0,
            estimated_minutes: int = 0,
            spent_hours: int = 0,
            spent_minutes: int = 0
    ):

        if not title.strip():
            raise ValueError("Title can not be empty string")

        if not description.strip():
            raise ValueError("Description can not be empty string")

        if not creator_id.strip():
            raise ValueError("Creator_id value can not be empty string")

        if not executor_id.strip():
            raise ValueError("Executor_id value can not be empty string")

        if not status.strip():
            raise ValueError("Status of task can not be empty string")

        if not project_id.strip():
            raise ValueError("Project_id of task can not be empty string")

        return cls(
            title,
            description,
            creator_id,
            executor_id,
            project_id,
            status,
            deadline,
            estimated_hours,
            estimated_minutes,
            spent_hours,
            spent_minutes
        )

    @check_active
    def change_title(self, new_title: str):
        if not new_title.strip():
            raise ValueError("Title can not be empty string")

        self.title = new_title

    @check_active
    def change_description(self, new_description: str):
        if not new_description.strip():
            raise ValueError("Description can not be empty string")

        self.description = new_description

    @check_active
    def change_executor(self, new_executor_id: str):
        if not new_executor_id.strip():
            raise ValueError("Executor_id value can not be empty string")
        self.executor_id = new_executor_id

    @check_active
    def change_status(self, new_status: str):
        if not new_status.strip():
            raise ValueError("Status of task can not be empty string")
        self.status = new_status

    def set_deadline(self, new_deadline: datetime):
        self.deadline = Deadline(deadline=new_deadline)

    def set_estimated_time(self, hours: int = 0, minutes: int = 0):
        self.estimated_time = TimeRecord(hours=hours, minutes=minutes)


    @check_active
    def add_spend_time(self, hours: int = 0, minutes: int = 0):
        self.spent_time += TimeRecord(hours=hours, minutes=minutes)


    def pause(self):
        target_lifecycle = TaskLifecycle.PAUSED
        available_lifecycles = self.LIFECYCLE_SWITCH_RULES.get(self.lifecycle, {})

        if target_lifecycle not in available_lifecycles:
            raise Exception(f"Only switches are possible for {self.lifecycle.value}: {available_lifecycles}")

        self.lifecycle = target_lifecycle


    def close(self):
        target_lifecycle = TaskLifecycle.CLOSED
        available_lifecycles = self.LIFECYCLE_SWITCH_RULES.get(self.lifecycle, {})

        if target_lifecycle not in available_lifecycles:
            raise Exception(f"Only switches are possible for {self.lifecycle.value}: {available_lifecycles}")

        self.lifecycle = target_lifecycle


    def resume(self):
        target_lifecycle = TaskLifecycle.ACTIVE
        available_lifecycles = self.LIFECYCLE_SWITCH_RULES.get(self.lifecycle, {})

        if target_lifecycle not in available_lifecycles:
            raise Exception(f"Only switches are possible for {self.lifecycle.value}: {available_lifecycles}")
        self.lifecycle = target_lifecycle


if __name__ == "__main__":
    task = Task.create(
        title="Задача № 1",
        description="Описание к задаче № 1",
        creator_id="creator_id",
        executor_id="executor_id",
        project_id="project_id",
        status="NEW"
    )