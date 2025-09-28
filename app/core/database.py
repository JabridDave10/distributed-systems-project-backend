from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

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
    from app.modules.citas.models.cita import Cita

    print("Creando tablas...")
    print(f"Tablas a crear: {list(Base.metadata.tables.keys())}")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")