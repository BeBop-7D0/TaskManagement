from domain.task.task import Task
from domain.task.deadline import Deadline

class TaskRepository:
    def get(self, task_id) -> Task:

        # Логика запроса данных

        task = Task(
            task_id="mock_task_id",
            title="mock_title",
            description="mock_descr",
            executor_id="mock_executor_id",
            creator_id="mock_creator_id",
            project_id="mock_project_id",
            status="mock_status",
            deadline=None,
            estimated_hours = 0,
            estimated_minutes = 0,
            spent_hours = 0,
            spent_minutes = 0,
            comments = [],
            history = []
        )
        return task

    def save(self, task: Task) -> str:
        # Логика сохранения задачи
        return "mock_task_id"
