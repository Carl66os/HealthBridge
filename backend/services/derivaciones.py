from sqlalchemy import and_, case, func

from backend.orm_models import Derivacion


def condicion_atrasada():
    return and_(
        Derivacion.fecha_limite.is_not(None),
        Derivacion.fecha_limite < func.now(),
        Derivacion.estado.not_in(["Cerrada", "Cancelada"]),
    )


def expresion_atrasada():
    return case((condicion_atrasada(), True), else_=False)
