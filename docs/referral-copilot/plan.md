# HealthBridge Referral Copilot — Plan de implementación

## Decisión de alcance

El primer entregable será un Copilot determinista, interno y de solo lectura. No requiere cambios de esquema, migraciones, proveedor de IA ni credenciales. Su única salida será una propuesta explicada que exige revisión humana.

## Arquitectura objetivo

```text
Ruta FastAPI de solo lectura
        ↓
Adaptador de derivación anonimizada
        ↓
Servicio Referral Copilot determinista
        ↓
Esquema Pydantic de respuesta
```

El adaptador seleccionará únicamente los campos permitidos. El servicio no conocerá sesiones SQLAlchemy, pacientes ni identificadores. La ruta no reutilizará las operaciones de actualización de estado.

## Fases

### Fase 0 — Línea base

- Recuperar un entorno Python funcional.
- Añadir pruebas automatizadas y una configuración de base de datos de pruebas aislada.
- Confirmar los cambios actuales de filtros e indicadores en un commit separado.

### Fase 1 — Núcleo determinista

- Definir esquemas de entrada y salida del Copilot.
- Implementar resumen, detección de faltantes, reglas de prioridad administrativa e incertidumbre.
- Probar el servicio sin FastAPI, PostgreSQL ni proveedor externo.

### Fase 2 — Integración read-only

- Crear una ruta que recupere una derivación existente.
- Convertirla a un objeto anonimizado y enviarlo al servicio.
- Devolver la propuesta sin escribir en la base.

### Fase 3 — Endurecimiento

- Añadir pruebas de no escritura, anonimización y límites no clínicos.
- Documentar ejemplos y respuestas de error.
- Revisar manualmente que toda respuesta exija revisión humana.

### Fase futura — Proveedor LLM opcional

Solo tras aprobación explícita:

- definir un adaptador de proveedor independiente;
- añadir variables opcionales documentadas en `.env.example`, sin valores reales;
- añadir una política de minimización de datos, tiempos de espera y tratamiento de errores;
- conservar el motor determinista como respaldo.

No se deben guardar recomendaciones ni aprobaciones hasta que se diseñe una auditoría específica y se apruebe la correspondiente migración.
