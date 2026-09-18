
class WorkflowRepository:
    def get_initial_status(self, organization_id) -> str:
        # Логика запроса
        return "NEW"