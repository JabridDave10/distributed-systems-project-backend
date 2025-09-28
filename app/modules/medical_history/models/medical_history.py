from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id_medical_history = Column(Integer, primary_key=True, index=True)
    id_patient = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    id_doctor = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    id_appointment = Column(Integer, ForeignKey("appointment.id"), nullable=False)
    diagnosis = Column(Text, nullable=False)
    treatment = Column(Text, nullable=False)
    medication = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    patient = relationship("User", foreign_keys=[id_patient], back_populates="medical_histories_as_patient")
    doctor = relationship("User", foreign_keys=[id_doctor], back_populates="medical_histories_as_doctor")
    appointment = relationship("Appointment", back_populates="medical_history")
