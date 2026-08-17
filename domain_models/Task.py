from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass



def validate_non_negative_int(value, field_name):
    if value is not None:
        if not isinstance(value, int):
            raise TypeError(f"Value {field_name} must be integer, got {type(value).__name__}")

        if value < 0:
            raise ValueError(f"Value {field_name} must be non-negative, got {value}")


@dataclass
class TimeRecord:
    hours: Optional[int] = 0
    minutes: Optional[int] = 0

    def __post_init__(self):
        validate_non_negative_int(self.hours, 'hours')
        validate_non_negative_int(self.minutes, 'minutes')


    def __setattr__(self, name, value):
        if name in ('hours', 'minutes'):
            validate_non_negative_int(value, name)
        super().__setattr__(name, value)

    def __str__(self):
        return f"{self.hours or 0}h {self.minutes or 0}m"


class Task:
    def __init__(
            self,
            title: str,
            description: str,
            creator_id: str,
            executor_id: str,
            project_id: str,
            status: str,
            deadline: Optional[datetime] = None,
            estimated_hours: Optional[int] = 0,
            estimated_minutes: Optional[int] = 0,
            spent_hours: Optional[int] = 0,
            spent_minutes: Optional[int] = 0

    ):
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.executor_id = executor_id
        self.project_id = project_id
        self.status = status
        self.deadline = deadline
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
            deadline: Optional[datetime] = None,
            estimated_hours: Optional[int] = 0,
            estimated_minutes: Optional[int] = 0,
            spent_hours: Optional[int] = 0,
            spent_minutes: Optional[int] = 0
    ):

        if deadline is not None:
            now = datetime.now(tz=timezone.utc)

            if deadline <= now:
                raise ValueError(
                    f"Deadline must be in the future. Current time: {now}, deadline: {deadline}"
                )

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


if __name__ == "__main__":
    task = Task.create(
        title="Задача № 1",
        description="Описание к задаче № 1",
        creator_id="creator_id",
        executor_id="executor_id",
        project_id="project_id",
        status="NEW",
        deadline=datetime(year=2026, month=8, day=18, tzinfo=timezone.utc),
    )

