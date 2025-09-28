from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.auth.services.user_service import UserService
from app.modules.auth.schemas.user.user_response_dto import UserResponseDto
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/test")
def test_endpoint():
    """Endpoint de prueba"""
    print("🧪 ENDPOINT DE PRUEBA EJECUTÁNDOSE")
    return {"message": "Router de usuarios funcionando", "status": "ok"}

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}", response_model=UserResponseDto)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener un usuario por ID
    """
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[UserResponseDto])
def get_all_users(db: Session = Depends(get_db)):
    """
    Obtener todos los usuarios
    """
    try:
        user_service = UserService(db)
        users = user_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )