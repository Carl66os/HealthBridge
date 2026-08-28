from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    DerivacionCrear,
    DerivacionRespuesta,
    EstadoDerivacion,
    EstadoPermitido,
    HistorialDerivacionRespuesta,
    IndicadoresRespuesta,
    PacienteCrear,
    PacienteRespuesta,
    PrioridadDerivacion,
)
from backend.orm_models import Derivacion, HistorialDerivacion, Paciente
from backend.routers.copilot import router as copilot_router
from backend.services.derivaciones import condicion_atrasada, expresion_atrasada


app = FastAPI(
    title="HealthBridge API",
    description="API para gestión y trazabilidad de derivaciones clínicas.",
    version="0.1.0"
)
app.include_router(copilot_router)


def confirmar_cambios(db: Session, detalle_error: str, codigo_error: int) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=codigo_error, detail=detalle_error) from error


def crear_respuesta_derivacion(
    derivacion: Derivacion,
    atrasada: bool,
) -> DerivacionRespuesta:
    return DerivacionRespuesta.model_validate(
        {
            "id": derivacion.id,
            "paciente_id": derivacion.paciente_id,
            "especialidad": derivacion.especialidad,
            "motivo": derivacion.motivo,
            "prioridad": derivacion.prioridad,
            "estado": derivacion.estado,
            "responsable": derivacion.responsable,
            "observaciones": derivacion.observaciones,
            "fecha_creacion": derivacion.fecha_creacion,
            "fecha_limite": derivacion.fecha_limite,
            "atrasada": bool(atrasada),
        }
    )


def obtener_derivacion_con_atrasada(
    db: Session,
    derivacion_id: int,
) -> tuple[Derivacion, bool] | None:
    resultado = db.execute(
        select(Derivacion, expresion_atrasada().label("atrasada"))
        .where(Derivacion.id == derivacion_id)
    ).one_or_none()

    if resultado is None:
        return None

    return resultado[0], bool(resultado[1])


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
def listar_derivaciones(
    estado: EstadoPermitido | None = None,
    prioridad: PrioridadDerivacion | None = None,
    especialidad: str | None = None,
    paciente_rut: str | None = None,
    atrasada: bool | None = None,
    db: Session = Depends(get_db),
):
    condicion = condicion_atrasada()
    consulta = select(Derivacion, expresion_atrasada().label("atrasada"))

    if estado is not None:
        consulta = consulta.where(Derivacion.estado == estado)
    if prioridad is not None:
        consulta = consulta.where(Derivacion.prioridad == prioridad)
    if especialidad is not None:
        consulta = consulta.where(Derivacion.especialidad == especialidad)
    if paciente_rut is not None:
        consulta = consulta.join(Paciente).where(Paciente.rut == paciente_rut)
    if atrasada is True:
        consulta = consulta.where(condicion)
    elif atrasada is False:
        consulta = consulta.where(~condicion)

    resultados = db.execute(consulta.order_by(Derivacion.id)).all()
    return [
        crear_respuesta_derivacion(derivacion, es_atrasada)
        for derivacion, es_atrasada in resultados
    ]


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
        fecha_limite=nueva_derivacion.fecha_limite,
    )
    db.add(derivacion)
    confirmar_cambios(
        db,
        "No fue posible guardar la derivación.",
        status.HTTP_400_BAD_REQUEST,
    )
    db.refresh(derivacion)

    derivacion_con_atrasada = obtener_derivacion_con_atrasada(db, derivacion.id)
    if derivacion_con_atrasada is None:
        raise HTTPException(status_code=500, detail="No fue posible leer la derivación.")

    return crear_respuesta_derivacion(*derivacion_con_atrasada)


@app.get("/derivaciones/{derivacion_id}", response_model=DerivacionRespuesta)
def obtener_derivacion(derivacion_id: int, db: Session = Depends(get_db)):
    derivacion_con_atrasada = obtener_derivacion_con_atrasada(db, derivacion_id)
    if derivacion_con_atrasada is None:
        raise HTTPException(status_code=404, detail="Derivación no encontrada.")

    return crear_respuesta_derivacion(*derivacion_con_atrasada)


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

    derivacion_con_atrasada = obtener_derivacion_con_atrasada(db, derivacion_id)
    if derivacion_con_atrasada is None:
        raise HTTPException(status_code=500, detail="No fue posible leer la derivación.")

    return crear_respuesta_derivacion(*derivacion_con_atrasada)


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


@app.get("/indicadores", response_model=IndicadoresRespuesta)
def obtener_indicadores(db: Session = Depends(get_db)):
    resultado = db.execute(
        select(
            func.count(Derivacion.id).label("total_derivaciones"),
            func.count(Derivacion.id)
            .filter(Derivacion.estado == "Pendiente")
            .label("pendientes"),
            func.count(Derivacion.id)
            .filter(Derivacion.estado == "En revisión")
            .label("en_revision"),
            func.count(Derivacion.id)
            .filter(Derivacion.estado == "Agendada")
            .label("agendadas"),
            func.count(Derivacion.id)
            .filter(Derivacion.estado == "Atendida")
            .label("atendidas"),
            func.count(Derivacion.id)
            .filter(Derivacion.estado == "Cerrada")
            .label("cerradas"),
            func.count(Derivacion.id)
            .filter(Derivacion.estado == "Cancelada")
            .label("canceladas"),
            func.count(Derivacion.id)
            .filter(Derivacion.prioridad == "Alta")
            .label("prioridad_alta"),
            func.count(Derivacion.id)
            .filter(condicion_atrasada())
            .label("atrasadas"),
        )
    ).one()

    return IndicadoresRespuesta(**resultado._mapping)
