from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Appointment(Base):
    __tablename__ = "appointment"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(String(50), default="scheduled")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="appointments_as_patient")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="appointments_as_doctor")
    medical_history = relationship("MedicalHistory", back_populates="appointment")
