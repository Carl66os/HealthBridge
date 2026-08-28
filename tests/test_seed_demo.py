from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from backend.orm_models import Derivacion, HistorialDerivacion, Paciente
from scripts import seed_demo


@pytest.fixture
def directorio_demo_temporal(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def obtener_datos_demo() -> tuple[list[Derivacion], int, int]:
    motor = create_engine(seed_demo.URL_DEMO_LOCAL)
    try:
        with Session(motor) as db:
            derivaciones = list(db.scalars(select(Derivacion)).all())
            pacientes = len(db.scalars(select(Paciente)).all())
            historiales = len(db.scalars(select(HistorialDerivacion)).all())
            return derivaciones, pacientes, historiales
    finally:
        motor.dispose()


def test_carga_datos_demo_y_aplica_migraciones(directorio_demo_temporal):
    resumen = seed_demo.cargar_datos_demo()
    derivaciones, pacientes, historiales = obtener_datos_demo()
    motor = create_engine(seed_demo.URL_DEMO_LOCAL)
    try:
        with motor.connect() as conexion:
            revision = conexion.scalar(text("SELECT version_num FROM alembic_version"))
    finally:
        motor.dispose()

    assert (directorio_demo_temporal / "healthbridge_demo.db").exists()
    assert revision == "6fc0b3050d3e"
    assert resumen == {"pacientes": 3, "derivaciones": 6, "historiales": 2}
    assert pacientes == 3
    assert len(derivaciones) == 6
    assert historiales == 2


def test_no_duplica_datos_en_una_base_demo_poblada(directorio_demo_temporal):
    seed_demo.cargar_datos_demo()

    with pytest.raises(seed_demo.BaseDemoConDatosError):
        seed_demo.cargar_datos_demo()

    derivaciones, pacientes, historiales = obtener_datos_demo()
    assert (len(derivaciones), pacientes, historiales) == (6, 3, 2)


@pytest.mark.parametrize(
    "url_no_segura",
    [
        "postgresql+psycopg://usuario:secreto@localhost/healthbridge",
        "sqlite:///./otra_base.db",
        "sqlite:////servidor/healthbridge_demo.db",
    ],
)
def test_reset_rechaza_urls_no_seguras(url_no_segura):
    with pytest.raises(seed_demo.BaseDemoNoSeguraError):
        seed_demo.eliminar_base_demo(url_no_segura)


def test_datos_demo_cubren_escenarios_del_dashboard(directorio_demo_temporal):
    seed_demo.cargar_datos_demo()
    derivaciones, _, _ = obtener_datos_demo()
    ahora = datetime.now(timezone.utc)

    assert {derivacion.especialidad for derivacion in derivaciones} >= {
        "Cardiología",
        "Traumatología",
        "Dermatología",
    }
    assert {derivacion.estado for derivacion in derivaciones} == {
        "Pendiente",
        "En revisión",
        "Agendada",
        "Atendida",
        "Cerrada",
        "Cancelada",
    }
    assert {derivacion.prioridad for derivacion in derivaciones} == {
        "Alta",
        "Media",
        "Baja",
    }
    assert len({derivacion.responsable for derivacion in derivaciones}) >= 3
    assert any(derivacion.fecha_limite is None for derivacion in derivaciones)
    assert any(
        derivacion.fecha_limite is not None
        and derivacion.fecha_limite.replace(tzinfo=timezone.utc) < ahora
        and derivacion.estado not in {"Cerrada", "Cancelada"}
        for derivacion in derivaciones
    )
