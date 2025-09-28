from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.modules.citas.services.cita_service import AppointmentService
from app.core.database import SessionLocal

router = APIRouter(prefix="/appointments", tags=["appointments"])
legacy_router = APIRouter(prefix="/citas", tags=["citas"])

class TodayAppointment(BaseModel):
    id: int
    patient_name: str
    appointment_date: str
    reason: str
    status: str
    duration: str

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/today", response_model=List[TodayAppointment])
def get_today_appointments(db: Session = Depends(get_db)):
    """
    Get today's appointments with patient details
    """
    try:
        print("🚀 ENDPOINT: /appointments/today - Getting today's appointments")
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_today_appointments_with_details()

        print(f"✅ ENDPOINT: Returning {len(appointments)} today's appointments")
        return appointments
    except Exception as e:
        print(f"❌ ENDPOINT: Error getting today's appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting today's appointments"
        )

@legacy_router.get("/today", response_model=List[TodayAppointment])
def get_today_appointments_legacy(db: Session = Depends(get_db)):
    """
    Legacy endpoint - Get today's appointments with patient details
    """
    try:
        print("🚀 ENDPOINT: /citas/today - Getting today's appointments (legacy)")
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_today_appointments_with_details()

        print(f"✅ ENDPOINT: Returning {len(appointments)} today's appointments (legacy)")
        return appointments
    except Exception as e:
        print(f"❌ ENDPOINT: Error getting today's appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting today's appointments"
        )