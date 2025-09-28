from sqlalchemy.orm import Session
from datetime import datetime
from app.modules.auth.models.user import User
from app.modules.auth.models.credentials import Credentials
from app.modules.auth.models.user_role import UserRole
from app.modules.auth.schemas.user.user_response_dto import UserResponseDto
from app.core.security import get_password_hash, verify_password
from typing import List

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    
    def get_user_by_id(self, user_id: int) -> UserResponseDto:
        """Obtener usuario por ID"""
        user = self.db.query(User).filter(User.id_user == user_id).first()
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Obtener credenciales del usuario
        credentials = self.db.query(Credentials).filter(Credentials.id_user == user_id).first()
        
        # Obtener el rol del usuario
        user_role = self.db.query(UserRole).filter(UserRole.id_user == user_id).first()
        
        return UserResponseDto(
            id_user=user.id_user,
            firstName=user.firstName,
            lastName=user.lastName,
            identification=user.identification,
            phone=user.phone or "",
            email=credentials.email if credentials else "",
            id_status=user.id_status,
            id_role=user_role.id_role if user_role else 1,  # Por defecto paciente
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat()
        )
    
    def get_all_users(self) -> List[UserResponseDto]:
        """Obtener todos los usuarios"""
        users = self.db.query(User).all()
        result = []
        
        for user in users:
            # Obtener credenciales del usuario
            credentials = self.db.query(Credentials).filter(Credentials.id_user == user.id_user).first()
            
            # Obtener el rol del usuario
            user_role = self.db.query(UserRole).filter(UserRole.id_user == user.id_user).first()
            
            result.append(UserResponseDto(
                id_user=user.id_user,
                firstName=user.firstName,
                lastName=user.lastName,
                identification=user.identification,
                phone=user.phone or "",
                email=credentials.email if credentials else "",
                id_status=user.id_status,
                id_role=user_role.id_role if user_role else 1,
                createdAt=datetime.now().isoformat(),
                updatedAt=datetime.now().isoformat()
            ))
        
        return result
    
    def verify_credentials(self, email: str, password: str) -> dict:
        """
        Verificar credenciales de login
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            dict: Información del usuario si las credenciales son correctas
        """
        print(f"🔍 USER_SERVICE: Verificando credenciales para {email}")
        
        # Buscar credenciales por email
        credentials = self.db.query(Credentials).filter(Credentials.email == email).first()
        if not credentials:
            print("❌ USER_SERVICE: Email no encontrado")
            raise ValueError("Credenciales inválidas")
        
        # Verificar contraseña
        if not verify_password(password, credentials.password):
            print("❌ USER_SERVICE: Contraseña incorrecta")
            raise ValueError("Credenciales inválidas")
        
        # Obtener información del usuario
        user = self.db.query(User).filter(User.id_user == credentials.id_user).first()
        if not user:
            print("❌ USER_SERVICE: Usuario no encontrado")
            raise ValueError("Usuario no encontrado")
        
        # Obtener rol del usuario
        user_role = self.db.query(UserRole).filter(UserRole.id_user == user.id_user).first()
        
        print("✅ USER_SERVICE: Credenciales verificadas correctamente")
        return {
            "id": user.id_user,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": credentials.email,
            "id_role": user_role.id_role if user_role else 1,
            "id_status": user.id_status
        }
