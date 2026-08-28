import os
from datetime import datetime, timedelta, timezone

os.environ["HEALTHBRIDGE_TESTING"] = "1"
os.environ["DB_HOST"] = "test-host"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "healthbridge_test"
os.environ["DB_USER"] = "test-user"
os.environ["DB_PASSWORD"] = "test-password"
os.environ.pop("DATABASE_URL", None)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.orm_models import Derivacion, Paciente


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    yield session_local

    engine.dispose()


@pytest.fixture
def client(test_db):
    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def derivaciones_ficticias(test_db):
    ahora = datetime.now(timezone.utc)

    with test_db() as db:
        paciente = Paciente(
            rut="11.111.111-1",
            nombre="Paciente Ficticio",
        )
        db.add(paciente)
        db.flush()

        db.add_all(
            [
                Derivacion(
                    paciente_id=paciente.id,
                    especialidad="Cardiología",
                    motivo="Control ficticio",
                    prioridad="Alta",
                    estado="Pendiente",
                    responsable="Unidad ficticia",
                    observaciones="Con fecha límite vencida",
                    fecha_limite=ahora - timedelta(days=1),
                ),
                Derivacion(
                    paciente_id=paciente.id,
                    especialidad="Traumatología",
                    motivo="Seguimiento ficticio",
                    prioridad="Media",
                    estado="Agendada",
                    responsable="Unidad ficticia",
                    observaciones="Con fecha límite futura",
                    fecha_limite=ahora + timedelta(days=7),
                ),
                Derivacion(
                    paciente_id=paciente.id,
                    especialidad="Dermatología",
                    motivo="Caso ficticio cerrado",
                    prioridad="Alta",
                    estado="Cerrada",
                    responsable="Unidad ficticia",
                    observaciones="Cerrada con fecha límite vencida",
                    fecha_limite=ahora - timedelta(days=2),
                ),
            ]
        )
        db.commit()


@pytest.fixture
def client_con_datos(client, derivaciones_ficticias):
    return client
