from pydantic import BaseModel
from typing import Optional

# Schema base para Role
class RoleBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

# Schema para crear rol (POST)
class RoleCreate(RoleBase):
    pass

# Schema para actualizar rol (PUT/PATCH)
class RoleUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

# Schema para respuesta de rol (GET)
class RoleOut(RoleBase):
    id_role: int

    class Config:
        from_attributes = True
