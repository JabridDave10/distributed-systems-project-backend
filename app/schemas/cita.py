from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Cita(Base):
    __tablename__ = "cita"

    id_cita = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String(255), nullable=True)
    estado = Column(String(255))

    # Llaves foráneas
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_doctor = Column(Integer, ForeignKey("doctor.id_doctor"), nullable=False)

    # Relaciones
    paciente = relationship("Paciente", back_populates="citas")
    doctor = relationship("Doctor", back_populates="citas")
