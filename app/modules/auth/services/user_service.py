from sqlalchemy.orm import Session
from datetime import datetime
from app.modules.auth.models.user import User
from app.modules.auth.models.credentials import Credentials
from app.modules.auth.models.user_role import UserRole
from app.modules.auth.schemas.user import CreateUserDto, UserResponseDto
from typing import List

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, data: CreateUserDto) -> dict:
        """Crear un nuevo usuario"""
        print("🔍 USER_SERVICE: Iniciando creación de usuario")
        
        # Verificar si el email ya existe en credentials
        print("🔍 USER_SERVICE: Verificando email existente")
        try:
            existing_credentials = self.db.query(Credentials).filter(Credentials.email == data.email).first()
            print(f"🔍 USER_SERVICE: Consulta de email ejecutada, resultado: {existing_credentials}")
        except Exception as e:
            print(f"❌ USER_SERVICE: Error al consultar credentials: {e}")
            raise e
        
        if existing_credentials:
            print("❌ USER_SERVICE: Email ya existe")
            raise ValueError("El email ya está registrado")
        
        # Verificar si la identificación ya existe
        print("🔍 USER_SERVICE: Verificando identificación existente")
        existing_id = self.db.query(User).filter(User.identification == data.identification).first()
        if existing_id:
            print("❌ USER_SERVICE: Identificación ya existe")
            raise ValueError("La identificación ya está registrada")
        
        # Crear nuevo usuario
        print("🔍 USER_SERVICE: Creando nuevo usuario")
        new_user = User(
            firstName=data.firstName,
            lastName=data.lastName,
            identification=data.identification,
            phone=data.phone,
            id_status=True
        )
        
        print("🔍 USER_SERVICE: Agregando usuario a la sesión")
        self.db.add(new_user)
        print("🔍 USER_SERVICE: Haciendo commit del usuario")
        self.db.commit()
        print("🔍 USER_SERVICE: Refrescando usuario")
        self.db.refresh(new_user)
        print(f"✅ USER_SERVICE: Usuario creado con ID: {new_user.id_user}")
        
        # Crear credenciales con la contraseña del frontend
        print("🔍 USER_SERVICE: Creando credenciales")
        new_credentials = Credentials(
            id_user=new_user.id_user,
            email=data.email,
            password=data.password
        )
        
        print("🔍 USER_SERVICE: Agregando credenciales a la sesión")
        self.db.add(new_credentials)
        
        # Crear la relación user_role
        print(f"🔍 USER_SERVICE: Creando user_role con id_role={data.id_role}")
        new_user_role = UserRole(
            id_user=new_user.id_user,
            id_role=data.id_role
        )
        
        print("🔍 USER_SERVICE: Agregando user_role a la sesión")
        self.db.add(new_user_role)
        print("🔍 USER_SERVICE: Haciendo commit final")
        self.db.commit()
        print("🔍 USER_SERVICE: Refrescando objetos")
        self.db.refresh(new_credentials)
        self.db.refresh(new_user_role)
        
        print("✅ USER_SERVICE: Usuario creado exitosamente")
        return {
            "message": "Usuario registrado exitosamente",
            "id": new_user.id_user,
            "firstName": new_user.firstName,
            "lastName": new_user.lastName
        }
    
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
            id=user.id_user,
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
        
        return [
            UserResponseDto(
                id_user=user.id_user,
                firstName=user.firstName,
                lastName=user.lastName,
                identification=user.identification,
                phone=user.phone,
                email=user.email,
                userType=None,  # Por ahora null hasta que agreguemos el campo a la BD
                id_status=user.id_status
            )
            for user in users
        ]
