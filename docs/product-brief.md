# HealthBridge — Product Brief

## 1. Descripción

HealthBridge es una plataforma HealthTech orientada a la gestión y trazabilidad de derivaciones clínicas.

El proyecto busca facilitar el seguimiento de una derivación desde su creación hasta su cierre, permitiendo visualizar su estado, prioridad, responsable, fechas relevantes e historial de cambios.

En su etapa inicial, HealthBridge será desarrollado únicamente con datos ficticios y con fines académicos, de aprendizaje y demostración.

---

## 2. Problema a investigar

En un proceso de derivación clínica pueden participar diferentes profesionales, unidades administrativas y etapas.

La hipótesis inicial del proyecto es que, cuando la información relacionada con estas derivaciones se encuentra distribuida entre diferentes herramientas o procesos, puede resultar más difícil identificar rápidamente:

- Qué derivaciones continúan pendientes.
- Cuáles se encuentran atrasadas.
- Quién es responsable de gestionarlas.
- Qué acciones se han realizado anteriormente.
- Cuánto tiempo lleva cada derivación en proceso.

Este problema deberá ser validado mediante investigación y entrevistas antes de considerarse una necesidad clínica real.

---

## 3. Usuario objetivo inicial

El usuario principal considerado para el MVP será un funcionario encargado de gestionar o coordinar derivaciones clínicas.

En versiones futuras podrían existir diferentes tipos de usuarios:

- Personal administrativo.
- Profesionales de salud.
- Coordinadores.
- Supervisores.
- Administradores del sistema.

---

## 4. Propuesta de valor

HealthBridge busca centralizar la información asociada a una derivación clínica y facilitar la visualización de su progreso.

La plataforma permitirá conocer rápidamente:

- Estado actual.
- Prioridad.
- Especialidad o unidad.
- Responsable.
- Fecha de creación.
- Fecha límite.
- Historial de modificaciones.

---

## 5. MVP

La primera versión funcional de HealthBridge deberá permitir:

1. Registrar pacientes ficticios.
2. Crear una derivación.
3. Asociar una derivación a un paciente.
4. Seleccionar una especialidad.
5. Asignar una prioridad.
6. Consultar las derivaciones existentes.
7. Buscar derivaciones.
8. Filtrar derivaciones según estado.
9. Actualizar el estado de una derivación.
10. Registrar un historial de cambios.
11. Identificar derivaciones atrasadas.
12. Visualizar indicadores básicos.

---

## 6. Estados de una derivación

Inicialmente se utilizarán los siguientes estados:

- Pendiente.
- En revisión.
- Agendada.
- Atendida.
- Cerrada.
- Cancelada.

Un flujo normal podría ser:

Pendiente → En revisión → Agendada → Atendida → Cerrada

---

## 7. Prioridades

Las derivaciones podrán tener tres niveles iniciales:

- Baja.
- Media.
- Alta.

La prioridad en el MVP será utilizada únicamente con fines demostrativos y no representará criterios clínicos reales.

---

## 8. Información de una derivación

Cada derivación podrá contener:

- ID.
- Paciente.
- Especialidad.
- Motivo.
- Prioridad.
- Estado.
- Responsable.
- Fecha de creación.
- Fecha límite.
- Observaciones.
- Historial de modificaciones.

---

## 9. Fuera del alcance inicial

El MVP NO incluirá:

- Pacientes reales.
- Información clínica real.
- Diagnósticos automáticos.
- Recomendaciones médicas.
- Integración con TrakCare.
- Integraciones con hospitales.
- Acceso a fichas clínicas reales.
- Inteligencia artificial clínica.
- Prescripción de medicamentos.
- Decisiones clínicas automatizadas.

---

## 10. Pregunta inicial de investigación

¿Puede una plataforma centralizada de trazabilidad facilitar la identificación y seguimiento de derivaciones pendientes o atrasadas dentro de un flujo clínico simulado?

---

## 11. Hipótesis inicial

El uso de una plataforma centralizada de trazabilidad podría reducir el tiempo necesario para conocer el estado de una derivación y facilitar la identificación de solicitudes pendientes o atrasadas frente a un método de seguimiento no centralizado.

---

## 12. Posibles métricas

En una futura evaluación se podrían medir:

- Tiempo necesario para localizar una derivación.
- Tiempo para identificar una derivación atrasada.
- Número de pasos necesarios para realizar una tarea.
- Número de errores durante una búsqueda.
- Porcentaje de tareas completadas correctamente.
- Usabilidad percibida.
- Satisfacción del usuario.

---

## 13. Tecnologías previstas

### Backend

- Python.
- FastAPI.

### Base de datos

- PostgreSQL.

### Frontend

- React.

### Control de versiones

- Git.
- GitHub.

### Testing

- Pytest.

### Interoperabilidad futura

- HL7 FHIR.

---

## 14. Evolución futura

Después del MVP, HealthBridge podría incorporar:

- Inicio de sesión.
- Roles y permisos.
- Auditoría.
- Dashboard avanzado.
- Notificaciones.
- API REST documentada.
- Docker.
- Despliegue en la nube.
- Interoperabilidad mediante HL7 FHIR.
- Integración con sistemas externos.