from uuid import uuid4
from typing import Optional
from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator



class TimeRecord(BaseModel):
    hours: int = Field(default=0, ge=0, description="Hours (non-negative)")
    minutes: int = Field(default=0, ge=0, description="Minutes (non-negative)")

    @model_validator(mode='after')
    def normalize_time(self):
        self.hours += self.minutes // 60
        self.minutes = self.minutes % 60
        return self


    def __add__(self, other):
        if not isinstance(other, TimeRecord):
            raise TypeError("expected type: TimeRecord")

        self.minutes += other.minutes % 60
        self.hours += other.hours + other.minutes // 60

        return TimeRecord(
            hours=self.hours,
            minutes=self.minutes
        )

    def __sub__(self, other):
        if not isinstance(other, TimeRecord):
            raise TypeError("expected type: TimeRecord")


        target_total_minutes = self.minutes + self.hours * 60
        other_total_minutes = other.minutes + other.hours * 60

        target_total_minutes -= other_total_minutes

        if target_total_minutes < 0:
            raise ValueError("TimeRecord value cannot be negative")

        target_hours = target_total_minutes // 60
        target_minutes = target_total_minutes % 60
        return TimeRecord(
            hours=target_hours,
            minutes=target_minutes
        )


    def __str__(self):
        return f"{self.hours} h {self.minutes} m"


class Deadline(BaseModel):
    deadline: datetime = Field(..., description="deadline (not less than now)")

    @model_validator(mode='after')
    def check_datetime(self):
        tz_info = self.deadline
        if tz_info is None or tz_info != timezone.utc:
            raise ValueError("UTC time zone is required")

        now = datetime.now(tz=timezone.utc)
        if self.deadline <= now:
            raise ValueError(
                f"Deadline must be in the future. Current time: {now}, deadline: {self.deadline}"
            )

        return self

    def __str__(self):
        return f"{self.deadline.isoformat()}"


class Task:
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
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.executor_id = executor_id
        self.project_id = project_id
        self.status = status
        self.deadline = Deadline(deadline=deadline)
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

    def change_title(self, new_title: str):
        if not new_title.strip():
            raise ValueError("Title can not be empty string")

        self.title = new_title

    def change_description(self, new_description: str):
        if not new_description.strip():
            raise ValueError("Description can not be empty string")

        self.description = new_description

    def change_executor(self, new_executor_id: str):
        if not new_executor_id:
            raise ValueError("Executor_id value can not be empty string")
        self.executor_id = new_executor_id

    def change_status(self, new_status: str):
        if not new_status.strip():
            raise ValueError("Status of task can not be empty string")
        self.status = new_status

    def set_deadline(self, new_deadline: datetime):
        self.deadline = Deadline(deadline=new_deadline)

    def set_estimated_time(self, hours: int = 0, minutes: int = 0):
        self.estimated_time = TimeRecord(hours=hours, minutes=minutes)

    def add_spend_time(self, hours: int = 0, minutes: int = 0):
        self.spent_time += TimeRecord(hours=hours, minutes=minutes)


if __name__ == "__main__":
    task = Task.create(
        title="Задача № 1",
        description="Описание к задаче № 1",
        creator_id="creator_id",
        executor_id="executor_id",
        project_id="project_id",
        status="NEW",
        deadline=datetime(year=2026, month=8, day=30, tzinfo=timezone.utc)
    )

