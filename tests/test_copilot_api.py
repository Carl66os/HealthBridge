import json

from sqlalchemy import func, select

from backend.orm_models import Derivacion, HistorialDerivacion


def obtener_derivacion_pendiente(test_db) -> Derivacion:
    with test_db() as db:
        return db.scalar(
            select(Derivacion).where(Derivacion.estado == "Pendiente")
        )


def test_copilot_analiza_derivacion_existente_sin_exponer_identificadores(
    client_con_datos,
    test_db,
):
    derivacion = obtener_derivacion_pendiente(test_db)

    response = client_con_datos.post(
        f"/derivaciones/{derivacion.id}/copilot/analizar"
    )

    assert response.status_code == 200
    respuesta = response.json()
    contenido = json.dumps(respuesta)

    assert respuesta["requiere_revision_humana"] is True
    assert respuesta["prioridad_sugerida"] == "Alta"
    assert "fecha límite figura vencida" in respuesta["justificacion"]
    assert "rut" not in respuesta
    assert "nombre" not in respuesta
    assert "paciente_id" not in respuesta
    assert "11.111.111-1" not in contenido
    assert "Paciente Ficticio" not in contenido


def test_copilot_devuelve_404_para_derivacion_inexistente(client_con_datos):
    response = client_con_datos.post("/derivaciones/999/copilot/analizar")

    assert response.status_code == 404
    assert response.json() == {"detail": "Derivación no encontrada."}


def test_copilot_no_modifica_derivacion_ni_historial(client_con_datos, test_db):
    derivacion_antes = obtener_derivacion_pendiente(test_db)
    estado_antes = derivacion_antes.estado
    prioridad_antes = derivacion_antes.prioridad

    with test_db() as db:
        historial_antes = db.scalar(select(func.count(HistorialDerivacion.id)))

    response = client_con_datos.post(
        f"/derivaciones/{derivacion_antes.id}/copilot/analizar"
    )

    assert response.status_code == 200

    with test_db() as db:
        derivacion_despues = db.get(Derivacion, derivacion_antes.id)
        historial_despues = db.scalar(select(func.count(HistorialDerivacion.id)))

    assert derivacion_despues.estado == estado_antes
    assert derivacion_despues.prioridad == prioridad_antes
    assert historial_despues == historial_antes
