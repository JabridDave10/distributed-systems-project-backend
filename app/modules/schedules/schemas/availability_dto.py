from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum

class ExceptionType(str, Enum):
    BLOCKED = "blocked"
    CUSTOM_HOURS = "custom_hours"

class AvailabilityExceptionBase(BaseModel):
    exception_date: date = Field(..., description="Fecha de la excepción")
    start_time: Optional[time] = Field(None, description="Hora de inicio (null para día completo)")
    end_time: Optional[time] = Field(None, description="Hora de fin (null para día completo)")
    exception_type: ExceptionType = Field(..., description="Tipo de excepción")
    reason: Optional[str] = Field(None, description="Razón de la excepción")

class AvailabilityExceptionCreate(AvailabilityExceptionBase):
    pass

class AvailabilityExceptionUpdate(BaseModel):
    exception_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    exception_type: Optional[ExceptionType] = None
    reason: Optional[str] = None

class AvailabilityExceptionOut(AvailabilityExceptionBase):
    id: int
    doctor_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TimeSlot(BaseModel):
    start_time: time
    end_time: time
    is_available: bool = True

class DayAvailability(BaseModel):
    date: date
    day_of_week: int
    slots: List[TimeSlot]
    is_working_day: bool = True

class AvailabilityQuery(BaseModel):
    doctor_id: int
    start_date: date
    end_date: Optional[date] = None  # Si es None, solo consulta start_date

class AvailabilityResponse(BaseModel):
    doctor_id: int
    availability: List[DayAvailability]

class AvailableSlotsQuery(BaseModel):
    doctor_id: int
    date: date

class AvailableSlotsResponse(BaseModel):
    doctor_id: int
    date: date
    available_slots: List[TimeSlot]