from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PacienteCrear(BaseModel):
    rut: str
    nombre: str
    fecha_nacimiento: date | None = None
    sexo: str | None = None


class PacienteRespuesta(BaseModel):
    id: int
    rut: str
    nombre: str
    fecha_nacimiento: date | None
    sexo: str | None
    activo: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DerivacionCrear(BaseModel):
    paciente_rut: str
    especialidad: str
    motivo: str
    prioridad: Literal["Alta", "Media", "Baja"]
    responsable: str
    observaciones: str = "Sin observaciones"


class DerivacionRespuesta(BaseModel):
    id: int
    paciente_id: int
    especialidad: str
    motivo: str
    prioridad: str
    estado: str
    responsable: str
    observaciones: str | None
    fecha_creacion: datetime
    fecha_limite: datetime | None

    model_config = ConfigDict(from_attributes=True)


class EstadoDerivacion(BaseModel):
    estado: Literal[
        "Pendiente",
        "En revisión",
        "Agendada",
        "Atendida",
        "Cerrada",
        "Cancelada"
    ]


class HistorialDerivacionRespuesta(BaseModel):
    id: int
    derivacion_id: int
    estado_anterior: str | None
    estado_nuevo: str
    fecha_cambio: datetime

    model_config = ConfigDict(from_attributes=True)
