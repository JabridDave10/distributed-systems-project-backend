from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Cita(Base):
    __tablename__ = "cita"

    id_cita = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String(255), nullable=True)
    estado = Column(String(255))

    # Relaciones
    user = relationship("User", back_populates="citas")
