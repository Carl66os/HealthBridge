"""Carga datos ficticios en una base SQLite local exclusiva para demostraciones."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

# Evita que las importaciones del backend consulten el archivo .env local.
os.environ["HEALTHBRIDGE_TESTING"] = "1"
os.environ.setdefault("DB_HOST", "demo-host-no-usado")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "healthbridge_demo_no_usado")
os.environ.setdefault("DB_USER", "demo-user-no-usado")
os.environ.setdefault("DB_PASSWORD", "demo-password-no-usado")

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.orm_models import Derivacion, HistorialDerivacion, Paciente


URL_DEMO_LOCAL = "sqlite:///./healthbridge_demo.db"
NOMBRE_ARCHIVO_DEMO = "healthbridge_demo.db"


class BaseDemoNoSeguraError(ValueError):
    """Se intentó usar una base distinta de la SQLite demo autorizada."""


class BaseDemoConDatosError(RuntimeError):
    """La base demo ya tiene datos y la semilla no debe duplicarlos."""


def ruta_base_demo_segura(url: str = URL_DEMO_LOCAL) -> Path:
    """Valida la única URL admitida y devuelve su ruta local absoluta."""
    if url != URL_DEMO_LOCAL:
        raise BaseDemoNoSeguraError(
            "Solo se permite sqlite:///./healthbridge_demo.db; "
            "se rechazan PostgreSQL, URLs externas y otros archivos."
        )

    return (Path.cwd() / NOMBRE_ARCHIVO_DEMO).resolve()


def eliminar_base_demo(url: str = URL_DEMO_LOCAL) -> None:
    """Elimina exclusivamente el archivo SQLite demo autorizado."""
    ruta_base_demo_segura(url).unlink(missing_ok=True)


def aplicar_migraciones_demo(url: str = URL_DEMO_LOCAL) -> None:
    """Lleva la base SQLite demo al último esquema mediante Alembic."""
    ruta_base_demo_segura(url)
    configuracion = Config(str(RAIZ_PROYECTO / "alembic.ini"))
    configuracion.set_main_option("script_location", str(RAIZ_PROYECTO / "alembic"))
    configuracion.set_main_option("sqlalchemy.url", url)
    command.upgrade(configuracion, "head")


def base_demo_tiene_datos(db: Session) -> bool:
    """Indica si ya existe cualquier entidad de demostración persistida."""
    return any(
        db.scalar(select(func.count(modelo.id))) > 0
        for modelo in (Paciente, Derivacion, HistorialDerivacion)
    )


def cargar_datos_demo(url: str = URL_DEMO_LOCAL) -> dict[str, int]:
    """Aplica migraciones y carga un conjunto consistente de datos ficticios."""
    ruta_base_demo_segura(url)
    aplicar_migraciones_demo(url)

    motor = create_engine(url)
    try:
        with Session(motor) as db:
            if base_demo_tiene_datos(db):
                raise BaseDemoConDatosError(
                    "La base demo ya contiene datos. Usa --reset solo para "
                    "regenerar healthbridge_demo.db."
                )

            ahora = datetime.now(timezone.utc)
            pacientes = [
                Paciente(
                    rut="DEMO-RUT-001",
                    nombre="Paciente demo A",
                    created_at=ahora,
                ),
                Paciente(
                    rut="DEMO-RUT-002",
                    nombre="Paciente demo B",
                    created_at=ahora,
                ),
                Paciente(
                    rut="DEMO-RUT-003",
                    nombre="Paciente demo C",
                    created_at=ahora,
                ),
            ]
            db.add_all(pacientes)
            db.flush()

            derivaciones = [
                Derivacion(
                    paciente_id=pacientes[0].id,
                    especialidad="Cardiología",
                    motivo="Seguimiento administrativo ficticio",
                    prioridad="Alta",
                    estado="Pendiente",
                    responsable="Coordinación Norte",
                    observaciones="Revisión de plazo pendiente.",
                    fecha_creacion=ahora - timedelta(days=12),
                    fecha_limite=ahora - timedelta(days=2),
                ),
                Derivacion(
                    paciente_id=pacientes[1].id,
                    especialidad="Traumatología",
                    motivo="Agenda de atención ficticia",
                    prioridad="Media",
                    estado="En revisión",
                    responsable="Unidad de Derivaciones",
                    observaciones="Documentación administrativa recibida.",
                    fecha_creacion=ahora - timedelta(days=8),
                    fecha_limite=ahora + timedelta(days=5),
                ),
                Derivacion(
                    paciente_id=pacientes[2].id,
                    especialidad="Dermatología",
                    motivo="Coordinación ficticia de agenda",
                    prioridad="Baja",
                    estado="Agendada",
                    responsable="Agenda Central",
                    observaciones=None,
                    fecha_creacion=ahora - timedelta(days=5),
                    fecha_limite=None,
                ),
                Derivacion(
                    paciente_id=pacientes[0].id,
                    especialidad="Neurología",
                    motivo="Seguimiento administrativo ficticio",
                    prioridad="Alta",
                    estado="Atendida",
                    responsable="Coordinación Norte",
                    observaciones="Atención registrada para demostración.",
                    fecha_creacion=ahora - timedelta(days=20),
                    fecha_limite=ahora - timedelta(days=1),
                ),
                Derivacion(
                    paciente_id=pacientes[1].id,
                    especialidad="Oftalmología",
                    motivo="Cierre administrativo ficticio",
                    prioridad="Media",
                    estado="Cerrada",
                    responsable="Unidad de Derivaciones",
                    observaciones="Cerrada; no debe considerarse atrasada.",
                    fecha_creacion=ahora - timedelta(days=30),
                    fecha_limite=ahora - timedelta(days=10),
                ),
                Derivacion(
                    paciente_id=pacientes[2].id,
                    especialidad="Kinesiología",
                    motivo="Cancelación administrativa ficticia",
                    prioridad="Baja",
                    estado="Cancelada",
                    responsable="Agenda Central",
                    observaciones="Cancelada para demostración.",
                    fecha_creacion=ahora - timedelta(days=15),
                    fecha_limite=ahora + timedelta(days=10),
                ),
            ]
            db.add_all(derivaciones)
            db.flush()
            db.add_all(
                [
                    HistorialDerivacion(
                        derivacion_id=derivaciones[1].id,
                        estado_anterior="Pendiente",
                        estado_nuevo="En revisión",
                        fecha_cambio=ahora - timedelta(days=7),
                    ),
                    HistorialDerivacion(
                        derivacion_id=derivaciones[2].id,
                        estado_anterior="En revisión",
                        estado_nuevo="Agendada",
                        fecha_cambio=ahora - timedelta(days=4),
                    ),
                ]
            )
            db.commit()

            return {
                "pacientes": len(pacientes),
                "derivaciones": len(derivaciones),
                "historiales": 2,
            }
    finally:
        motor.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Carga datos ficticios en la base SQLite demo local."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help=(
            "Elimina solo healthbridge_demo.db local y vuelve a crear "
            "sus datos de demostración."
        ),
    )
    argumentos = parser.parse_args()

    if argumentos.reset:
        eliminar_base_demo()

    resumen = cargar_datos_demo()
    print(
        "Base demo lista: "
        f"{resumen['pacientes']} pacientes ficticios, "
        f"{resumen['derivaciones']} derivaciones y "
        f"{resumen['historiales']} movimientos de historial."
    )


if __name__ == "__main__":
    main()
