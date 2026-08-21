from fastapi import FastAPI, HTTPException

from backend.data import derivaciones
from backend.models import DerivacionCrear, EstadoDerivacion


app = FastAPI(
    title="HealthBridge API",
    description="API para gestión y trazabilidad de derivaciones clínicas.",
    version="0.1.0"
)


@app.get("/")
def inicio():
    return {
        "aplicacion": "HealthBridge",
        "estado": "Funcionando"
    }


@app.get("/derivaciones")
def listar_derivaciones():
    return derivaciones


@app.post("/derivaciones")
def crear_derivacion(nueva_derivacion: DerivacionCrear):
    derivacion = {
        "id": len(derivaciones) + 1,
        "paciente_rut": nueva_derivacion.paciente_rut,
        "especialidad": nueva_derivacion.especialidad,
        "motivo": nueva_derivacion.motivo,
        "prioridad": nueva_derivacion.prioridad,
        "estado": "Pendiente",
        "responsable": nueva_derivacion.responsable,
        "observaciones": nueva_derivacion.observaciones
    }

    derivaciones.append(derivacion)

    return derivacion


@app.get("/derivaciones/{derivacion_id}")
def obtener_derivacion(derivacion_id: int):
    for derivacion in derivaciones:
        if derivacion["id"] == derivacion_id:
            return derivacion

    raise HTTPException(status_code=404, detail="Derivación no encontrada")


@app.patch("/derivaciones/{derivacion_id}/estado")
def actualizar_estado_derivacion(
    derivacion_id: int,
    estado_actualizado: EstadoDerivacion
):
    for derivacion in derivaciones:
        if derivacion["id"] == derivacion_id:
            derivacion["estado"] = estado_actualizado.estado
            return derivacion

    raise HTTPException(status_code=404, detail="Derivación no encontrada")
