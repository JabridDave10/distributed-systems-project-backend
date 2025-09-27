from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from app.modules.auth.schemas.user import UserLogin, UserLoginResponse, UserCreate, UserRegisterResponse
from app.modules.auth.models.user import UserRole, UserStatus

router = APIRouter(prefix="/auth", tags=["authentication"])

# Simulación de base de datos de usuarios para autenticación
auth_users_mock = [
    {
        "id": 1,
        "email": "admin@hospital.com",
        "username": "admin",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8",  # "admin123"
        "first_name": "Administrador",
        "last_name": "Sistema",
        "role": "admin",
        "status": "active",
        "is_verified": True
    },
    {
        "id": 2,
        "email": "doctor@hospital.com",
        "username": "dr_smith",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8",  # "doctor123"
        "first_name": "John",
        "last_name": "Smith",
        "role": "doctor",
        "status": "active",
        "is_verified": True
    },
    {
        "id": 3,
        "email": "paciente@email.com",
        "username": "jane_doe",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8",  # "paciente123"
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "paciente",
        "status": "active",
        "is_verified": True
    }
]

# Simulación de tokens (en producción usar JWT real)
tokens_mock = {}

@router.post("/login", response_model=UserLoginResponse)
def login(credentials: UserLogin):
    """
    Iniciar sesión con email y contraseña.
    """
    # Buscar usuario por email
    user = None
    for u in auth_users_mock:
        if u["email"] == credentials.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # Verificar contraseña (en producción usar bcrypt)
    # Para demo, aceptamos cualquier contraseña que termine en "123"
    if not credentials.password.endswith("123"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # Verificar estado del usuario
    if user["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    # Generar token (simulado)
    token = f"mock_token_{user['id']}_{datetime.now().timestamp()}"
    tokens_mock[token] = {
        "user_id": user["id"],
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    
    # Actualizar último login
    user["last_login"] = datetime.now().isoformat()
    
    # Preparar respuesta del usuario (sin contraseña)
    user_response = {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "phone": None,
        "role": user["role"],
        "status": user["status"],
        "is_verified": user["is_verified"],
        "created_at": "2024-01-01T00:00:00",
        "updated_at": datetime.now().isoformat(),
        "last_login": user["last_login"]
    }
    
    return UserLoginResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """
    Registrar un nuevo usuario.
    """
    # Verificar si el email ya existe
    for existing_user in auth_users_mock:
        if existing_user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        if existing_user["username"] == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
    
    # Crear nuevo usuario
    new_id = max([u["id"] for u in auth_users_mock]) + 1 if auth_users_mock else 1
    new_user = {
        "id": new_id,
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": f"$2b$12$hashed_{user_data.password}",  # En producción usar bcrypt
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "role": user_data.role.value,
        "status": user_data.status.value,
        "is_verified": False
    }
    
    auth_users_mock.append(new_user)
    
    # Preparar respuesta del usuario (sin contraseña)
    user_response = {
        "id": new_user["id"],
        "email": new_user["email"],
        "username": new_user["username"],
        "first_name": new_user["first_name"],
        "last_name": new_user["last_name"],
        "phone": new_user["phone"],
        "role": new_user["role"],
        "status": new_user["status"],
        "is_verified": new_user["is_verified"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    return UserRegisterResponse(
        message="Usuario registrado exitosamente",
        user=user_response
    )

@router.post("/logout")
def logout():
    """
    Cerrar sesión (invalidar token).
    """
    return {"message": "Sesión cerrada exitosamente"}

@router.get("/me")
def get_current_user():
    """
    Obtener información del usuario actual.
    En producción, esto requeriría validación de token.
    """
    return {
        "message": "Endpoint para obtener usuario actual",
        "note": "Requiere implementación de autenticación JWT"
    }

@router.get("/test/connection")
def test_connection():
    """
    Endpoint específico para probar la conexión desde el frontend.
    """
    return {
        "message": "¡Módulo de autenticación funcionando! 🔐",
        "server_time": datetime.now().isoformat(),
        "total_users": len(auth_users_mock),
        "active_tokens": len(tokens_mock),
        "endpoints_available": [
            "POST /auth/login",
            "POST /auth/register",
            "POST /auth/logout",
            "GET /auth/me",
            "GET /auth/test/connection"
        ],
        "demo_credentials": {
            "admin": {"email": "admin@hospital.com", "password": "admin123"},
            "doctor": {"email": "doctor@hospital.com", "password": "doctor123"},
            "paciente": {"email": "paciente@email.com", "password": "paciente123"}
        },
        "status": "ready"
    }
