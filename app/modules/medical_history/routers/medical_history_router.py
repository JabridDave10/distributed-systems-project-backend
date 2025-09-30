from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, verify_jwt_auth
from app.modules.medical_history.services.medical_history_service import MedicalHistoryService
from app.modules.medical_history.schemas.medical_history_dto import (
    MedicalHistoryCreate, 
    MedicalHistoryUpdate, 
    MedicalHistoryResponse
)

router = APIRouter(prefix="/medical-history", tags=["medical-history"])

@router.post("/create-medical-history", response_model=MedicalHistoryResponse)
async def create_medical_history(
    medical_data: MedicalHistoryCreate,
    current_user: dict = Depends(verify_jwt_auth),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo registro de historial médico
    """
    try:
        # Verificar que el usuario es un doctor
        if current_user.get("id_role") != 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los doctores pueden crear historiales médicos"
            )

        service = MedicalHistoryService(db)
        medical_history = service.create_medical_history(medical_data)
        
        return medical_history
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Error creando historial médico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/appointment/{appointment_id}", response_model=MedicalHistoryResponse)
async def get_medical_history_by_appointment(
    appointment_id: int,
    current_user: dict = Depends(verify_jwt_auth),
    db: Session = Depends(get_db)
):
    """
    Obtener historial médico por ID de cita
    """
    try:
        service = MedicalHistoryService(db)
        medical_history = service.get_medical_history_by_appointment(appointment_id)
        
        if not medical_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Historial médico no encontrado"
            )

        # Verificar permisos: doctor que lo creó, paciente de la cita, o admin
        if (current_user.get("id_role") == 3 or  # Admin
            current_user.get("id") == medical_history.id_doctor or  # Doctor que lo creó
            current_user.get("id") == medical_history.id_patient):  # Paciente
            return medical_history
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver este historial médico"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error obteniendo historial médico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/patient/{patient_id}", response_model=List[MedicalHistoryResponse])
async def get_medical_histories_by_patient(
    patient_id: int,
    current_user: dict = Depends(verify_jwt_auth),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los historiales médicos de un paciente
    """
    try:
        # Verificar permisos: el propio paciente, un doctor, o admin
        if (current_user.get("id_role") == 3 or  # Admin
            current_user.get("id_role") == 2 or  # Doctor
            current_user.get("id") == patient_id):  # El propio paciente
            service = MedicalHistoryService(db)
            medical_histories = service.get_medical_histories_by_patient(patient_id)
            return medical_histories
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver estos historiales médicos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error obteniendo historiales del paciente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/doctor/{doctor_id}", response_model=List[MedicalHistoryResponse])
async def get_medical_histories_by_doctor(
    doctor_id: int,
    current_user: dict = Depends(verify_jwt_auth),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los historiales médicos creados por un doctor
    """
    try:
        # Verificar permisos: el propio doctor o admin
        if (current_user.get("id_role") == 3 or  # Admin
            current_user.get("id") == doctor_id):  # El propio doctor
            service = MedicalHistoryService(db)
            medical_histories = service.get_medical_histories_by_doctor(doctor_id)
            return medical_histories
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver estos historiales médicos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error obteniendo historiales del doctor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{history_id}", response_model=MedicalHistoryResponse)
async def update_medical_history(
    history_id: int,
    update_data: MedicalHistoryUpdate,
    current_user: dict = Depends(verify_jwt_auth),
    db: Session = Depends(get_db)
):
    """
    Actualizar historial médico
    """
    try:
        # Verificar que el usuario es un doctor
        if current_user.get("id_role") != 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los doctores pueden actualizar historiales médicos"
            )

        service = MedicalHistoryService(db)
        medical_history = service.update_medical_history(
            history_id, 
            update_data, 
            current_user.get("id")
        )
        
        if not medical_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Historial médico no encontrado"
            )
        
        return medical_history
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error actualizando historial médico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{history_id}")
async def delete_medical_history(
    history_id: int,
    current_user: dict = Depends(verify_jwt_auth),
    db: Session = Depends(get_db)
):
    """
    Eliminar historial médico
    """
    try:
        # Verificar que el usuario es un doctor
        if current_user.get("id_role") != 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los doctores pueden eliminar historiales médicos"
            )

        service = MedicalHistoryService(db)
        success = service.delete_medical_history(history_id, current_user.get("id"))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Historial médico no encontrado"
            )
        
        return {"message": "Historial médico eliminado exitosamente"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando historial médico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
