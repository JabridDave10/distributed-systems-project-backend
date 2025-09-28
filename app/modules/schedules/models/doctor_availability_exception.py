from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ExceptionType(enum.Enum):
    BLOCKED = "blocked"
    CUSTOM_HOURS = "custom_hours"

class DoctorAvailabilityException(Base):
    __tablename__ = "doctor_availability_exceptions"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("user.id_user"), nullable=False, index=True)
    exception_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=True)  # Null si es día completo bloqueado
    end_time = Column(Time, nullable=True)    # Null si es día completo bloqueado
    exception_type = Column(Enum(ExceptionType), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    doctor = relationship("User", back_populates="availability_exceptions")

    def __repr__(self):
        return f"<DoctorAvailabilityException(doctor_id={self.doctor_id}, date={self.exception_date}, type={self.exception_type})>"