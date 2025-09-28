from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SintomasRequest(BaseModel):
    sintomas: List[str] = Field(..., description="Lista de síntomas presentados")
    edad: Optional[int] = Field(None, ge=0, le=120, description="Edad del paciente")
    genero: Optional[str] = Field(None, description="Género del paciente")

class TratamientoRequest(BaseModel):
    enfermedad: str = Field(..., description="Nombre de la enfermedad")
    severidad: str = Field("moderada", description="Severidad: leve, moderada, severa")

class EmergenciaRequest(BaseModel):
    sintomas: List[str] = Field(..., description="Lista de síntomas para evaluar urgencia")

class EnfermedadResponse(BaseModel):
    enfermedad: str
    informacion: str
    timestamp: str

class DiagnosticoResponse(BaseModel):
    sintomas: List[str]
    posibles_diagnosticos: str
    recomendaciones: str
    urgencia: str
    timestamp: str

class TratamientoResponse(BaseModel):
    enfermedad: str
    severidad: str
    tratamientos: str
    recomendaciones: str
    timestamp: str

class MedicamentoResponse(BaseModel):
    medicamento: str
    informacion: str
    advertencias: str
    timestamp: str

class EmergenciaResponse(BaseModel):
    sintomas: List[str]
    nivel_urgencia: str
    recomendaciones: str
    tiempo_atencion: str
    timestamp: str

class ErrorResponse(BaseModel):
    error: str
    detalles: Optional[str] = None
    timestamp: str
