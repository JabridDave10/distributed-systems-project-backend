# Schema para actualizar asignación usuario-rol (PUT/PATCH)
class UserRoleUpdate(BaseModel):
    id_user: Optional[int] = None
    id_role: Optional[int] = None