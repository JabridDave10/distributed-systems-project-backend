from pydantic import BaseModel

class AssignRoleDto(BaseModel):
    id_user: int
    id_role: int
