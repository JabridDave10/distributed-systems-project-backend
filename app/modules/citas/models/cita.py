from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Cita(Base):
    __tablename__ = "cita"

    id_cita = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    id_doctor = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String(255), nullable=True)
    estado = Column(String(50), default="programada")

    # Relaciones
    paciente = relationship("User", foreign_keys=[id_paciente], back_populates="citas_como_paciente")
    doctor = relationship("User", foreign_keys=[id_doctor], back_populates="citas_como_doctor")
