# HealthBridge: guía para contribuciones

## Alcance del proyecto

HealthBridge es una demostración académica de gestión y trazabilidad de derivaciones. Solo se permiten datos ficticios. No debe utilizarse ni presentarse como un sistema clínico real.

## Seguridad y datos

- No leer, registrar, mostrar ni enviar el contenido de `.env`.
- No incluir credenciales, secretos, RUT, nombres u otros identificadores personales en prompts, registros o respuestas de IA.
- No ejecutar operaciones destructivas sobre PostgreSQL (`DROP`, `DELETE`, truncados) salvo una autorización explícita y acotada.
- No ejecutar migraciones sin que la tarea lo solicite expresamente.
- Antes de editar, revisar `git status`; preservar cambios del usuario que no pertenezcan a la tarea.

## Backend

- Mantener FastAPI, SQLAlchemy 2.x y la dependencia `get_db()` para acceso a PostgreSQL.
- Mantener separados los modelos ORM (`backend/orm_models.py`) y los esquemas Pydantic (`backend/models.py`) hasta que una tarea aprobada redefina esa estructura.
- No eliminar `backend/data.py` ni `backend/prototype.py`; son código legado de la evolución del proyecto.
- Todo cambio de esquema requiere una migración Alembic revisada; no generar una migración si la tarea no lo autoriza.

## Referral Copilot

- Es apoyo administrativo para derivaciones, nunca diagnóstico, prescripción ni decisión clínica.
- La primera versión es determinista y de solo lectura: no actualiza pacientes, derivaciones, estados ni historial.
- Toda salida debe incluir `requiere_revision_humana: true`.
- Las sugerencias de prioridad se basan exclusivamente en señales administrativas permitidas y deben explicar su incertidumbre.
- Un proveedor LLM será una integración futura, desacoplada y opcional; no añadir SDK ni credenciales sin una tarea explícita.

## Calidad

- Añadir o actualizar pruebas antes de considerar lista una funcionalidad nueva.
- Usar una base de datos de pruebas aislada para pruebas de integración; nunca reutilizar datos de desarrollo como fixture.
- Mantener commits pequeños, de un único propósito, con mensajes claros.
