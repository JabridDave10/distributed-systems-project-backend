from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date
from typing import List, Optional
from app.modules.citas.models.cita import Appointment
from app.modules.auth.models.user import User
from app.modules.citas.schemas.cita import AppointmentCreate, AppointmentOut
from app.modules.schedules.services.schedule_service import ScheduleService

class AppointmentService:
    def __init__(self, db: Session):
        self.db = db

    def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """
        Create a new appointment in the database

        Args:
            appointment_data (AppointmentCreate): Appointment data to create

        Returns:
            Appointment: Created appointment

        Raises:
            ValueError: If patient or doctor don't exist or are not valid
        """
        print(f"🚀 APPOINTMENT_SERVICE: Creating new appointment")
        print(f"📋 Data: doctor={appointment_data.doctor_id}, patient={appointment_data.patient_id}, date={appointment_data.appointment_date}")

        # Verificar que el doctor existe y es realmente un doctor (id_role = 2)
        doctor = self.db.query(User).join(User.user_roles).filter(
            User.id_user == appointment_data.doctor_id,
            User.id_status == True
        ).first()

        if not doctor:
            print(f"❌ APPOINTMENT_SERVICE: Doctor with ID {appointment_data.doctor_id} not found")
            raise ValueError("Doctor not found")

        # Verificar que el doctor tiene rol de doctor (id_role = 2)
        doctor_role = any(role.id_role == 2 for role in doctor.user_roles)
        if not doctor_role:
            print(f"❌ APPOINTMENT_SERVICE: User {appointment_data.doctor_id} is not a doctor")
            raise ValueError("The specified user is not a doctor")

        # Verificar que el paciente existe y es realmente un paciente (id_role = 1)
        patient = self.db.query(User).join(User.user_roles).filter(
            User.id_user == appointment_data.patient_id,
            User.id_status == True
        ).first()

        if not patient:
            print(f"❌ APPOINTMENT_SERVICE: Patient with ID {appointment_data.patient_id} not found")
            raise ValueError("Patient not found")

        # Verificar que el paciente tiene rol de paciente (id_role = 1)
        patient_role = any(role.id_role == 1 for role in patient.user_roles)
        if not patient_role:
            print(f"❌ APPOINTMENT_SERVICE: User {appointment_data.patient_id} is not a patient")
            raise ValueError("The specified user is not a patient")

        # Verificar disponibilidad del doctor usando el ScheduleService
        schedule_service = ScheduleService(self.db)

        # Verificar que el slot esté disponible
        is_available = schedule_service.is_slot_available(
            doctor_id=appointment_data.doctor_id,
            appointment_datetime=appointment_data.appointment_date
        )

        if not is_available:
            print(f"❌ APPOINTMENT_SERVICE: Doctor is not available at {appointment_data.appointment_date}")
            raise ValueError("El doctor no está disponible en esa fecha y hora. Por favor, consulte los horarios disponibles.")

        # Verificar que no hay conflicto de horarios para el doctor (verificación adicional)
        doctor_conflict = self.db.query(Appointment).filter(
            Appointment.doctor_id == appointment_data.doctor_id,
            Appointment.appointment_date == appointment_data.appointment_date,
            Appointment.status.in_(["scheduled", "confirmed"]),
            Appointment.deleted_at.is_(None)
        ).first()

        if doctor_conflict:
            print(f"❌ APPOINTMENT_SERVICE: Schedule conflict for doctor at {appointment_data.appointment_date}")
            raise ValueError("The doctor already has an appointment scheduled at that time")

        # Crear la cita
        new_appointment = Appointment(
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_date=appointment_data.appointment_date,
            reason=appointment_data.reason,
            status=appointment_data.status or "scheduled"
        )

        print(f"💾 APPOINTMENT_SERVICE: Saving appointment to database")
        self.db.add(new_appointment)
        self.db.commit()
        self.db.refresh(new_appointment)

        print(f"✅ APPOINTMENT_SERVICE: Appointment created successfully with ID {new_appointment.id}")
        return new_appointment

    def get_all_appointments(self) -> List[Appointment]:
        """
        Get all appointments

        Returns:
            List[Appointment]: List of all appointments
        """
        print(f"🔍 APPOINTMENT_SERVICE: Getting all appointments")
        appointments = self.db.query(Appointment).filter(Appointment.deleted_at.is_(None)).all()
        print(f"✅ APPOINTMENT_SERVICE: Found {len(appointments)} appointments")
        return appointments

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """
        Get an appointment by ID

        Args:
            appointment_id (int): Appointment ID

        Returns:
            Optional[Appointment]: Found appointment or None
        """
        print(f"🔍 APPOINTMENT_SERVICE: Searching appointment with ID {appointment_id}")
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.deleted_at.is_(None)
        ).first()

        if appointment:
            print(f"✅ APPOINTMENT_SERVICE: Appointment found")
        else:
            print(f"❌ APPOINTMENT_SERVICE: Appointment not found")

        return appointment

    def get_appointments_by_doctor(self, doctor_id: int) -> List[Appointment]:
        """
        Get all appointments for a doctor

        Args:
            doctor_id (int): Doctor ID

        Returns:
            List[Appointment]: List of doctor's appointments
        """
        print(f"🔍 APPOINTMENT_SERVICE: Getting appointments for doctor {doctor_id}")
        appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.deleted_at.is_(None)
        ).all()
        print(f"✅ APPOINTMENT_SERVICE: Found {len(appointments)} appointments for the doctor")
        return appointments

    def get_appointments_by_patient(self, patient_id: int) -> List[Appointment]:
        """
        Get all appointments for a patient

        Args:
            patient_id (int): Patient ID

        Returns:
            List[Appointment]: List of patient's appointments
        """
        print(f"🔍 APPOINTMENT_SERVICE: Getting appointments for patient {patient_id}")
        appointments = self.db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.deleted_at.is_(None)
        ).all()
        print(f"✅ APPOINTMENT_SERVICE: Found {len(appointments)} appointments for the patient")
        return appointments

    def update_appointment_status(self, appointment_id: int, new_status: str) -> Optional[Appointment]:
        """
        Update appointment status

        Args:
            appointment_id (int): Appointment ID
            new_status (str): New status

        Returns:
            Optional[Appointment]: Updated appointment or None if not found
        """
        print(f"🔄 APPOINTMENT_SERVICE: Updating appointment {appointment_id} status to '{new_status}'")

        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.deleted_at.is_(None)
        ).first()
        if not appointment:
            print(f"❌ APPOINTMENT_SERVICE: Appointment {appointment_id} not found")
            return None

        appointment.status = new_status
        self.db.commit()
        self.db.refresh(appointment)

        print(f"✅ APPOINTMENT_SERVICE: Status updated successfully")
        return appointment

    def soft_delete_appointment(self, appointment_id: int) -> bool:
        """
        Soft delete an appointment (mark as deleted)

        Args:
            appointment_id (int): Appointment ID

        Returns:
            bool: True if deleted, False if not found
        """
        print(f"🗑️ APPOINTMENT_SERVICE: Soft deleting appointment {appointment_id}")

        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.deleted_at.is_(None)
        ).first()
        if not appointment:
            print(f"❌ APPOINTMENT_SERVICE: Appointment {appointment_id} not found")
            return False

        appointment.deleted_at = datetime.utcnow()
        self.db.commit()

        print(f"✅ APPOINTMENT_SERVICE: Appointment soft deleted successfully")
        return True

    def hard_delete_appointment(self, appointment_id: int) -> bool:
        """
        Hard delete an appointment (permanently remove)

        Args:
            appointment_id (int): Appointment ID

        Returns:
            bool: True if deleted, False if not found
        """
        print(f"🗑️ APPOINTMENT_SERVICE: Hard deleting appointment {appointment_id}")

        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            print(f"❌ APPOINTMENT_SERVICE: Appointment {appointment_id} not found")
            return False

        self.db.delete(appointment)
        self.db.commit()

        print(f"✅ APPOINTMENT_SERVICE: Appointment hard deleted successfully")
        return True

    def get_today_appointments_count(self) -> int:
        """
        Get count of appointments for today

        Returns:
            int: Number of appointments today
        """
        today = date.today()
        count = self.db.query(func.count(Appointment.id)).filter(
            func.date(Appointment.appointment_date) == today,
            Appointment.deleted_at.is_(None)
        ).scalar()
        print(f"📊 APPOINTMENT_SERVICE: Found {count} appointments for today")
        return count or 0

    def get_active_patients_count(self) -> int:
        """
        Get count of unique active patients (patients with at least one appointment)

        Returns:
            int: Number of active patients
        """
        count = self.db.query(func.count(func.distinct(Appointment.patient_id))).filter(
            Appointment.deleted_at.is_(None)
        ).scalar()
        print(f"📊 APPOINTMENT_SERVICE: Found {count} active patients")
        return count or 0

    def get_pending_appointments_count(self) -> int:
        """
        Get count of pending/scheduled appointments

        Returns:
            int: Number of pending appointments
        """
        count = self.db.query(func.count(Appointment.id)).filter(
            Appointment.status.in_(["scheduled", "confirmed", "pending"]),
            Appointment.deleted_at.is_(None)
        ).scalar()
        print(f"📊 APPOINTMENT_SERVICE: Found {count} pending appointments")
        return count or 0

    def get_today_appointments_with_details(self) -> List[dict]:
        """
        Get today's appointments with patient and doctor details

        Returns:
            List[dict]: List of today's appointments with details
        """
        today = date.today()
        appointments = self.db.query(Appointment).join(
            User, Appointment.patient_id == User.id_user, isouter=False
        ).filter(
            func.date(Appointment.appointment_date) == today,
            Appointment.deleted_at.is_(None)
        ).all()

        result = []
        for appointment in appointments:
            # Get patient info
            patient = self.db.query(User).filter(User.id_user == appointment.patient_id).first()

            result.append({
                "id": appointment.id,
                "patient_name": f"{patient.firstName} {patient.lastName}" if patient else "Paciente Desconocido",
                "appointment_date": appointment.appointment_date.isoformat(),
                "reason": appointment.reason or "Consulta General",
                "status": appointment.status,
                "duration": "30 min"  # Por defecto, se puede calcular o almacenar en el futuro
            })

        print(f"📊 APPOINTMENT_SERVICE: Found {len(result)} detailed appointments for today")
        return result