from backend.copilot.guardrails import validar_campos_anonimizados
from backend.copilot.schemas import AnalisisDerivacion, DerivacionAnonimizada


CAMPOS_REQUERIDOS = (
    "especialidad",
    "motivo",
    "prioridad_actual",
    "responsable",
    "observaciones",
)


def analizar_derivacion(derivacion: DerivacionAnonimizada) -> AnalisisDerivacion:
    """Genera una sugerencia administrativa sin efectos secundarios."""
    validar_campos_anonimizados(derivacion.model_dump().keys())

    datos_faltantes = _detectar_datos_faltantes(derivacion)
    prioridad_sugerida = derivacion.prioridad_actual or "Media"

    return AnalisisDerivacion(
        resumen=_crear_resumen(derivacion),
        datos_faltantes=datos_faltantes,
        calidad_datos=_calcular_calidad_datos(datos_faltantes),
        prioridad_sugerida=prioridad_sugerida,
        justificacion=_crear_justificacion(
            derivacion,
            datos_faltantes,
            prioridad_sugerida,
        ),
        incertidumbre=_crear_incertidumbre(derivacion, datos_faltantes),
        limitacion=(
            "Apoyo administrativo de solo lectura; no diagnostica, prescribe "
            "ni modifica la derivación."
        ),
        requiere_revision_humana=True,
    )


def _detectar_datos_faltantes(derivacion: DerivacionAnonimizada) -> list[str]:
    return [
        campo
        for campo in CAMPOS_REQUERIDOS
        if _es_valor_faltante(getattr(derivacion, campo))
    ]


def _es_valor_faltante(valor: str | None) -> bool:
    return valor is None or not valor.strip()


def _calcular_calidad_datos(datos_faltantes: list[str]) -> str:
    if len(datos_faltantes) >= 3:
        return "Insuficiente"
    if datos_faltantes:
        return "Incompleta"
    return "Completa"


def _crear_resumen(derivacion: DerivacionAnonimizada) -> str:
    especialidad = derivacion.especialidad or "especialidad no registrada"
    estado = derivacion.estado or "estado no registrado"
    prioridad = derivacion.prioridad_actual or "prioridad no registrada"
    responsable = derivacion.responsable or "responsable no registrado"
    fecha_limite = (
        derivacion.fecha_limite.isoformat()
        if derivacion.fecha_limite is not None
        else "no registrada"
    )

    return (
        f"Derivación administrativa para {especialidad}; estado: {estado}; "
        f"prioridad registrada: {prioridad}; responsable: {responsable}; "
        f"fecha límite: {fecha_limite}."
    )


def _crear_justificacion(
    derivacion: DerivacionAnonimizada,
    datos_faltantes: list[str],
    prioridad_sugerida: str,
) -> str:
    if derivacion.prioridad_actual is None:
        partes = [
            "No hay prioridad registrada; se propone Media como marcador "
            "administrativo provisional."
        ]
    else:
        partes = [
            f"Se conserva la prioridad registrada: {prioridad_sugerida}."
        ]

    if derivacion.atrasada:
        partes.append(
            "La fecha límite figura vencida y requiere revisión administrativa."
        )
    elif derivacion.fecha_limite is None:
        partes.append(
            "No hay fecha límite registrada; puede completarse si el proceso "
            "administrativo lo requiere."
        )

    if datos_faltantes:
        partes.append(f"Datos pendientes de completar: {', '.join(datos_faltantes)}.")

    partes.append("Esta sugerencia no evalúa gravedad ni urgencia clínica.")
    return " ".join(partes)


def _crear_incertidumbre(
    derivacion: DerivacionAnonimizada,
    datos_faltantes: list[str],
) -> str:
    if len(datos_faltantes) >= 3:
        return "Alta: faltan varios datos administrativos para una revisión completa."
    if derivacion.atrasada or datos_faltantes:
        return (
            "Media: la sugerencia usa información administrativa disponible y "
            "requiere confirmación humana."
        )
    return (
        "Baja: los datos administrativos están completos, pero la prioridad "
        "sugerida sigue requiriendo revisión humana."
    )
