
class ProjectRepository:
    def has_member(self, project_id: str,  member_id: str):
        if not member_id.strip():
            return False

        if not project_id.strip():
            return False

        # Логика запроса данных
        return True