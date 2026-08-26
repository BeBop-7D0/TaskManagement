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

        total_minutes = (
                self.hours * 60
                + self.minutes
                + other.hours * 60
                + other.minutes
        )

        return TimeRecord(
            hours=total_minutes // 60,
            minutes=total_minutes % 60,
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
