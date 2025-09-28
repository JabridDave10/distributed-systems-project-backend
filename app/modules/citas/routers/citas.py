from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.modules.citas.schemas.cita import CitaOut, CitaCreate, CitaUpdate
from app.modules.citas.services.cita_service import CitaService
from app.core.database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="/citas", tags=["citas"])

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[CitaOut])
def get_citas(db: Session = Depends(get_db)):
    """
    Obtener todas las citas desde la base de datos
    """
    try:
        print("🚀 ENDPOINT: /citas/ - Obteniendo todas las citas")
        cita_service = CitaService(db)
        citas = cita_service.get_all_citas()

        # Convertir a formato de salida
        result = []
        for cita in citas:
            result.append(CitaOut(
                id_cita=cita.id_cita,
                fecha_hora=cita.fecha_hora,
                motivo=cita.motivo,
                estado=cita.estado,
                id_paciente=cita.id_paciente,
                id_doctor=cita.id_doctor
            ))

        print(f"✅ ENDPOINT: Retornando {len(result)} citas")
        return result
    except Exception as e:
        print(f"❌ ENDPOINT: Error obteniendo citas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{cita_id}", response_model=CitaOut)
def get_cita(cita_id: int, db: Session = Depends(get_db)):
    """
    Obtener una cita específica por ID desde la base de datos
    """
    try:
        print(f"🚀 ENDPOINT: /citas/{cita_id} - Obteniendo cita específica")
        cita_service = CitaService(db)
        cita = cita_service.get_cita_by_id(cita_id)

        if not cita:
            print(f"❌ ENDPOINT: Cita {cita_id} no encontrada")
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        result = CitaOut(
            id_cita=cita.id_cita,
            fecha_hora=cita.fecha_hora,
            motivo=cita.motivo,
            estado=cita.estado,
            id_paciente=cita.id_paciente,
            id_doctor=cita.id_doctor
        )

        print(f"✅ ENDPOINT: Cita encontrada")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENDPOINT: Error obteniendo cita: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/", response_model=CitaOut)
def create_cita(cita: CitaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva cita en la base de datos
    """
    try:
        print("🚀 ENDPOINT: POST /citas/ - Creando nueva cita")
        print(f"📋 Datos recibidos: {cita.dict()}")

        cita_service = CitaService(db)
        nueva_cita = cita_service.create_cita(cita)

        result = CitaOut(
            id_cita=nueva_cita.id_cita,
            fecha_hora=nueva_cita.fecha_hora,
            motivo=nueva_cita.motivo,
            estado=nueva_cita.estado,
            id_paciente=nueva_cita.id_paciente,
            id_doctor=nueva_cita.id_doctor
        )

        print(f"✅ ENDPOINT: Cita creada exitosamente con ID {nueva_cita.id_cita}")
        return result
    except ValueError as e:
        print(f"❌ ENDPOINT: Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ ENDPOINT: Error creando cita: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/test/connection")
def test_connection():
    """
    Endpoint específico para probar la conexión desde el frontend.
    Retorna información básica del servidor.
    """
    return {
        "message": "¡Conexión exitosa! 🎉",
        "server_time": datetime.now().isoformat(),
        "endpoints_available": [
            "GET /health/",
            "GET /health/ping", 
            "GET /citas/",
            "GET /citas/{id}",
            "POST /citas/",
            "GET /citas/test/connection"
        ],
        "status": "ready"
    }

