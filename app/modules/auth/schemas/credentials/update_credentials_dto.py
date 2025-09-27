from pydantic import BaseModel, EmailStr
from typing import Optional

class UpdateCredentialsDto(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
