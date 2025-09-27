from pydantic import BaseModel

class UserRoleResponseDto(BaseModel):
    id_user_role: int
    id_user: int
    id_role: int

    class Config:
        from_attributes = True
