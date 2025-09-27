from pydantic import BaseModel
from typing import Optional

class CreateRoleDto(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
