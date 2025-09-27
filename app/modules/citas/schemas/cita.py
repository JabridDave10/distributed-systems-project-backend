from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# Para crear/actualizar citas (entrada)
class CitaBase(BaseModel):
    fecha_hora: datetime
    motivo: Optional[str] = None
    estado: Optional[str] = None
    id_paciente: int
    id_doctor: int

# Para crear una cita (POST)
class CitaCreate(CitaBase):
    pass

# Para actualizar una cita (PUT/PATCH)
class CitaUpdate(BaseModel):
    fecha_hora: Optional[datetime] = None
    motivo: Optional[str] = None
    estado: Optional[str] = None
    id_paciente: Optional[int] = None
    id_doctor: Optional[int] = None

# Para devolver una cita en responses
class CitaOut(CitaBase):
    id_cita: int

    class Config:
        orm_mode = True  # <- Permite convertir modelos SQLAlchemy en Pydantic automáticamente
