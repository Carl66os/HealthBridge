from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rut: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    sexo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    derivaciones: Mapped[list["Derivacion"]] = relationship(
        back_populates="paciente"
    )


class Derivacion(Base):
    __tablename__ = "derivaciones"
    __table_args__ = (
        CheckConstraint(
            "prioridad IN ('Alta', 'Media', 'Baja')",
            name="ck_derivaciones_prioridad_valida",
        ),
        CheckConstraint(
            "estado IN ('Pendiente', 'En revisión', 'Agendada', "
            "'Atendida', 'Cerrada', 'Cancelada')",
            name="ck_derivaciones_estado_valido",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.id"),
        nullable=False,
        index=True,
    )
    especialidad: Mapped[str] = mapped_column(String(255), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    prioridad: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Pendiente",
        server_default="Pendiente",
    )
    responsable: Mapped[str] = mapped_column(String(255), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    fecha_limite: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    paciente: Mapped["Paciente"] = relationship(back_populates="derivaciones")
    historial: Mapped[list["HistorialDerivacion"]] = relationship(
        back_populates="derivacion"
    )


class HistorialDerivacion(Base):
    __tablename__ = "historial_derivaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    derivacion_id: Mapped[int] = mapped_column(
        ForeignKey("derivaciones.id"),
        nullable=False,
        index=True,
    )
    estado_anterior: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_cambio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    derivacion: Mapped["Derivacion"] = relationship(back_populates="historial")
