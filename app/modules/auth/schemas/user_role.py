from pydantic import BaseModel
from typing import Optional

# Schema base para UserRole
class UserRoleBase(BaseModel):
    id_user: int
    id_role: int

# Schema para crear asignación usuario-rol (POST)
class UserRoleCreate(UserRoleBase):
    pass

# Schema para actualizar asignación usuario-rol (PUT/PATCH)
class UserRoleUpdate(BaseModel):
    id_user: Optional[int] = None
    id_role: Optional[int] = None

# Schema para respuesta de asignación usuario-rol (GET)
class UserRoleOut(UserRoleBase):
    id_user_role: int

    class Config:
        from_attributes = True
