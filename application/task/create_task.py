import datetime

from domain.task.task import Task
from repository.task import TaskRepository
from repository.project import ProjectRepository
from repository.workflow import WorkflowRepository
from repository.organization import OrganizationRepository

class CreateTaskUseCase:
    def __init__(
            self,
            task_repository: TaskRepository,
            workflow_repository: WorkflowRepository,
            project_repository: ProjectRepository,
            organization_repository: OrganizationRepository
    ):
        self.task_repository = task_repository
        self.workflow_repository = workflow_repository
        self.project_repository = project_repository
        self.organization_repository = organization_repository

    # TODO: Обработка ошибок, возвращение результата
    def execute(
            self,
            title: str,
            description: str,
            creator_id: str,
            executor_id: str,
            project_id: str,
            organization_id: str,
            deadline: datetime = None,
            estimated_hours: int = 0,
            estimated_minutes: int = 0,
    ):

        if not self.organization_repository.is_active_employee(organization_id, creator_id):
            raise Exception("Постановщик не найден в организации")

        if not self.organization_repository.is_active_employee(organization_id, executor_id):
            raise Exception("Исполнитель не найден в организации")

        if not self.organization_repository.has_project(organization_id, project_id):
            raise Exception("Проект не найден в организации")

        if not self.project_repository.has_member(project_id, creator_id):
            raise Exception("Постановщик не имеет доступа к проекту")

        if not self.project_repository.has_member(project_id, executor_id):
            raise Exception("Исполнитель не имеет доступа к проекту")

        initial_status = self.workflow_repository.get_initial_status(organization_id)

        task = Task.create(
            title,
            description,
            creator_id,
            executor_id,
            project_id,
            initial_status,
            deadline,
            estimated_hours,
            estimated_minutes
        )

        task_id = self.task_repository.save(task)

        return task_id


if __name__ == "__main__":

    org_repo = OrganizationRepository()
    proj_repo = ProjectRepository()
    workflow_repo = WorkflowRepository()
    task_repo = TaskRepository()

    use_case = CreateTaskUseCase(
        organization_repository=org_repo,
        project_repository=proj_repo,
        task_repository=task_repo,
        workflow_repository=workflow_repo
    )

    task_id = use_case.execute(
        title="new_task",
        executor_id="executor_id",
        creator_id="creator_id",
        organization_id="organization_id",
        project_id = "project_id",
        description="some desc"
    )

    print(task_id)