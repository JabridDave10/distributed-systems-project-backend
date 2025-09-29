from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.core.dependencies import get_db, verify_jwt_auth
from app.modules.schedules.services.schedule_service import ScheduleService
from app.modules.schedules.schemas.schedule_dto import (
    DoctorScheduleCreate, DoctorScheduleOut, DoctorScheduleUpdate,
    WeeklyScheduleCreate, WeeklyScheduleOut,
    DoctorSettingsCreate, DoctorSettingsOut, DoctorSettingsUpdate
)
from app.modules.schedules.schemas.availability_dto import (
    AvailabilityExceptionCreate, AvailabilityExceptionOut,
    AvailableSlotsResponse
)

router = APIRouter(prefix="/schedules", tags=["schedules"])

# ============ DOCTOR SCHEDULES ============

@router.post("/doctor/{doctor_id}", response_model=List[DoctorScheduleOut])
def create_weekly_schedule(
    doctor_id: int,
    weekly_schedule: WeeklyScheduleCreate,
    db: Session = Depends(get_db)
):
    """
    Crear horario semanal para un doctor
    """
    try:
        print(f"🚀 ENDPOINT: POST /schedules/doctor/{doctor_id} - Creating weekly schedule")

        # Autenticación temporalmente removida para testing

        schedule_service = ScheduleService(db)
        schedules = schedule_service.create_weekly_schedule(doctor_id, weekly_schedule.schedules)

        print(f"✅ ENDPOINT: Created {len(schedules)} schedules for doctor {doctor_id}")
        return schedules

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error creating weekly schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/doctor/{doctor_id}", response_model=WeeklyScheduleOut)
def get_doctor_schedule(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener horario semanal de un doctor
    """
    try:
        print(f"🚀 ENDPOINT: GET /schedules/doctor/{doctor_id} - Getting doctor schedule")

        schedule_service = ScheduleService(db)
        schedules = schedule_service.get_doctor_schedules(doctor_id)

        return WeeklyScheduleOut(
            doctor_id=doctor_id,
            schedules=schedules
        )

    except Exception as e:
        print(f"❌ ENDPOINT: Error getting doctor schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/schedule/{schedule_id}", response_model=DoctorScheduleOut)
def update_schedule(
    schedule_id: int,
    schedule_update: DoctorScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_auth)
):
    """
    Actualizar un horario específico
    """
    try:
        print(f"🚀 ENDPOINT: PUT /schedules/schedule/{schedule_id} - Updating schedule")

        schedule_service = ScheduleService(db)
        updated_schedule = schedule_service.update_doctor_schedule(schedule_id, schedule_update)

        if not updated_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Horario no encontrado"
            )

        # Verificar permisos
        if current_user.get("id_role") != 3 and current_user.get("id_user") != updated_schedule.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar este horario"
            )

        print(f"✅ ENDPOINT: Updated schedule {schedule_id}")
        return updated_schedule

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error updating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/schedule/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_auth)
):
    """
    Eliminar un horario específico
    """
    try:
        print(f"🚀 ENDPOINT: DELETE /schedules/schedule/{schedule_id} - Deleting schedule")

        schedule_service = ScheduleService(db)
        success = schedule_service.delete_doctor_schedule(schedule_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Horario no encontrado"
            )

        print(f"✅ ENDPOINT: Deleted schedule {schedule_id}")
        return {"message": "Horario eliminado exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error deleting schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# ============ DOCTOR SETTINGS ============

@router.get("/doctor/{doctor_id}/settings", response_model=DoctorSettingsOut)
def get_doctor_settings(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener configuración de un doctor
    """
    try:
        print(f"🚀 ENDPOINT: GET /schedules/doctor/{doctor_id}/settings - Getting doctor settings")

        schedule_service = ScheduleService(db)
        settings = schedule_service.get_or_create_doctor_settings(doctor_id)

        print(f"✅ ENDPOINT: Retrieved settings for doctor {doctor_id}")
        return settings

    except Exception as e:
        print(f"❌ ENDPOINT: Error getting doctor settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/doctor/{doctor_id}/settings", response_model=DoctorSettingsOut)
def update_doctor_settings(
    doctor_id: int,
    settings_update: DoctorSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_auth)
):
    """
    Actualizar configuración de un doctor
    """
    try:
        print(f"🚀 ENDPOINT: PUT /schedules/doctor/{doctor_id}/settings - Updating doctor settings")

        # Verificar permisos
        if current_user.get("id_role") != 3 and current_user.get("id_user") != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar la configuración de este doctor"
            )

        schedule_service = ScheduleService(db)
        updated_settings = schedule_service.update_doctor_settings(doctor_id, settings_update)

        if not updated_settings:
            # Crear configuración si no existe
            default_settings = DoctorSettingsCreate(**settings_update.dict(exclude_unset=True))
            updated_settings = schedule_service.create_doctor_settings(doctor_id, default_settings)

        print(f"✅ ENDPOINT: Updated settings for doctor {doctor_id}")
        return updated_settings

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error updating doctor settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# ============ AVAILABILITY EXCEPTIONS ============

@router.post("/doctor/{doctor_id}/exceptions", response_model=AvailabilityExceptionOut)
def create_availability_exception(
    doctor_id: int,
    exception: AvailabilityExceptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_auth)
):
    """
    Crear una excepción de disponibilidad (bloqueo o horario personalizado)
    """
    try:
        print(f"🚀 ENDPOINT: POST /schedules/doctor/{doctor_id}/exceptions - Creating availability exception")

        # Verificar permisos
        if current_user.get("id_role") != 3 and current_user.get("id_user") != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para crear excepciones para este doctor"
            )

        schedule_service = ScheduleService(db)
        new_exception = schedule_service.create_availability_exception(doctor_id, exception)

        print(f"✅ ENDPOINT: Created exception for doctor {doctor_id} on {exception.exception_date}")
        return new_exception

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error creating availability exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/doctor/{doctor_id}/exceptions", response_model=List[AvailabilityExceptionOut])
def get_doctor_exceptions(
    doctor_id: int,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """
    Obtener excepciones de disponibilidad de un doctor
    """
    try:
        print(f"🚀 ENDPOINT: GET /schedules/doctor/{doctor_id}/exceptions - Getting doctor exceptions")

        schedule_service = ScheduleService(db)
        exceptions = schedule_service.get_doctor_exceptions(doctor_id, start_date, end_date)

        print(f"✅ ENDPOINT: Retrieved {len(exceptions)} exceptions for doctor {doctor_id}")
        return exceptions

    except Exception as e:
        print(f"❌ ENDPOINT: Error getting doctor exceptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/exceptions/{exception_id}")
def delete_availability_exception(
    exception_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_auth)
):
    """
    Eliminar una excepción de disponibilidad
    """
    try:
        print(f"🚀 ENDPOINT: DELETE /schedules/exceptions/{exception_id} - Deleting availability exception")

        schedule_service = ScheduleService(db)
        success = schedule_service.delete_availability_exception(exception_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Excepción no encontrada"
            )

        print(f"✅ ENDPOINT: Deleted exception {exception_id}")
        return {"message": "Excepción eliminada exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error deleting availability exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# ============ AVAILABILITY QUERIES ============

@router.get("/doctor/{doctor_id}/availability", response_model=AvailableSlotsResponse)
def get_available_slots(
    doctor_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    """
    Obtener slots disponibles para un doctor en una fecha específica
    """
    try:
        print(f"🚀 ENDPOINT: GET /schedules/doctor/{doctor_id}/availability?date={date} - Getting available slots")

        schedule_service = ScheduleService(db)
        availability = schedule_service.get_available_slots(doctor_id, date)

        print(f"✅ ENDPOINT: Retrieved {len(availability.available_slots)} available slots for doctor {doctor_id} on {date}")
        return availability

    except Exception as e:
        print(f"❌ ENDPOINT: Error getting available slots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )