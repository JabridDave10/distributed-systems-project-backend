from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    identification = Column(String(20), nullable=False)
    phone = Column(String(20))
    id_status = Column(Boolean, default=True)

    # Relaciones
    user_roles = relationship("UserRole", back_populates="user")
    credentials = relationship("Credentials", back_populates="user")
    appointments_as_patient = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient")
    appointments_as_doctor = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")

    # Legacy relationships for backward compatibility
    citas_como_paciente = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient")
    citas_como_doctor = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")

    # Schedule relationships
    schedules = relationship("DoctorSchedule", back_populates="doctor")
    availability_exceptions = relationship("DoctorAvailabilityException", back_populates="doctor")
    doctor_settings = relationship("DoctorSettings", back_populates="doctor", uselist=False)