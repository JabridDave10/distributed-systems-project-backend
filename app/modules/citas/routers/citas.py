from fastapi import APIRouter, HTTPException
from typing import List
from app.modules.citas.schemas.cita import CitaOut, CitaCreate, CitaUpdate
from datetime import datetime

router = APIRouter(prefix="/citas", tags=["citas"])

# Datos de prueba en memoria (simulando base de datos)
citas_mock = [
    {
        "id_cita": 1,
        "fecha_hora": "2024-01-15T10:00:00",
        "motivo": "Consulta general",
        "estado": "programada",
        "id_paciente": 1,
        "id_doctor": 1
    },
    {
        "id_cita": 2,
        "fecha_hora": "2024-01-16T14:30:00",
        "motivo": "Revisión",
        "estado": "confirmada",
        "id_paciente": 2,
        "id_doctor": 1
    }
]

@router.get("/", response_model=List[CitaOut])
def get_citas():
    """
    Obtener todas las citas.
    Endpoint de prueba para verificar que el frontend puede obtener datos.
    """
    return citas_mock

@router.get("/{cita_id}", response_model=CitaOut)
def get_cita(cita_id: int):
    """
    Obtener una cita específica por ID.
    """
    for cita in citas_mock:
        if cita["id_cita"] == cita_id:
            return cita
    
    raise HTTPException(status_code=404, detail="Cita no encontrada")

@router.post("/", response_model=CitaOut)
def create_cita(cita: CitaCreate):
    """
    Crear una nueva cita.
    Endpoint de prueba para verificar que el frontend puede enviar datos.
    """
    new_id = max([c["id_cita"] for c in citas_mock]) + 1 if citas_mock else 1
    
    new_cita = {
        "id_cita": new_id,
        "fecha_hora": cita.fecha_hora.isoformat(),
        "motivo": cita.motivo,
        "estado": cita.estado or "programada",
        "id_paciente": cita.id_paciente,
        "id_doctor": cita.id_doctor
    }
    
    citas_mock.append(new_cita)
    return new_cita

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

