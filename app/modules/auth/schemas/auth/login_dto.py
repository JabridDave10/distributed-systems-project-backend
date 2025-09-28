"""
Esquemas para el login
"""
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    id: int
    firstName: str
    lastName: str
    email: str
    id_role: int
    id_status: bool

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user: UserInfo
