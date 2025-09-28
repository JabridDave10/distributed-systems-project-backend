from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MedicalHistoryCreate(BaseModel):
    id_patient: int
    id_doctor: int
    id_appointment: int
    diagnosis: str = Field(..., min_length=1, description="Diagnóstico del paciente")
    treatment: str = Field(..., min_length=1, description="Tratamiento prescrito")
    medication: Optional[str] = Field(None, description="Medicación prescrita")
    symptoms: str = Field(..., min_length=1, description="Síntomas presentados")
    notes: Optional[str] = Field(None, description="Notas adicionales")

class MedicalHistoryUpdate(BaseModel):
    diagnosis: Optional[str] = Field(None, min_length=1, description="Diagnóstico del paciente")
    treatment: Optional[str] = Field(None, min_length=1, description="Tratamiento prescrito")
    medication: Optional[str] = Field(None, description="Medicación prescrita")
    symptoms: Optional[str] = Field(None, min_length=1, description="Síntomas presentados")
    notes: Optional[str] = Field(None, description="Notas adicionales")

class MedicalHistoryResponse(BaseModel):
    id_medical_history: int
    id_patient: int
    id_doctor: int
    id_appointment: int
    diagnosis: str
    treatment: str
    medication: Optional[str]
    symptoms: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
