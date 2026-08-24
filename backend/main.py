from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    DerivacionCrear,
    DerivacionRespuesta,
    EstadoDerivacion,
    HistorialDerivacionRespuesta,
    PacienteCrear,
    PacienteRespuesta,
)
from backend.orm_models import Derivacion, HistorialDerivacion, Paciente


app = FastAPI(
    title="HealthBridge API",
    description="API para gestión y trazabilidad de derivaciones clínicas.",
    version="0.1.0"
)


def confirmar_cambios(db: Session, detalle_error: str, codigo_error: int) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=codigo_error, detail=detalle_error) from error


@app.get("/")
def inicio():
    return {
        "aplicacion": "HealthBridge",
        "estado": "Funcionando"
    }


@app.post(
    "/pacientes",
    response_model=PacienteRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_paciente(paciente_nuevo: PacienteCrear, db: Session = Depends(get_db)):
    paciente_existente = db.scalar(
        select(Paciente).where(Paciente.rut == paciente_nuevo.rut)
    )
    if paciente_existente is not None:
        raise HTTPException(status_code=409, detail="El RUT ya está registrado.")

    paciente = Paciente(
        rut=paciente_nuevo.rut,
        nombre=paciente_nuevo.nombre,
        fecha_nacimiento=paciente_nuevo.fecha_nacimiento,
        sexo=paciente_nuevo.sexo,
    )
    db.add(paciente)
    confirmar_cambios(db, "El RUT ya está registrado.", status.HTTP_409_CONFLICT)
    db.refresh(paciente)
    return paciente


@app.get("/pacientes", response_model=list[PacienteRespuesta])
def listar_pacientes(db: Session = Depends(get_db)):
    return db.scalars(select(Paciente).order_by(Paciente.id)).all()


@app.get("/pacientes/{paciente_id}", response_model=PacienteRespuesta)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.get(Paciente, paciente_id)
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    return paciente


@app.get("/derivaciones", response_model=list[DerivacionRespuesta])
def listar_derivaciones(db: Session = Depends(get_db)):
    return db.scalars(select(Derivacion).order_by(Derivacion.id)).all()


@app.post(
    "/derivaciones",
    response_model=DerivacionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_derivacion(
    nueva_derivacion: DerivacionCrear,
    db: Session = Depends(get_db),
):
    paciente = db.scalar(
        select(Paciente).where(Paciente.rut == nueva_derivacion.paciente_rut)
    )
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    derivacion = Derivacion(
        paciente_id=paciente.id,
        especialidad=nueva_derivacion.especialidad,
        motivo=nueva_derivacion.motivo,
        prioridad=nueva_derivacion.prioridad,
        estado="Pendiente",
        responsable=nueva_derivacion.responsable,
        observaciones=nueva_derivacion.observaciones,
    )
    db.add(derivacion)
    confirmar_cambios(
        db,
        "No fue posible guardar la derivación.",
        status.HTTP_400_BAD_REQUEST,
    )
    db.refresh(derivacion)
    return derivacion


@app.get("/derivaciones/{derivacion_id}", response_model=DerivacionRespuesta)
def obtener_derivacion(derivacion_id: int, db: Session = Depends(get_db)):
    derivacion = db.get(Derivacion, derivacion_id)
    if derivacion is None:
        raise HTTPException(status_code=404, detail="Derivación no encontrada.")

    return derivacion


@app.patch(
    "/derivaciones/{derivacion_id}/estado",
    response_model=DerivacionRespuesta,
)
def actualizar_estado_derivacion(
    derivacion_id: int,
    estado_actualizado: EstadoDerivacion,
    db: Session = Depends(get_db),
):
    derivacion = db.get(Derivacion, derivacion_id)
    if derivacion is None:
        raise HTTPException(status_code=404, detail="Derivación no encontrada.")

    historial = HistorialDerivacion(
        derivacion_id=derivacion.id,
        estado_anterior=derivacion.estado,
        estado_nuevo=estado_actualizado.estado,
    )
    db.add(historial)
    derivacion.estado = estado_actualizado.estado

    confirmar_cambios(
        db,
        "No fue posible actualizar el estado de la derivación.",
        status.HTTP_400_BAD_REQUEST,
    )
    db.refresh(derivacion)
    return derivacion


@app.get(
    "/derivaciones/{derivacion_id}/historial",
    response_model=list[HistorialDerivacionRespuesta],
)
def listar_historial_derivacion(
    derivacion_id: int,
    db: Session = Depends(get_db),
):
    derivacion = db.get(Derivacion, derivacion_id)
    if derivacion is None:
        raise HTTPException(status_code=404, detail="Derivación no encontrada.")

    return db.scalars(
        select(HistorialDerivacion)
        .where(HistorialDerivacion.derivacion_id == derivacion_id)
        .order_by(HistorialDerivacion.fecha_cambio, HistorialDerivacion.id)
    ).all()
