from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.modules.citas.schemas.cita import AppointmentOut, AppointmentCreate, AppointmentUpdate, CitaOut, CitaCreate
from app.modules.citas.services.cita_service import AppointmentService
from app.core.database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="/appointments", tags=["appointments"])
# Legacy router for backward compatibility
legacy_router = APIRouter(prefix="/citas", tags=["citas"])

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[AppointmentOut])
def get_appointments(db: Session = Depends(get_db)):
    """
    Get all appointments from database
    """
    try:
        print("🚀 ENDPOINT: /appointments/ - Getting all appointments")
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_all_appointments()

        print(f"✅ ENDPOINT: Returning {len(appointments)} appointments")
        return appointments
    except Exception as e:
        print(f"❌ ENDPOINT: Error getting appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@legacy_router.get("/", response_model=List[CitaOut])
def get_citas_legacy(db: Session = Depends(get_db)):
    """
    Legacy endpoint - Get all appointments (citas) from database
    """
    try:
        print("🚀 ENDPOINT: /citas/ - Getting all appointments (legacy)")
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_all_appointments()

        # Convert to legacy format
        result = []
        for appointment in appointments:
            result.append(CitaOut(
                id_cita=appointment.id,
                fecha_hora=appointment.appointment_date,
                motivo=appointment.reason,
                estado=appointment.status,
                id_paciente=appointment.patient_id,
                id_doctor=appointment.doctor_id
            ))

        print(f"✅ ENDPOINT: Returning {len(result)} appointments (legacy)")
        return result
    except Exception as e:
        print(f"❌ ENDPOINT: Error getting appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{cita_id}", response_model=CitaOut)
def get_cita(cita_id: int, db: Session = Depends(get_db)):
    """
    Obtener una cita específica por ID desde la base de datos
    """
    try:
        print(f"🚀 ENDPOINT: /citas/{cita_id} - Obteniendo cita específica")
        cita_service = CitaService(db)
        cita = cita_service.get_cita_by_id(cita_id)

        if not cita:
            print(f"❌ ENDPOINT: Cita {cita_id} no encontrada")
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        result = CitaOut(
            id_cita=cita.id_cita,
            fecha_hora=cita.fecha_hora,
            motivo=cita.motivo,
            estado=cita.estado,
            id_paciente=cita.id_paciente,
            id_doctor=cita.id_doctor
        )

        print(f"✅ ENDPOINT: Cita encontrada")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error obteniendo cita: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/", response_model=AppointmentOut)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Create a new appointment in the database
    """
    try:
        print("🚀 ENDPOINT: POST /appointments/ - Creating new appointment")
        print(f"📋 Data received: {appointment.dict()}")

        appointment_service = AppointmentService(db)
        new_appointment = appointment_service.create_appointment(appointment)

        print(f"✅ ENDPOINT: Appointment created successfully with ID {new_appointment.id}")
        return new_appointment
    except ValueError as e:
        print(f"❌ ENDPOINT: Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ ENDPOINT: Error creating appointment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@legacy_router.post("/", response_model=CitaOut)
def create_cita_legacy(cita: CitaCreate, db: Session = Depends(get_db)):
    """
    Legacy endpoint - Create a new appointment (cita) in the database
    """
    try:
        print("🚀 ENDPOINT: POST /citas/ - Creating new appointment (legacy)")
        print(f"📋 Data received: {cita.dict()}")

        # Convert legacy format to new format
        appointment_data = AppointmentCreate(
            appointment_date=cita.fecha_hora,
            reason=cita.motivo,
            status=cita.estado,
            patient_id=cita.id_paciente,
            doctor_id=cita.id_doctor
        )

        appointment_service = AppointmentService(db)
        new_appointment = appointment_service.create_appointment(appointment_data)

        # Convert back to legacy format
        result = CitaOut(
            id_cita=new_appointment.id,
            fecha_hora=new_appointment.appointment_date,
            motivo=new_appointment.reason,
            estado=new_appointment.status,
            id_paciente=new_appointment.patient_id,
            id_doctor=new_appointment.doctor_id
        )

        print(f"✅ ENDPOINT: Appointment created successfully with ID {new_appointment.id} (legacy)")
        return result
    except ValueError as e:
        print(f"❌ ENDPOINT: Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ ENDPOINT: Error creating appointment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentOut])
def get_appointments_by_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """
    Get all appointments for a specific doctor
    """
    try:
        print(f"🚀 ENDPOINT: /appointments/doctor/{doctor_id} - Getting doctor's appointments")
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_appointments_by_doctor(doctor_id)

        print(f"✅ ENDPOINT: Returning {len(appointments)} doctor's appointments")
        return appointments
    except Exception as e:
        print(f"❌ ENDPOINT: Error getting doctor's appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@legacy_router.get("/doctor/{doctor_id}", response_model=List[CitaOut])
def get_citas_by_doctor_legacy(doctor_id: int, db: Session = Depends(get_db)):
    """
    Legacy endpoint - Get all appointments for a specific doctor
    """
    try:
        print(f"🚀 ENDPOINT: /citas/doctor/{doctor_id} - Getting doctor's appointments (legacy)")
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_appointments_by_doctor(doctor_id)

        # Convert to legacy format
        result = []
        for appointment in appointments:
            result.append(CitaOut(
                id_cita=appointment.id,
                fecha_hora=appointment.appointment_date,
                motivo=appointment.reason,
                estado=appointment.status,
                id_paciente=appointment.patient_id,
                id_doctor=appointment.doctor_id
            ))

        print(f"✅ ENDPOINT: Returning {len(result)} doctor's appointments (legacy)")
        return result
    except Exception as e:
        print(f"❌ ENDPOINT: Error getting doctor's appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/paciente/{paciente_id}", response_model=List[CitaOut])
def get_citas_by_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """
    Obtener todas las citas de un paciente específico
    """
    try:
        print(f"🚀 ENDPOINT: /citas/paciente/{paciente_id} - Obteniendo citas del paciente")
        cita_service = CitaService(db)
        citas = cita_service.get_citas_by_paciente(paciente_id)

        # Convertir a formato de salida
        result = []
        for cita in citas:
            result.append(CitaOut(
                id_cita=cita.id_cita,
                fecha_hora=cita.fecha_hora,
                motivo=cita.motivo,
                estado=cita.estado,
                id_paciente=cita.id_paciente,
                id_doctor=cita.id_doctor
            ))

        print(f"✅ ENDPOINT: Retornando {len(result)} citas del paciente")
        return result
    except Exception as e:
        print(f"❌ ENDPOINT: Error obteniendo citas del paciente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/test/connection")
def test_connection():
    """
    Endpoint específico para probar la conexión desde el frontend.
    Retorna información básica del servidor.
    """
    return {
        "message": "¡Conexión exitosa! 🎉",
        "server_time": datetime.now().isoformat(),
        "endpoints_available": [
            "GET /health/",
            "GET /health/ping", 
            "GET /citas/",
            "GET /citas/{id}",
            "POST /citas/",
            "GET /citas/test/connection"
        ],
        "status": "ready"
    }

