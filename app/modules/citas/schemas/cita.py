from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# Base schema for appointments
class AppointmentBase(BaseModel):
    appointment_date: datetime
    reason: Optional[str] = None
    status: Optional[str] = None
    patient_id: int
    doctor_id: int

# For creating an appointment (POST)
class AppointmentCreate(AppointmentBase):
    pass

# For updating an appointment (PUT/PATCH)
class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None

# For returning an appointment in responses
class AppointmentOut(AppointmentBase):
    id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic V2: Allows automatic conversion from SQLAlchemy models

# Legacy schemas for backward compatibility (if needed temporarily)
class CitaBase(BaseModel):
    fecha_hora: datetime
    motivo: Optional[str] = None
    estado: Optional[str] = None
    id_paciente: int
    id_doctor: int

class CitaCreate(CitaBase):
    pass

class CitaOut(BaseModel):
    id_cita: int
    fecha_hora: datetime
    motivo: Optional[str] = None
    estado: Optional[str] = None
    id_paciente: int
    id_doctor: int

    class Config:
        from_attributes = True  # Pydantic V2: Updated from orm_mode
