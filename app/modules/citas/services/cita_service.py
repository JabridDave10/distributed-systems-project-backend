from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional
from app.modules.citas.models.cita import Cita
from app.modules.auth.models.user import User
from app.modules.citas.schemas.cita import CitaCreate, CitaOut

class CitaService:
    def __init__(self, db: Session):
        self.db = db

    def create_cita(self, cita_data: CitaCreate) -> Cita:
        """
        Crear una nueva cita en la base de datos

        Args:
            cita_data (CitaCreate): Datos de la cita a crear

        Returns:
            Cita: Cita creada

        Raises:
            ValueError: Si el paciente o doctor no existen o no son válidos
        """
        print(f"🚀 CITA_SERVICE: Creando nueva cita")
        print(f"📋 Datos: doctor={cita_data.id_doctor}, paciente={cita_data.id_paciente}, fecha={cita_data.fecha_hora}")

        # Verificar que el doctor existe y es realmente un doctor (id_role = 2)
        doctor = self.db.query(User).join(User.user_roles).filter(
            User.id_user == cita_data.id_doctor,
            User.id_status == True
        ).first()

        if not doctor:
            print(f"❌ CITA_SERVICE: Doctor con ID {cita_data.id_doctor} no encontrado")
            raise ValueError("Doctor no encontrado")

        # Verificar que el doctor tiene rol de doctor (id_role = 2)
        doctor_role = any(role.id_role == 2 for role in doctor.user_roles)
        if not doctor_role:
            print(f"❌ CITA_SERVICE: Usuario {cita_data.id_doctor} no es doctor")
            raise ValueError("El usuario especificado no es un doctor")

        # Verificar que el paciente existe y es realmente un paciente (id_role = 1)
        paciente = self.db.query(User).join(User.user_roles).filter(
            User.id_user == cita_data.id_paciente,
            User.id_status == True
        ).first()

        if not paciente:
            print(f"❌ CITA_SERVICE: Paciente con ID {cita_data.id_paciente} no encontrado")
            raise ValueError("Paciente no encontrado")

        # Verificar que el paciente tiene rol de paciente (id_role = 1)
        paciente_role = any(role.id_role == 1 for role in paciente.user_roles)
        if not paciente_role:
            print(f"❌ CITA_SERVICE: Usuario {cita_data.id_paciente} no es paciente")
            raise ValueError("El usuario especificado no es un paciente")

        # Verificar que no hay conflicto de horarios para el doctor
        conflicto_doctor = self.db.query(Cita).filter(
            Cita.id_doctor == cita_data.id_doctor,
            Cita.fecha_hora == cita_data.fecha_hora,
            Cita.estado.in_(["programada", "confirmada"])
        ).first()

        if conflicto_doctor:
            print(f"❌ CITA_SERVICE: Conflicto de horario para doctor en {cita_data.fecha_hora}")
            raise ValueError("El doctor ya tiene una cita programada en ese horario")

        # Crear la cita
        nueva_cita = Cita(
            id_paciente=cita_data.id_paciente,
            id_doctor=cita_data.id_doctor,
            fecha_hora=cita_data.fecha_hora,
            motivo=cita_data.motivo,
            estado=cita_data.estado or "programada"
        )

        print(f"💾 CITA_SERVICE: Guardando cita en base de datos")
        self.db.add(nueva_cita)
        self.db.commit()
        self.db.refresh(nueva_cita)

        print(f"✅ CITA_SERVICE: Cita creada exitosamente con ID {nueva_cita.id_cita}")
        return nueva_cita

    def get_all_citas(self) -> List[Cita]:
        """
        Obtener todas las citas

        Returns:
            List[Cita]: Lista de todas las citas
        """
        print(f"🔍 CITA_SERVICE: Obteniendo todas las citas")
        citas = self.db.query(Cita).all()
        print(f"✅ CITA_SERVICE: Encontradas {len(citas)} citas")
        return citas

    def get_cita_by_id(self, cita_id: int) -> Optional[Cita]:
        """
        Obtener una cita por ID

        Args:
            cita_id (int): ID de la cita

        Returns:
            Optional[Cita]: Cita encontrada o None
        """
        print(f"🔍 CITA_SERVICE: Buscando cita con ID {cita_id}")
        cita = self.db.query(Cita).filter(Cita.id_cita == cita_id).first()

        if cita:
            print(f"✅ CITA_SERVICE: Cita encontrada")
        else:
            print(f"❌ CITA_SERVICE: Cita no encontrada")

        return cita

    def get_citas_by_doctor(self, doctor_id: int) -> List[Cita]:
        """
        Obtener todas las citas de un doctor

        Args:
            doctor_id (int): ID del doctor

        Returns:
            List[Cita]: Lista de citas del doctor
        """
        print(f"🔍 CITA_SERVICE: Obteniendo citas del doctor {doctor_id}")
        citas = self.db.query(Cita).filter(Cita.id_doctor == doctor_id).all()
        print(f"✅ CITA_SERVICE: Encontradas {len(citas)} citas para el doctor")
        return citas

    def get_citas_by_paciente(self, paciente_id: int) -> List[Cita]:
        """
        Obtener todas las citas de un paciente

        Args:
            paciente_id (int): ID del paciente

        Returns:
            List[Cita]: Lista de citas del paciente
        """
        print(f"🔍 CITA_SERVICE: Obteniendo citas del paciente {paciente_id}")
        citas = self.db.query(Cita).filter(Cita.id_paciente == paciente_id).all()
        print(f"✅ CITA_SERVICE: Encontradas {len(citas)} citas para el paciente")
        return citas

    def update_cita_estado(self, cita_id: int, nuevo_estado: str) -> Optional[Cita]:
        """
        Actualizar el estado de una cita

        Args:
            cita_id (int): ID de la cita
            nuevo_estado (str): Nuevo estado

        Returns:
            Optional[Cita]: Cita actualizada o None si no se encontró
        """
        print(f"🔄 CITA_SERVICE: Actualizando estado de cita {cita_id} a '{nuevo_estado}'")

        cita = self.db.query(Cita).filter(Cita.id_cita == cita_id).first()
        if not cita:
            print(f"❌ CITA_SERVICE: Cita {cita_id} no encontrada")
            return None

        cita.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(cita)

        print(f"✅ CITA_SERVICE: Estado actualizado exitosamente")
        return cita

    def delete_cita(self, cita_id: int) -> bool:
        """
        Eliminar una cita

        Args:
            cita_id (int): ID de la cita

        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        print(f"🗑️ CITA_SERVICE: Eliminando cita {cita_id}")

        cita = self.db.query(Cita).filter(Cita.id_cita == cita_id).first()
        if not cita:
            print(f"❌ CITA_SERVICE: Cita {cita_id} no encontrada")
            return False

        self.db.delete(cita)
        self.db.commit()

        print(f"✅ CITA_SERVICE: Cita eliminada exitosamente")
        return True