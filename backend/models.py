from typing import Literal

from pydantic import BaseModel


class DerivacionCrear(BaseModel):
    paciente_rut: str
    especialidad: str
    motivo: str
    prioridad: Literal["Alta", "Media", "Baja"]
    responsable: str
    observaciones: str = "Sin observaciones"


class EstadoDerivacion(BaseModel):
    estado: Literal[
        "Pendiente",
        "En revisión",
        "Agendada",
        "Atendida",
        "Cerrada",
        "Cancelada"
    ]
