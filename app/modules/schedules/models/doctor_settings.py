from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DoctorSettings(Base):
    __tablename__ = "doctor_settings"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("user.id_user"), nullable=False, unique=True, index=True)
    appointment_duration = Column(Integer, default=30, nullable=False)  # minutos por cita
    break_between_appointments = Column(Integer, default=5, nullable=False)  # tiempo entre citas en minutos
    advance_booking_days = Column(Integer, default=30, nullable=False)  # días máximos para agendar
    allow_weekend_appointments = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    doctor = relationship("User", back_populates="doctor_settings", uselist=False)

    def __repr__(self):
        return f"<DoctorSettings(doctor_id={self.doctor_id}, duration={self.appointment_duration}min)>"