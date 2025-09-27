from pydantic import BaseModel

class CreateCredentialsDto(BaseModel):
    id_user: int
    email: str
    password: str
