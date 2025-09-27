from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime
from app.modules.auth.schemas.user import (
    UserCreate, UserUpdate, UserOut, UserDetail, 
    UserLogin, UserLoginResponse, UserRegisterResponse,
    UserListResponse, UserPasswordChange
)
from app.modules.auth.models.user import User, UserRole, UserStatus

router = APIRouter(prefix="/users", tags=["users"])

# Datos de prueba en memoria (simulando base de datos)
users_mock = [
    {
        "id": 1,
        "email": "admin@hospital.com",
        "username": "admin",
        "first_name": "Administrador",
        "last_name": "Sistema",
        "phone": "+1234567890",
        "role": "admin",
        "status": "active",
        "is_verified": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "last_login": "2024-01-15T10:30:00"
    },
    {
        "id": 2,
        "email": "doctor@hospital.com",
        "username": "dr_smith",
        "first_name": "John",
        "last_name": "Smith",
        "phone": "+1234567891",
        "role": "doctor",
        "status": "active",
        "is_verified": True,
        "created_at": "2024-01-02T00:00:00",
        "updated_at": "2024-01-02T00:00:00",
        "last_login": "2024-01-15T09:15:00"
    },
    {
        "id": 3,
        "email": "paciente@email.com",
        "username": "jane_doe",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone": "+1234567892",
        "role": "paciente",
        "status": "active",
        "is_verified": True,
        "created_at": "2024-01-03T00:00:00",
        "updated_at": "2024-01-03T00:00:00",
        "last_login": "2024-01-14T16:45:00"
    }
]

@router.get("/", response_model=UserListResponse)
def get_users(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    role: Optional[UserRole] = Query(None, description="Filtrar por rol"),
    status: Optional[UserStatus] = Query(None, description="Filtrar por estado")
):
    """
    Obtener lista de usuarios con paginación y filtros.
    Solo administradores pueden acceder a esta información.
    """
    # Filtrar usuarios
    filtered_users = users_mock.copy()
    
    if role:
        filtered_users = [u for u in filtered_users if u["role"] == role.value]
    
    if status:
        filtered_users = [u for u in filtered_users if u["status"] == status.value]
    
    # Paginación
    total = len(filtered_users)
    start = (page - 1) * size
    end = start + size
    paginated_users = filtered_users[start:end]
    
    # Calcular páginas
    pages = (total + size - 1) // size
    
    return UserListResponse(
        users=paginated_users,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{user_id}", response_model=UserDetail)
def get_user(user_id: int):
    """
    Obtener un usuario específico por ID.
    """
    for user in users_mock:
        if user["id"] == user_id:
            return user
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )

@router.post("/", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """
    Crear un nuevo usuario.
    """
    # Verificar si el email ya existe
    for existing_user in users_mock:
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
    
    # Crear nuevo usuario
    new_id = max([u["id"] for u in users_mock]) + 1 if users_mock else 1
    new_user = {
        "id": new_id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role": user.role.value,
        "status": user.status.value,
        "is_verified": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    users_mock.append(new_user)
    
    return UserRegisterResponse(
        message="Usuario creado exitosamente",
        user=new_user
    )

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserUpdate):
    """
    Actualizar un usuario existente.
    """
    for i, user in enumerate(users_mock):
        if user["id"] == user_id:
            # Verificar email único si se está actualizando
            if user_update.email and user_update.email != user["email"]:
                for other_user in users_mock:
                    if other_user["id"] != user_id and other_user["email"] == user_update.email:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El email ya está registrado"
                        )
            
            # Verificar username único si se está actualizando
            if user_update.username and user_update.username != user["username"]:
                for other_user in users_mock:
                    if other_user["id"] != user_id and other_user["username"] == user_update.username:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El nombre de usuario ya está en uso"
                        )
            
            # Actualizar campos
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(value, 'value'):  # Para enums
                    users_mock[i][field] = value.value
                else:
                    users_mock[i][field] = value
            
            users_mock[i]["updated_at"] = datetime.now().isoformat()
            return users_mock[i]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """
    Eliminar un usuario (soft delete - cambiar estado a inactive).
    """
    for i, user in enumerate(users_mock):
        if user["id"] == user_id:
            users_mock[i]["status"] = "inactive"
            users_mock[i]["updated_at"] = datetime.now().isoformat()
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )

@router.get("/test/connection")
def test_connection():
    """
    Endpoint específico para probar la conexión desde el frontend.
    """
    return {
        "message": "¡Módulo de usuarios funcionando! 🎉",
        "server_time": datetime.now().isoformat(),
        "total_users": len(users_mock),
        "endpoints_available": [
            "GET /users/",
            "GET /users/{id}",
            "POST /users/",
            "PUT /users/{id}",
            "DELETE /users/{id}",
            "GET /users/test/connection"
        ],
        "status": "ready"
    }
