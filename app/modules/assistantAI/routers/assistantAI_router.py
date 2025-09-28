from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from typing import Dict, Any

from app.modules.assistantAI.services.assistantAI_service import AssistantAIService
from app.modules.assistantAI.schemas.assistantAI_schemas import (
    SintomasRequest, TratamientoRequest, EmergenciaRequest,
    EnfermedadResponse, DiagnosticoResponse, TratamientoResponse,
    MedicamentoResponse, EmergenciaResponse, ErrorResponse
)

# Importar dependencia de autenticación centralizada
from app.core.dependencies import verify_jwt_auth

router = APIRouter(prefix="/assistantAI", tags=["assistantAI"])

# Inicializar el servicio médico
try:
    assistantAI_service = AssistantAIService()
except ValueError as e:
    print(f"❌ Error inicializando AssistantAIService: {e}")
    assistantAI_service = None


@router.get("/health")
async def health_check(current_user: dict = Depends(verify_jwt_auth)):
    """
    Verificar estado del servicio médico
    """
    if not assistantAI_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio médico no disponible - OPENROUTER_API_KEY no configurado"
        )
    
    return {
        "status": "healthy",
        "service": "assistantAI",
        "user": current_user.get("email", "Usuario"),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/enfermedad/{nombre}", response_model=EnfermedadResponse)
async def consultar_enfermedad(nombre: str, current_user: dict = Depends(verify_jwt_auth)):
    if not assistantAI_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio médico no disponible"
        )
    
    try:
        resultado = assistantAI_service.consultar_enfermedad(nombre)
        
        if "error" in resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado["error"]
            )
        
        return EnfermedadResponse(
            enfermedad=nombre,
            informacion=resultado["content"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error consultando enfermedad: {str(e)}"
        )

@router.post("/diagnostico", response_model=DiagnosticoResponse)
async def diagnosticar_sintomas(request: SintomasRequest, current_user: dict = Depends(verify_jwt_auth)):
    """
    Realizar diagnóstico basado en síntomas
    """
    if not assistantAI_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio médico no disponible"
        )
    
    if not request.sintomas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un síntoma"
        )
    
    try:
        resultado = assistantAI_service.diagnosticar_sintomas(
            sintomas=request.sintomas,
            edad=request.edad,
            genero=request.genero
        )
        
        if "error" in resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado["error"]
            )
        
        return DiagnosticoResponse(
            sintomas=request.sintomas,
            posibles_diagnosticos=resultado["content"],
            recomendaciones="Consulte con un médico profesional para un diagnóstico preciso",
            urgencia="Evaluar según síntomas presentados",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error realizando diagnóstico: {str(e)}"
        )

@router.post("/tratamiento", response_model=TratamientoResponse)
async def obtener_tratamiento(request: TratamientoRequest, current_user: dict = Depends(verify_jwt_auth)):
    """
    Obtener información sobre tratamientos para una enfermedad
    """
    if not assistantAI_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio médico no disponible"
        )
    
    try:
        resultado = assistantAI_service.obtener_tratamiento(
            enfermedad=request.enfermedad,
            severidad=request.severidad
        )
        
        if "error" in resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado["error"]
            )
        
        return TratamientoResponse(
            enfermedad=request.enfermedad,
            severidad=request.severidad,
            tratamientos=resultado["content"],
            recomendaciones="Consulte con un médico antes de iniciar cualquier tratamiento",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tratamiento: {str(e)}"
        )

@router.get("/medicamento/{nombre}", response_model=MedicamentoResponse)
async def analizar_medicamento(nombre: str, current_user: dict = Depends(verify_jwt_auth)):
    """
    Analizar información sobre un medicamento
    """
    if not assistantAI_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio médico no disponible"
        )
    
    try:
        resultado = assistantAI_service.analizar_medicamento(nombre)
        
        if "error" in resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado["error"]
            )
        
        return MedicamentoResponse(
            medicamento=nombre,
            informacion=resultado["content"],
            advertencias="Consulte con un médico o farmacéutico antes de usar cualquier medicamento",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analizando medicamento: {str(e)}"
        )

@router.post("/emergencia", response_model=EmergenciaResponse)
async def evaluar_emergencia(request: EmergenciaRequest, current_user: dict = Depends(verify_jwt_auth)):
    """
    Evaluar si los síntomas requieren atención médica urgente
    """
    if not assistantAI_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio médico no disponible"
        )
    
    if not request.sintomas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un síntoma"
        )
    
    try:
        resultado = assistantAI_service.emergencia_medica(request.sintomas)
        
        if "error" in resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado["error"]
            )
        
        return EmergenciaResponse(
            sintomas=request.sintomas,
            nivel_urgencia="Evaluar según recomendaciones",
            recomendaciones=resultado["content"],
            tiempo_atencion="Según nivel de urgencia",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluando emergencia: {str(e)}"
        )

@router.get("/")
async def assistantAI_info(current_user: dict = Depends(verify_jwt_auth)):
    """
    Información sobre los endpoints médicos disponibles
    """
    return {
        "service": "Medical AI Assistant",
        "description": "Servicio de diagnóstico médico con IA",
        "user": current_user.get("email", "Usuario"),
        "endpoints": {
            "health": "GET /assistantAI/health - Estado del servicio",
            "enfermedad": "GET /assistantAI/enfermedad/{nombre} - Información de enfermedad",
            "diagnostico": "POST /assistantAI/diagnostico - Diagnóstico por síntomas",
            "tratamiento": "POST /assistantAI/tratamiento - Información de tratamientos",
            "medicamento": "GET /assistantAI/medicamento/{nombre} - Información de medicamento",
            "emergencia": "POST /assistantAI/emergencia - Evaluación de urgencia"
        },
        "disclaimer": "Esta información es solo para orientación médica. Siempre consulte con un médico profesional.",
        "timestamp": datetime.now().isoformat()
    }
