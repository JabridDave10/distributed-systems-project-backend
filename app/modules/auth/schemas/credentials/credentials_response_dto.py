from pydantic import BaseModel, EmailStr

class CredentialsResponseDto(BaseModel):
    id_credentials: int
    id_user: int
    email: EmailStr

    class Config:
        from_attributes = True
