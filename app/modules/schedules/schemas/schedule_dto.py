from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time, datetime

class DoctorScheduleBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="Día de la semana (0=domingo, 1=lunes, ..., 6=sábado)")
    start_time: time = Field(..., description="Hora de inicio")
    end_time: time = Field(..., description="Hora de fin")
    is_active: bool = Field(True, description="Si el horario está activo")

class DoctorScheduleCreate(DoctorScheduleBase):
    pass

class DoctorScheduleUpdate(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None

class DoctorScheduleOut(DoctorScheduleBase):
    id: int
    doctor_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WeeklyScheduleCreate(BaseModel):
    schedules: List[DoctorScheduleCreate] = Field(..., description="Lista de horarios para la semana")

class WeeklyScheduleOut(BaseModel):
    doctor_id: int
    schedules: List[DoctorScheduleOut]

class DoctorSettingsBase(BaseModel):
    appointment_duration: int = Field(30, gt=0, description="Duración de cada cita en minutos")
    break_between_appointments: int = Field(5, ge=0, description="Tiempo entre citas en minutos")
    advance_booking_days: int = Field(30, gt=0, description="Días máximos para agendar con anticipación")
    allow_weekend_appointments: bool = Field(False, description="Permitir citas en fines de semana")

class DoctorSettingsCreate(DoctorSettingsBase):
    pass

class DoctorSettingsUpdate(BaseModel):
    appointment_duration: Optional[int] = Field(None, gt=0)
    break_between_appointments: Optional[int] = Field(None, ge=0)
    advance_booking_days: Optional[int] = Field(None, gt=0)
    allow_weekend_appointments: Optional[bool] = None

class DoctorSettingsOut(DoctorSettingsBase):
    id: int
    doctor_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True