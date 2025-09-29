"""
Dependencias para autenticación y autorización
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_user_from_token
from app.modules.auth.services.user_service import UserService

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_jwt_auth(request: Request, db: Session = Depends(get_db)):
    """
    Dependencia para verificar JWT y obtener el usuario actual autenticado desde cookies HttpOnly o header Authorization
    """
    try:
        # Debug logging
        print(f"🔍 JWT AUTH: Checking authentication")
        print(f"🔍 JWT AUTH: Available cookies: {dict(request.cookies)}")
        print(f"🔍 JWT AUTH: Authorization header: {request.headers.get('Authorization', 'None')}")

        # Obtener token desde cookie HttpOnly o header Authorization
        token = request.cookies.get("auth_token")
        print(f"🔍 JWT AUTH: Token from cookies: {'Found' if token else 'Not found'}")

        # Si no hay token en cookies, intentar obtenerlo del header Authorization
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                print(f"🔍 JWT AUTH: Token from header: Found")
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticación no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        email = get_user_from_token(token)
        user_service = UserService(db)
        
        # Buscar credenciales por email
        from app.modules.auth.models.credentials import Credentials
        credentials = db.query(Credentials).filter(Credentials.email == email).first()
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Obtener información completa del usuario sin verificar contraseña
        user_info = user_service.get_user_info_by_email(email)
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al obtener usuario actual: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def require_role(required_role: int):
    """
    Dependencia para verificar que el usuario tenga un rol específico
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("id_role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso"
            )
        return current_user
    
    return role_checker
