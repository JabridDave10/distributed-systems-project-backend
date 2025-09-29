from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# Para Render, usar DATABASE_URL si está disponible (recomendado)
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fallback para desarrollo local
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    """Crear todas las tablas en la base de datos"""
    from app.modules.auth.models.user import User
    from app.modules.auth.models.role import Role
    from app.modules.auth.models.user_role import UserRole
    from app.modules.auth.models.credentials import Credentials
    from app.modules.citas.models.cita import Appointment
    from app.modules.schedules.models.doctor_schedule import DoctorSchedule
    from app.modules.schedules.models.doctor_availability_exception import DoctorAvailabilityException
    from app.modules.schedules.models.doctor_settings import DoctorSettings

    print("Creando tablas...")
    print(f"Tablas a crear: {list(Base.metadata.tables.keys())}")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")