from pydantic import BaseModel
from typing import Optional

class UpdateRoleDto(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
