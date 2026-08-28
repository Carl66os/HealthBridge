from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


PrioridadDerivacion = Literal["Alta", "Media", "Baja"]
EstadoPermitido = Literal[
    "Pendiente",
    "En revisión",
    "Agendada",
    "Atendida",
    "Cerrada",
    "Cancelada",
]


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
    prioridad: PrioridadDerivacion
    responsable: str
    observaciones: str = "Sin observaciones"
    fecha_limite: datetime | None = None


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
    atrasada: bool

    model_config = ConfigDict(from_attributes=True)


class EstadoDerivacion(BaseModel):
    estado: EstadoPermitido


class HistorialDerivacionRespuesta(BaseModel):
    id: int
    derivacion_id: int
    estado_anterior: str | None
    estado_nuevo: str
    fecha_cambio: datetime

    model_config = ConfigDict(from_attributes=True)


class IndicadoresRespuesta(BaseModel):
    total_derivaciones: int
    pendientes: int
    en_revision: int
    agendadas: int
    atendidas: int
    cerradas: int
    canceladas: int
    prioridad_alta: int
    atrasadas: int
