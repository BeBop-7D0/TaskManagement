from uuid import uuid4
from functools import wraps
from datetime import datetime


from domain.task.comment import Comment
from domain.task.deadline import Deadline
from domain.task.time_record import TimeRecord
from domain.task.lifecycle import TaskLifecycle
from domain.task.history import (HistoryAction, HistoryEntry, ActionDataUnion, ChangeTitleData,
                                 ChangeDescriptionData, ChangeExecutorData, ChangeStatusData,
                                 ChangeDeadlineData, ChangeEstimatedTimeData, ChangeSpentTimeData, LifeCycleChangeData)




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
            spent_minutes: int = 0,
            comments: list[Comment] = None,
            history: list[HistoryEntry] = None,
            task_id: str = None

    ):
        self.id = task_id if task_id else str(uuid4())
        self._comments = comments if comments is not None else []
        self._history = history if history is not None else []
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
            spent_minutes,
            history=[
                HistoryEntry(
                    actor_id=creator_id,
                    action=HistoryAction.TASK_CREATE
                )
            ]
        )

    @check_active
    def change_title(self, new_title: str, actor_id: str):
        if not new_title.strip():
            raise ValueError("Title can not be empty string")

        old_title = self.title
        self.title = new_title

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.CHANGE_TITLE,
                data=ChangeTitleData(
                    old_title=old_title,
                    new_title=self.title
                )
            )
        )


    @check_active
    def change_description(self, new_description: str, actor_id: str):
        if not new_description.strip():
            raise ValueError("Description can not be empty string")

        old_description = self.description
        self.description = new_description

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.CHANGE_DESCRIPTION,
                data=ChangeDescriptionData(
                    old_description=old_description,
                    new_description=self.description
                )
            )
        )


    @check_active
    def change_executor(self, new_executor_id: str, actor_id: str):
        if not new_executor_id.strip():
            raise ValueError("Executor_id value can not be empty string")

        old_executor_id = self.executor_id
        self.executor_id = new_executor_id

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.CHANGE_EXECUTOR,
                data=ChangeExecutorData(
                    old_executor=old_executor_id,
                    new_executor=self.executor_id
                )
            )
        )

    @check_active
    def change_status(self, new_status: str, actor_id: str):
        if not new_status.strip():
            raise ValueError("Status of task can not be empty string")

        old_status = self.status
        self.status = new_status

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.CHANGE_STATUS,
                data=ChangeStatusData(
                    old_status=old_status,
                    new_status=self.status
                )
            )
        )

    def set_deadline(self, new_deadline: datetime, actor_id: str):
        old_deadline = self.deadline
        self.deadline = Deadline(deadline=new_deadline)

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.CHANGE_DEADLINE,
                data=ChangeDeadlineData(
                    old_deadline=old_deadline,
                    new_deadline=self.deadline
                )
            )
        )

    def set_estimated_time(self, actor_id: str, hours: int = 0, minutes: int = 0):
        old_estimated_time = self.estimated_time
        self.estimated_time = TimeRecord(hours=hours, minutes=minutes)

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.CHANGE_ESTIMATED_TIME,
                data=ChangeEstimatedTimeData(
                    old_estimated=old_estimated_time,
                    new_estimated=self.estimated_time
                )
            )
        )


    @check_active
    def add_spend_time(self, actor_id: str, hours: int = 0, minutes: int = 0):
        old_spent_time = self.spent_time
        self.spent_time += TimeRecord(hours=hours, minutes=minutes)

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.CHANGE_SPENT_TIME,
                data=ChangeSpentTimeData(
                    old_spent=old_spent_time,
                    new_spent=self.spent_time
                )
            )
        )


    def pause(self, actor_id: str):
        target_lifecycle = TaskLifecycle.PAUSED
        available_lifecycles = self.LIFECYCLE_SWITCH_RULES.get(self.lifecycle, {})

        if target_lifecycle not in available_lifecycles:
            raise Exception(f"Only switches are possible for {self.lifecycle.value}: {available_lifecycles}")

        old_lifecycle = self.lifecycle
        self.lifecycle = target_lifecycle

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.TASK_PAUSE,
                data=LifeCycleChangeData(
                    old_lifecycle=old_lifecycle,
                    new_lifecycle=self.lifecycle
                )
            )
        )



    def close(self, actor_id: str):
        target_lifecycle = TaskLifecycle.CLOSED
        available_lifecycles = self.LIFECYCLE_SWITCH_RULES.get(self.lifecycle, {})

        if target_lifecycle not in available_lifecycles:
            raise Exception(f"Only switches are possible for {self.lifecycle.value}: {available_lifecycles}")

        old_lifecycle = self.lifecycle
        self.lifecycle = target_lifecycle

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.TASK_CLOSE,
                data=LifeCycleChangeData(
                    old_lifecycle=old_lifecycle,
                    new_lifecycle=self.lifecycle
                )
            )
        )


    def resume(self, actor_id: str):
        target_lifecycle = TaskLifecycle.ACTIVE
        available_lifecycles = self.LIFECYCLE_SWITCH_RULES.get(self.lifecycle, {})

        if target_lifecycle not in available_lifecycles:
            raise Exception(f"Only switches are possible for {self.lifecycle.value}: {available_lifecycles}")

        old_lifecycle = self.lifecycle
        self.lifecycle = target_lifecycle

        self._history.append(
            HistoryEntry(
                actor_id=actor_id,
                action=HistoryAction.TASK_RESUME,
                data=LifeCycleChangeData(
                    old_lifecycle=old_lifecycle,
                    new_lifecycle=self.lifecycle
                )
            )
        )


    @property
    def comments(self) -> tuple[Comment]:
        return tuple(self._comments)


    def add_comment(self, author_id: str, content: str) -> str:
        comment = Comment(
            author_id=author_id,
            content=content
        )
        self._comments.append(comment)

        return comment.comment_id

    def remove_comment(self, comment_id: str):
        if not comment_id.strip():
            raise ValueError("Comment id can't be empty")

        remove_comment_id = next((i for i, c in enumerate(self._comments) if c.comment_id == comment_id), None)

        if remove_comment_id is None:
            raise KeyError("Comment with this comment id not found")

        removed = self._comments.pop(remove_comment_id)
        return removed

    @property
    def history(self) -> tuple[HistoryEntry]:
        return tuple(self._history)

    def _add_history(self, actor_id: str, action: HistoryAction, data: ActionDataUnion) -> str:
        history_entry = HistoryEntry(actor_id=actor_id, action=action, data=data)
        self._history.append(history_entry)
        return history_entry.history_id


if __name__ == "__main__":
    task = Task.create(
        title="Задача № 1",
        description="Описание к задаче № 1",
        creator_id="creator_id",
        executor_id="executor_id",
        project_id="project_id",
        status="NEW"
    )
