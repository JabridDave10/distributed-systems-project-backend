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
    citas_como_paciente = relationship("Cita", foreign_keys="Cita.id_paciente", back_populates="paciente")
    citas_como_doctor = relationship("Cita", foreign_keys="Cita.id_doctor", back_populates="doctor")