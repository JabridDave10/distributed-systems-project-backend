from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserRole(Base):
    __tablename__ = "user_role"

    id_user_role = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    id_role = Column(Integer, ForeignKey("role.id_role"), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
