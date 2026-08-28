# HealthBridge Referral Copilot — Tareas por commit

## 1. Base de pruebas

**Commit propuesto:** `test: preparar base aislada para referral copilot`

- Añadir Pytest a las dependencias de desarrollo.
- Crear `tests/` y fixtures sin datos reales.
- Configurar una base PostgreSQL de pruebas separada o transacciones reversibles.
- Cubrir las rutas actuales de derivaciones como línea base.

**Aceptación:** las pruebas no usan `.env` de desarrollo ni alteran datos de desarrollo.

## 2. Contrato y servicio determinista

**Commit propuesto:** `feat(copilot): agregar análisis determinista de derivaciones`

- Crear esquemas Pydantic del Copilot en un módulo dedicado.
- Crear el servicio puro de resumen, faltantes, prioridad, explicación e incertidumbre.
- Restringir la prioridad a `Alta`, `Media` o `Baja`.
- Incluir siempre `requiere_revision_humana=true` y el límite de uso no clínico.
- Añadir pruebas unitarias para reglas completas e incompletas.

**Aceptación:** el servicio no importa FastAPI, SQLAlchemy, `get_db` ni un SDK de IA.

## 3. Adaptador de anonimización

**Commit propuesto:** `feat(copilot): anonimizar datos de derivacion para analisis`

- Crear un adaptador que transforme una derivación a la entrada segura del Copilot.
- Excluir RUT, nombres, `paciente_id`, datos demográficos, secretos y relaciones ORM.
- Añadir pruebas que demuestren la ausencia de esos campos.

**Aceptación:** el objeto enviado al servicio contiene solo los campos permitidos por `spec.md`.

## 4. Ruta de consulta read-only

**Commit propuesto:** `feat(copilot): exponer consulta read-only de derivacion`

- Añadir un router dedicado y registrarlo en FastAPI.
- Recuperar una derivación existente mediante `get_db()`.
- Devolver 404 si no existe y la propuesta determinista si existe.
- No añadir `POST`, `PATCH`, `PUT` ni `DELETE` para el Copilot.

**Aceptación:** la ruta no realiza `add`, `commit`, `flush`, `delete` ni cambios de estado.

## 5. Pruebas de seguridad y documentación API

**Commit propuesto:** `test(copilot): validar limites de seguridad y revision humana`

- Probar respuestas con `requiere_revision_humana=true` en todos los casos.
- Probar que el Copilot no diagnostica ni prescribe.
- Probar que no se escriben registros de historial ni derivaciones.
- Documentar ejemplos ficticios en la API.

**Aceptación:** la suite completa cubre los límites de solo lectura y anonimización.

## 6. Integración LLM futura y opcional

**Commit propuesto:** `feat(copilot): agregar adaptador llm opcional`

- Requiere una decisión explícita de proveedor, modelo, coste y política de datos.
- Añadir una interfaz de adaptador, sin acoplar la lógica de negocio al SDK.
- Mantener el motor determinista como alternativa predeterminada.

**Aceptación:** ningún secreto llega a código, logs, respuestas o control de versiones; la salida conserva revisión humana obligatoria.
