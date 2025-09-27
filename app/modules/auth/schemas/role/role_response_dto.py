from pydantic import BaseModel
from typing import Optional

class RoleResponseDto(BaseModel):
    id_role: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True
