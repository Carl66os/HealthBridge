from sqlalchemy.orm import sessionmaker

from backend.database import crear_engine, get_db, obtener_database_url
from backend.main import app
from scripts import seed_demo


def test_database_url_temporal_inicializa_un_engine_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", seed_demo.URL_DEMO_LOCAL)

    url = obtener_database_url()
    motor = crear_engine(url)
    try:
        assert url == seed_demo.URL_DEMO_LOCAL
        assert motor.dialect.name == "sqlite"
    finally:
        motor.dispose()


def test_postgresql_se_mantiene_como_configuracion_predeterminada(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    url = obtener_database_url()

    assert url.drivername == "postgresql+psycopg"


def test_rutas_consultan_los_datos_sembrados_en_sqlite_demo(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", seed_demo.URL_DEMO_LOCAL)
    seed_demo.cargar_datos_demo()

    motor = crear_engine(obtener_database_url())
    sesiones = sessionmaker(bind=motor, autoflush=False, autocommit=False)

    def override_get_db():
        db = sesiones()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            respuesta = client.get("/derivaciones")
    finally:
        app.dependency_overrides.clear()
        motor.dispose()

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 6
    assert {
        derivacion["estado"] for derivacion in respuesta.json()
    } == {
        "Pendiente",
        "En revisión",
        "Agendada",
        "Atendida",
        "Cerrada",
        "Cancelada",
    }
