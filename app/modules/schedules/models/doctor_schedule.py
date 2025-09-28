from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("user.id_user"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=domingo, 1=lunes, ..., 6=sábado
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    doctor = relationship("User", back_populates="schedules")

    def __repr__(self):
        return f"<DoctorSchedule(doctor_id={self.doctor_id}, day={self.day_of_week}, {self.start_time}-{self.end_time})>"