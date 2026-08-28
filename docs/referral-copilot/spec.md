# HealthBridge Referral Copilot — Especificación

## Propósito

HealthBridge Referral Copilot será una ayuda administrativa de solo lectura para revisar derivaciones ficticias. Su propósito es hacer más visible la información ya registrada y apoyar la priorización operativa; no entrega evaluación, diagnóstico, tratamiento ni decisiones clínicas.

## Límites obligatorios

- No escribe en PostgreSQL ni modifica pacientes, derivaciones, estados o historial.
- No prescribe, diagnostica, interpreta síntomas ni toma decisiones clínicas.
- No sustituye la revisión de una persona responsable.
- No recibe ni transmite RUT, nombres, secretos, credenciales ni contenido de `.env`.
- Toda respuesta contiene `requiere_revision_humana: true`.

## Entrada segura

La primera versión trabajará con un objeto de derivación anonimizado. Podrá contener únicamente:

- especialidad;
- motivo;
- prioridad actual;
- estado;
- responsable;
- observaciones;
- fecha de creación;
- fecha límite;
- indicador calculado de atraso.

No debe incluir `paciente_id`, RUT, nombre, fecha de nacimiento, sexo ni relaciones completas del paciente.

## Salida esperada

La respuesta tendrá un contrato estructurado equivalente a:

```json
{
  "resumen": "Texto breve basado solo en los datos recibidos.",
  "datos_faltantes": ["responsable"],
  "prioridad_sugerida": "Media",
  "explicacion_prioridad": "Sugerencia operativa basada en prioridad registrada, estado y fecha límite.",
  "incertidumbre": "Media: falta información administrativa relevante.",
  "requiere_revision_humana": true,
  "limitacion": "No es una recomendación clínica ni modifica la derivación."
}
```

## Comportamiento determinista inicial

La primera implementación no usará un proveedor externo. Aplicará reglas transparentes y comprobables:

1. El resumen enumerará especialidad, estado, prioridad, responsable, fechas y observaciones disponibles.
2. Detectará como faltantes los campos administrativos vacíos o ausentes: especialidad, motivo, prioridad, responsable y observaciones. La ausencia de fecha límite se informará como dato opcional no registrado.
3. La prioridad sugerida solo considerará señales administrativas: prioridad actual registrada, atraso, estado y presencia de datos faltantes. Nunca inferirá gravedad o urgencia clínica desde el motivo.
4. La explicación indicará las señales usadas y las que faltan.
5. La incertidumbre será mayor cuando falten campos relevantes, no haya fecha límite o existan señales administrativas contradictorias.

Una sugerencia no cambia la prioridad guardada. La persona responsable debe revisarla y, si corresponde, aplicar cualquier cambio mediante los flujos normales de HealthBridge.

## Criterios de aceptación

- El Copilot acepta solamente datos anonimizados de una derivación.
- Produce los seis campos de salida definidos y valida las prioridades `Alta`, `Media` o `Baja`.
- Siempre devuelve `requiere_revision_humana: true`.
- No importa `Session`, `get_db`, modelos ORM ni ejecuta escrituras.
- Incluye limitación explícita de uso no clínico.
- Las reglas deterministas tienen pruebas para casos completos, atrasados, cerrados/cancelados y con datos faltantes.
- La integración posterior con un LLM conserva el mismo contrato de salida y pasa por una capa desacoplada.
