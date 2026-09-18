
class OrganizationRepository:
    def is_active_employee(self, organization_id: str, employee_id: str) -> bool:
        if not employee_id.strip():
            return False

        if not organization_id.strip():
            return False

        # Логика запроса данных
        return True

    def has_project(self, organization_id: str, project_id: str) -> bool:
        if not project_id.strip():
            return False

        if not organization_id.strip():
            return False

        # Логика запроса данных
        return True