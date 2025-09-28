"""
Router para el registro de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.register.services.register_service import RegisterService
from app.modules.register.schemas.create_user_dto import CreateUserDto

router = APIRouter(prefix="/register", tags=["register"])

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(data: CreateUserDto, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario
    """
    print("🚀 ENDPOINT EJECUTÁNDOSE - /register/")
    print(f"🔍 Datos recibidos: {data}")
    print(f"🔍 Tipo: {type(data)}")
    print(f"🔍 Diccionario: {data.dict()}")
    try:
        register_service = RegisterService(db)
        new_user = register_service.create_user(data)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
