"""
Router de autenticación con JWT
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.dependencies import get_db, get_current_user
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.modules.auth.services.user_service import UserService
from app.modules.auth.schemas.auth.login_dto import LoginRequest, LoginResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Iniciar sesión con email y contraseña
    """
    print("🚀 ENDPOINT EJECUTÁNDOSE - /auth/login")
    print(f"🔍 Datos de login recibidos: {login_data.email}")
    
    try:
        user_service = UserService(db)
        user_info = user_service.verify_credentials(login_data.email, login_data.password)
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_info["email"]}, 
            expires_delta=access_token_expires
        )
        
        # Configurar cookie HttpOnly
        response.set_cookie(
            key="auth_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convertir minutos a segundos
            httponly=True,
            secure=True,  # Solo HTTPS en producción
            samesite="lax"  # Protección CSRF
        )
        
        return LoginResponse(
            message="Login exitoso",
            access_token="",  # No enviar el token en la respuesta
            token_type="bearer",
            user=UserInfo(**user_info)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"❌ Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obtener información del usuario actual
    """
    return UserInfo(**current_user)

@router.post("/logout")
async def logout(response: Response):
    """
    Cerrar sesión - eliminar cookie HttpOnly
    """
    # Eliminar la cookie HttpOnly
    response.delete_cookie(
        key="auth_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return {"message": "Sesión cerrada exitosamente"}
