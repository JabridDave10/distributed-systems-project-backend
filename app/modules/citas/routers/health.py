from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    """
    Endpoint para verificar que el backend esté funcionando correctamente.
    Útil para el frontend para verificar conectividad.
    """
    return {
        "status": "healthy",
        "message": "Backend funcionando correctamente 🚀",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

@router.get("/ping")
def ping():
    """
    Endpoint simple de ping/pong para verificar conectividad básica.
    """
    return {"message": "pong", "timestamp": datetime.now().isoformat()}
