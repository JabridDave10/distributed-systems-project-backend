from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
from app.modules.medical_history.models.medical_history import MedicalHistory
from app.modules.medical_history.schemas.medical_history_dto import MedicalHistoryCreate, MedicalHistoryUpdate
from app.modules.auth.models.user import User
from app.modules.citas.models.cita import Appointment

class MedicalHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_medical_history(self, medical_data: MedicalHistoryCreate) -> MedicalHistory:
        """
        Crear un nuevo registro de historial médico
        """
        print(f"🔍 MEDICAL_HISTORY_SERVICE: Creando historial médico")
        print(f"📋 Data: appointment={medical_data.id_appointment}, patient={medical_data.id_patient}, doctor={medical_data.id_doctor}")

        # Verificar que la cita existe
        appointment = self.db.query(Appointment).filter(
            Appointment.id == medical_data.id_appointment,
            Appointment.deleted_at.is_(None)
        ).first()

        if not appointment:
            print(f"❌ MEDICAL_HISTORY_SERVICE: Cita con ID {medical_data.id_appointment} no encontrada")
            raise ValueError("La cita no existe")

        # Verificar que el doctor es el asignado a la cita
        if appointment.doctor_id != medical_data.id_doctor:
            print(f"❌ MEDICAL_HISTORY_SERVICE: El doctor {medical_data.id_doctor} no está asignado a esta cita")
            raise ValueError("No tienes permisos para crear el historial de esta cita")

        # Verificar que el paciente es el correcto
        if appointment.patient_id != medical_data.id_patient:
            print(f"❌ MEDICAL_HISTORY_SERVICE: El paciente {medical_data.id_patient} no coincide con la cita")
            raise ValueError("El paciente no coincide con la cita")

        # Verificar que no existe ya un historial para esta cita
        existing_history = self.db.query(MedicalHistory).filter(
            MedicalHistory.id_appointment == medical_data.id_appointment,
            MedicalHistory.deleted_at.is_(None)
        ).first()

        if existing_history:
            print(f"❌ MEDICAL_HISTORY_SERVICE: Ya existe un historial médico para esta cita")
            raise ValueError("Ya existe un historial médico para esta cita")

        # Crear el historial médico
        new_medical_history = MedicalHistory(
            id_patient=medical_data.id_patient,
            id_doctor=medical_data.id_doctor,
            id_appointment=medical_data.id_appointment,
            diagnosis=medical_data.diagnosis,
            treatment=medical_data.treatment,
            medication=medical_data.medication,
            symptoms=medical_data.symptoms,
            notes=medical_data.notes
        )

        self.db.add(new_medical_history)
        self.db.commit()
        self.db.refresh(new_medical_history)

        print(f"✅ MEDICAL_HISTORY_SERVICE: Historial médico creado con ID: {new_medical_history.id_medical_history}")
        return new_medical_history

    def get_medical_history_by_appointment(self, appointment_id: int) -> Optional[MedicalHistory]:
        """
        Obtener historial médico por ID de cita
        """
        return self.db.query(MedicalHistory).filter(
            MedicalHistory.id_appointment == appointment_id,
            MedicalHistory.deleted_at.is_(None)
        ).first()

    def get_medical_histories_by_patient(self, patient_id: int) -> List[MedicalHistory]:
        """
        Obtener todos los historiales médicos de un paciente
        """
        return self.db.query(MedicalHistory).filter(
            MedicalHistory.id_patient == patient_id,
            MedicalHistory.deleted_at.is_(None)
        ).order_by(MedicalHistory.created_at.desc()).all()

    def get_medical_histories_by_doctor(self, doctor_id: int) -> List[MedicalHistory]:
        """
        Obtener todos los historiales médicos creados por un doctor
        """
        return self.db.query(MedicalHistory).filter(
            MedicalHistory.id_doctor == doctor_id,
            MedicalHistory.deleted_at.is_(None)
        ).order_by(MedicalHistory.created_at.desc()).all()

    def update_medical_history(self, history_id: int, update_data: MedicalHistoryUpdate, doctor_id: int) -> Optional[MedicalHistory]:
        """
        Actualizar historial médico (solo el doctor que lo creó)
        """
        medical_history = self.db.query(MedicalHistory).filter(
            MedicalHistory.id_medical_history == history_id,
            MedicalHistory.deleted_at.is_(None)
        ).first()

        if not medical_history:
            raise ValueError("Historial médico no encontrado")

        if medical_history.id_doctor != doctor_id:
            raise ValueError("No tienes permisos para actualizar este historial")

        # Actualizar solo los campos proporcionados
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(medical_history, field, value)

        medical_history.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(medical_history)

        return medical_history

    def delete_medical_history(self, history_id: int, doctor_id: int) -> bool:
        """
        Eliminar (soft delete) historial médico
        """
        medical_history = self.db.query(MedicalHistory).filter(
            MedicalHistory.id_medical_history == history_id,
            MedicalHistory.deleted_at.is_(None)
        ).first()

        if not medical_history:
            raise ValueError("Historial médico no encontrado")

        if medical_history.id_doctor != doctor_id:
            raise ValueError("No tienes permisos para eliminar este historial")

        medical_history.deleted_at = datetime.utcnow()
        self.db.commit()

        return True
