from collections.abc import Iterable


CAMPOS_PERMITIDOS = frozenset(
    {
        "especialidad",
        "motivo",
        "prioridad_actual",
        "estado",
        "responsable",
        "observaciones",
        "fecha_creacion",
        "fecha_limite",
        "atrasada",
    }
)

CAMPOS_IDENTIFICATORIOS_PROHIBIDOS = frozenset(
    {
        "rut",
        "nombre",
        "paciente_id",
        "fecha_nacimiento",
        "sexo",
        "secretos",
        "credenciales",
        "env",
    }
)


def validar_campos_anonimizados(campos: Iterable[str]) -> None:
    campos_recibidos = set(campos)
    campos_no_permitidos = campos_recibidos - CAMPOS_PERMITIDOS

    if campos_no_permitidos:
        nombres = ", ".join(sorted(campos_no_permitidos))
        raise ValueError(f"La entrada contiene campos no permitidos: {nombres}.")
