from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema base para User
class UserBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: Optional[str] = None
    activo: bool = True

# Schema para crear usuario (POST)
class UserCreate(UserBase):
    password: str

# Schema para actualizar usuario (PUT/PATCH)
class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    password: Optional[str] = None
    activo: Optional[bool] = None

# Schema para respuesta de usuario (GET)
class UserOut(UserBase):
    id_user: int

    class Config:
        from_attributes = True