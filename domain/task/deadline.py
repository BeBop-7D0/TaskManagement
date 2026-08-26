from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator

class Deadline(BaseModel):
    deadline: datetime = Field(..., description="deadline (not less than now)")

    @model_validator(mode='after')
    def check_datetime(self):
        tz_info = self.deadline.tzinfo
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
