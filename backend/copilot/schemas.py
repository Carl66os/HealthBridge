from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


PrioridadSugerida = Literal["Alta", "Media", "Baja"]
CalidadDatos = Literal["Completa", "Incompleta", "Insuficiente"]


class DerivacionAnonimizada(BaseModel):
    """Datos administrativos permitidos para el análisis interno."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    especialidad: str | None = None
    motivo: str | None = None
    prioridad_actual: PrioridadSugerida | None = None
    estado: str | None = None
    responsable: str | None = None
    observaciones: str | None = None
    fecha_creacion: datetime | None = None
    fecha_limite: datetime | None = None
    atrasada: bool


class AnalisisDerivacion(BaseModel):
    """Salida administrativa que siempre requiere revisión humana."""

    resumen: str
    datos_faltantes: list[str]
    calidad_datos: CalidadDatos
    prioridad_sugerida: PrioridadSugerida
    justificacion: str
    incertidumbre: str
    limitacion: str
    requiere_revision_humana: Literal[True] = True
