from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.copilot.schemas import AnalisisDerivacion, DerivacionAnonimizada
from backend.database import get_db
from backend.orm_models import Derivacion
from backend.services.derivaciones import expresion_atrasada
from backend.services.referral_copilot import analizar_derivacion


router = APIRouter(tags=["Referral Copilot"])


@router.post(
    "/derivaciones/{derivacion_id}/copilot/analizar",
    response_model=AnalisisDerivacion,
)
def analizar_derivacion_copilot(
    derivacion_id: int,
    db: Session = Depends(get_db),
):
    resultado = db.execute(
        select(Derivacion, expresion_atrasada().label("atrasada"))
        .where(Derivacion.id == derivacion_id)
    ).one_or_none()

    if resultado is None:
        raise HTTPException(status_code=404, detail="Derivación no encontrada.")

    derivacion, atrasada = resultado
    entrada = DerivacionAnonimizada(
        especialidad=derivacion.especialidad,
        motivo=derivacion.motivo,
        prioridad_actual=derivacion.prioridad,
        estado=derivacion.estado,
        responsable=derivacion.responsable,
        observaciones=derivacion.observaciones,
        fecha_creacion=derivacion.fecha_creacion,
        fecha_limite=derivacion.fecha_limite,
        atrasada=bool(atrasada),
    )

    return analizar_derivacion(entrada)
