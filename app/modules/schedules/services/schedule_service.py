from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime, time, timedelta

from app.modules.schedules.models.doctor_schedule import DoctorSchedule
from app.modules.schedules.models.doctor_settings import DoctorSettings
from app.modules.schedules.models.doctor_availability_exception import DoctorAvailabilityException, ExceptionType
from app.modules.citas.models.cita import Appointment
from app.modules.schedules.schemas.schedule_dto import (
    DoctorScheduleCreate, DoctorScheduleUpdate, DoctorSettingsCreate, DoctorSettingsUpdate
)
from app.modules.schedules.schemas.availability_dto import (
    AvailabilityExceptionCreate, TimeSlot, DayAvailability, AvailableSlotsResponse
)

class ScheduleService:
    def __init__(self, db: Session):
        self.db = db

    # ============ DOCTOR SCHEDULES ============

    def create_doctor_schedule(self, doctor_id: int, schedule: DoctorScheduleCreate) -> DoctorSchedule:
        """Crear un horario para un doctor"""
        db_schedule = DoctorSchedule(
            doctor_id=doctor_id,
            **schedule.dict()
        )
        self.db.add(db_schedule)
        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule

    def create_weekly_schedule(self, doctor_id: int, schedules: List[DoctorScheduleCreate]) -> List[DoctorSchedule]:
        """Crear horarios para toda la semana"""
        # Primero eliminar horarios existentes para evitar duplicados
        self.db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor_id).delete()

        db_schedules = []
        for schedule in schedules:
            db_schedule = DoctorSchedule(
                doctor_id=doctor_id,
                **schedule.dict()
            )
            self.db.add(db_schedule)
            db_schedules.append(db_schedule)

        self.db.commit()
        for schedule in db_schedules:
            self.db.refresh(schedule)
        return db_schedules

    def get_doctor_schedules(self, doctor_id: int) -> List[DoctorSchedule]:
        """Obtener todos los horarios de un doctor"""
        return self.db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.is_active == True
        ).order_by(DoctorSchedule.day_of_week).all()

    def update_doctor_schedule(self, schedule_id: int, schedule_update: DoctorScheduleUpdate) -> Optional[DoctorSchedule]:
        """Actualizar un horario específico"""
        db_schedule = self.db.query(DoctorSchedule).filter(DoctorSchedule.id == schedule_id).first()
        if not db_schedule:
            return None

        update_data = schedule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_schedule, field, value)

        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule

    def delete_doctor_schedule(self, schedule_id: int) -> bool:
        """Eliminar un horario específico"""
        db_schedule = self.db.query(DoctorSchedule).filter(DoctorSchedule.id == schedule_id).first()
        if not db_schedule:
            return False

        self.db.delete(db_schedule)
        self.db.commit()
        return True

    # ============ DOCTOR SETTINGS ============

    def create_doctor_settings(self, doctor_id: int, settings: DoctorSettingsCreate) -> DoctorSettings:
        """Crear configuración para un doctor"""
        db_settings = DoctorSettings(
            doctor_id=doctor_id,
            **settings.dict()
        )
        self.db.add(db_settings)
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings

    def get_doctor_settings(self, doctor_id: int) -> Optional[DoctorSettings]:
        """Obtener configuración de un doctor"""
        return self.db.query(DoctorSettings).filter(DoctorSettings.doctor_id == doctor_id).first()

    def get_or_create_doctor_settings(self, doctor_id: int) -> DoctorSettings:
        """Obtener configuración o crear una por defecto"""
        settings = self.get_doctor_settings(doctor_id)
        if not settings:
            default_settings = DoctorSettingsCreate()
            settings = self.create_doctor_settings(doctor_id, default_settings)
        return settings

    def update_doctor_settings(self, doctor_id: int, settings_update: DoctorSettingsUpdate) -> Optional[DoctorSettings]:
        """Actualizar configuración de un doctor"""
        db_settings = self.get_doctor_settings(doctor_id)
        if not db_settings:
            return None

        update_data = settings_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_settings, field, value)

        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings

    # ============ AVAILABILITY EXCEPTIONS ============

    def create_availability_exception(self, doctor_id: int, exception: AvailabilityExceptionCreate) -> DoctorAvailabilityException:
        """Crear una excepción de disponibilidad"""
        db_exception = DoctorAvailabilityException(
            doctor_id=doctor_id,
            **exception.dict()
        )
        self.db.add(db_exception)
        self.db.commit()
        self.db.refresh(db_exception)
        return db_exception

    def get_doctor_exceptions(self, doctor_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[DoctorAvailabilityException]:
        """Obtener excepciones de disponibilidad de un doctor"""
        query = self.db.query(DoctorAvailabilityException).filter(
            DoctorAvailabilityException.doctor_id == doctor_id
        )

        if start_date:
            query = query.filter(DoctorAvailabilityException.exception_date >= start_date)
        if end_date:
            query = query.filter(DoctorAvailabilityException.exception_date <= end_date)

        return query.order_by(DoctorAvailabilityException.exception_date).all()

    def delete_availability_exception(self, exception_id: int) -> bool:
        """Eliminar una excepción de disponibilidad"""
        db_exception = self.db.query(DoctorAvailabilityException).filter(
            DoctorAvailabilityException.id == exception_id
        ).first()
        if not db_exception:
            return False

        self.db.delete(db_exception)
        self.db.commit()
        return True

    # ============ AVAILABILITY CALCULATION ============

    def get_available_slots(self, doctor_id: int, target_date: date) -> AvailableSlotsResponse:
        """Obtener slots disponibles para un doctor en una fecha específica"""

        # 1. Obtener configuración del doctor
        settings = self.get_or_create_doctor_settings(doctor_id)

        # 2. Verificar si el doctor trabaja ese día
        day_of_week = target_date.weekday()  # Python: 0=lunes, 6=domingo
        # Convertir a nuestro formato: 0=domingo, 1=lunes, ..., 6=sábado
        day_of_week = (day_of_week + 1) % 7

        # 3. Obtener horario base del día
        base_schedule = self.db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.day_of_week == day_of_week,
            DoctorSchedule.is_active == True
        ).first()

        if not base_schedule:
            # No hay horario para este día
            return AvailableSlotsResponse(
                doctor_id=doctor_id,
                date=target_date,
                available_slots=[]
            )

        # 4. Verificar excepciones para este día
        exceptions = self.get_doctor_exceptions(doctor_id, target_date, target_date)
        day_exception = next((e for e in exceptions if e.exception_date == target_date), None)

        if day_exception and day_exception.exception_type == ExceptionType.BLOCKED:
            # Día completamente bloqueado
            return AvailableSlotsResponse(
                doctor_id=doctor_id,
                date=target_date,
                available_slots=[]
            )

        # 5. Determinar horario de trabajo para el día
        if day_exception and day_exception.exception_type == ExceptionType.CUSTOM_HOURS:
            work_start = day_exception.start_time or base_schedule.start_time
            work_end = day_exception.end_time or base_schedule.end_time
        else:
            work_start = base_schedule.start_time
            work_end = base_schedule.end_time

        # 6. Generar slots disponibles
        available_slots = []
        current_time = datetime.combine(target_date, work_start)
        end_time = datetime.combine(target_date, work_end)

        # 7. Obtener citas existentes para el día
        # Crear fechas de inicio y fin del día como naive
        day_start = datetime.combine(target_date, time.min)
        day_end = datetime.combine(target_date + timedelta(days=1), time.min)

        existing_appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= day_start,
            Appointment.appointment_date < day_end
        ).all()

        # Crear lista de rangos ocupados
        occupied_ranges = []
        for appointment in existing_appointments:
            # Convertir appointment_date a naive si tiene timezone
            start = appointment.appointment_date.replace(tzinfo=None) if appointment.appointment_date.tzinfo else appointment.appointment_date
            end = start + timedelta(minutes=settings.appointment_duration)
            occupied_ranges.append((start, end))

        # 8. Generar slots disponibles
        while current_time + timedelta(minutes=settings.appointment_duration) <= end_time:
            slot_end = current_time + timedelta(minutes=settings.appointment_duration)

            # Verificar si el slot está ocupado
            is_occupied = any(
                not (slot_end <= occupied_start or current_time >= occupied_end)
                for occupied_start, occupied_end in occupied_ranges
            )

            if not is_occupied:
                available_slots.append(TimeSlot(
                    start_time=current_time.time(),
                    end_time=slot_end.time(),
                    is_available=True
                ))

            # Mover al siguiente slot
            current_time += timedelta(minutes=settings.appointment_duration + settings.break_between_appointments)

        return AvailableSlotsResponse(
            doctor_id=doctor_id,
            date=target_date,
            available_slots=available_slots
        )

    def is_slot_available(self, doctor_id: int, appointment_datetime: datetime, duration_minutes: int = None) -> bool:
        """Verificar si un slot específico está disponible"""
        target_date = appointment_datetime.date()
        target_time = appointment_datetime.time()

        # Obtener configuración
        settings = self.get_or_create_doctor_settings(doctor_id)
        if duration_minutes is None:
            duration_minutes = settings.appointment_duration

        # Obtener slots disponibles para el día
        available_response = self.get_available_slots(doctor_id, target_date)

        # Verificar si el tiempo solicitado está dentro de algún slot disponible
        for slot in available_response.available_slots:
            # La cita debe comenzar exactamente al inicio del slot
            if target_time == slot.start_time:
                # Verificar que hay suficiente tiempo para la duración requerida
                # Convertir appointment_datetime a naive (sin timezone) para comparar consistentemente
                appointment_naive = appointment_datetime.replace(tzinfo=None) if appointment_datetime.tzinfo else appointment_datetime
                slot_end_datetime = datetime.combine(target_date, slot.end_time)
                required_end_datetime = appointment_naive + timedelta(minutes=duration_minutes)

                if required_end_datetime <= slot_end_datetime:
                    return True

        return False