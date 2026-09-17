from enum import Enum
from uuid import uuid4
from typing import Union
from datetime import datetime, timezone, timedelta

from pydantic import BaseModel, Field, model_validator

from domain.task.deadline import Deadline
from domain.task.time_record import TimeRecord
from domain.task.lifecycle import TaskLifecycle


class HistoryAction(str, Enum):
    TASK_CREATE = "TASK_CREATE"
    CHANGE_TITLE = "CHANGE_TITLE"
    CHANGE_DESCRIPTION = "CHANGE_DESCRIPTION"
    CHANGE_STATUS = "CHANGE_STATUS"
    CHANGE_EXECUTOR = "CHANGE_EXECUTOR"
    CHANGE_DEADLINE = "CHANGE_DEADLINE"
    CHANGE_ESTIMATED_TIME = "CHANGE_ESTIMATED_TIME"
    CHANGE_SPENT_TIME = "CHANGE_SPENT_TIME"
    TASK_PAUSE = "TASK_PAUSE"
    TASK_RESUME = "TASK_RESUME"
    TASK_CLOSE = "TASK_CLOSE"



class BaseActionData(BaseModel):
    pass


class ChangeTitleData(BaseActionData):
    old_title: str
    new_title: str


class ChangeDescriptionData(BaseActionData):
    old_description: str
    new_description: str


class ChangeStatusData(BaseActionData):
    old_status: str
    new_status: str


class ChangeExecutorData(BaseActionData):
    old_executor: str
    new_executor: str


class ChangeDeadlineData(BaseActionData):
    old_deadline: Deadline | None = None
    new_deadline: Deadline | None = None


class ChangeEstimatedTimeData(BaseActionData):
    old_estimated: TimeRecord
    new_estimated: TimeRecord


class ChangeSpentTimeData(BaseActionData):
    old_spent: TimeRecord
    new_spent: TimeRecord


class LifeCycleChangeData(BaseActionData):
    old_lifecycle: TaskLifecycle
    new_lifecycle: TaskLifecycle



ActionDataUnion = Union[
    BaseActionData,
    ChangeTitleData,
    ChangeDescriptionData,
    ChangeStatusData,
    ChangeExecutorData,
    ChangeDeadlineData,
    ChangeEstimatedTimeData,
    ChangeSpentTimeData,
    LifeCycleChangeData,
]

ACTION_DATA_MAP: dict[HistoryAction, type[BaseActionData]] = {
    HistoryAction.TASK_CREATE: BaseActionData,
    HistoryAction.CHANGE_TITLE: ChangeTitleData,
    HistoryAction.CHANGE_DESCRIPTION: ChangeDescriptionData,
    HistoryAction.CHANGE_STATUS: ChangeStatusData,
    HistoryAction.CHANGE_EXECUTOR: ChangeExecutorData,
    HistoryAction.CHANGE_DEADLINE: ChangeDeadlineData,
    HistoryAction.CHANGE_ESTIMATED_TIME: ChangeEstimatedTimeData,
    HistoryAction.CHANGE_SPENT_TIME: ChangeSpentTimeData,
    HistoryAction.TASK_PAUSE: LifeCycleChangeData,
    HistoryAction.TASK_RESUME: LifeCycleChangeData,
    HistoryAction.TASK_CLOSE: LifeCycleChangeData,
}


class HistoryEntry(BaseModel):
    history_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Идентификатор записи в истории"
    )
    actor_id: str = Field(..., description="Идентификатор инициатора действия")
    action: HistoryAction = Field(..., description="Тип действия, выполненного над задачей")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="Дата создания записи в истории"
    )
    data: ActionDataUnion  = Field(default_factory=BaseActionData,
                                   description="Информация по действию, выполненному над задачей")


    @model_validator(mode="after")
    def check_non_empty_actor(self):
        if not self.actor_id.strip():
            raise ValueError("Actor id cannot be empty")

        return self

    @model_validator(mode="after")
    def check_data_scheme(self):
        required_type = ACTION_DATA_MAP.get(self.action)
        actual_type = type(self.data)

        if required_type != actual_type:
            raise ValueError(f"Data type must be {required_type.__name__}. Got {actual_type.__name__}")

        return self

