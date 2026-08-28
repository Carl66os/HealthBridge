from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from backend.copilot.guardrails import CAMPOS_IDENTIFICATORIOS_PROHIBIDOS
from backend.copilot.schemas import AnalisisDerivacion, DerivacionAnonimizada
from backend.services.referral_copilot import analizar_derivacion


def crear_derivacion_completa(**cambios) -> DerivacionAnonimizada:
    datos = {
        "especialidad": "Cardiología",
        "motivo": "Control administrativo ficticio",
        "prioridad_actual": "Alta",
        "estado": "Pendiente",
        "responsable": "Unidad ficticia",
        "observaciones": "Información completa",
        "fecha_creacion": datetime(2026, 8, 1, tzinfo=timezone.utc),
        "fecha_limite": datetime(2026, 9, 1, tzinfo=timezone.utc),
        "atrasada": False,
    }
    datos.update(cambios)
    return DerivacionAnonimizada.model_validate(datos)


def test_analiza_una_derivacion_completa():
    analisis = analizar_derivacion(crear_derivacion_completa())

    assert analisis.calidad_datos == "Completa"
    assert analisis.datos_faltantes == []
    assert analisis.prioridad_sugerida == "Alta"
    assert "Cardiología" in analisis.resumen
    assert "no evalúa gravedad ni urgencia clínica" in analisis.justificacion
    assert "no diagnostica" in analisis.limitacion


def test_reporta_datos_faltantes_e_incertidumbre_alta():
    analisis = analizar_derivacion(
        crear_derivacion_completa(
            especialidad="",
            motivo=None,
            prioridad_actual=None,
            responsable=" ",
            observaciones=None,
            fecha_limite=None,
        )
    )

    assert analisis.calidad_datos == "Insuficiente"
    assert analisis.prioridad_sugerida == "Media"
    assert "especialidad" in analisis.datos_faltantes
    assert "fecha_limite (opcional)" in analisis.datos_faltantes
    assert analisis.incertidumbre.startswith("Alta:")


def test_alerta_fecha_limite_vencida_sin_cambiar_prioridad():
    analisis = analizar_derivacion(
        crear_derivacion_completa(
            prioridad_actual="Baja",
            fecha_limite=datetime.now(timezone.utc) - timedelta(days=1),
            atrasada=True,
        )
    )

    assert analisis.prioridad_sugerida == "Baja"
    assert "fecha límite figura vencida" in analisis.justificacion
    assert analisis.incertidumbre.startswith("Media:")


@pytest.mark.parametrize("atrasada", [True, False])
def test_siempre_requiere_revision_humana(atrasada):
    analisis = analizar_derivacion(crear_derivacion_completa(atrasada=atrasada))

    assert analisis.requiere_revision_humana is True


def test_contrato_no_acepta_ni_expone_campos_identificatorios():
    campos_entrada = set(DerivacionAnonimizada.model_fields)
    campos_salida = set(AnalisisDerivacion.model_fields)

    assert not (campos_entrada & CAMPOS_IDENTIFICATORIOS_PROHIBIDOS)
    assert not (campos_salida & CAMPOS_IDENTIFICATORIOS_PROHIBIDOS)

    with pytest.raises(ValidationError):
        crear_derivacion_completa(rut="11.111.111-1")
