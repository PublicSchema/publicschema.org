# Metadatos de entrevista

Cada registro de perfil lleva un contexto administrativo sobre cómo se recopilaron los datos. Esta guía explica cómo los autores de formularios deben completar las propiedades clave de metadatos de entrevista.

## `observation_date`

La fecha en que se recopilaron los datos. Para la mayoría de los formularios de campo, es la fecha de hoy (completada automáticamente al abrir o enviar el formulario). Cuando la captura de datos se realiza después del hecho (por ej. transcripción de papel a digital), la observation_date debe ser la fecha de recolección original, no la fecha de transcripción.

## `performed_by`

El agente que realizó la recolección de datos. Puede ser:

- **Una referencia a un registro Agent** (Person u Organization) cuando el encuestador es un usuario conocido y registrado en el sistema.
- **Un nombre para mostrar** cuando el sistema no mantiene un registro de encuestadores.

Los sistemas de formularios que autentican a los encuestadores deben completar este campo automáticamente a partir del usuario conectado.

## `instrument_used`

Una referencia al registro Instrument que describe la herramienta de recolección. Para instrumentos estándar (WG-SS, SMART, FCS del PMA), usar el identificador canónico del registro de instrumentos de PublicSchema.

## `administration_mode`

Cómo se administró el instrumento. Valores del vocabulario `administration-mode`:

- `self`: el sujeto completó el instrumento por sí mismo
- `proxy`: un cuidador o miembro del hogar respondió en nombre del sujeto
- `assisted`: el sujeto respondió con asistencia de un encuestador
- `mixed`: algunos ítems fueron auto-reportados, otros reportados por proxy

Para instrumentos infantiles (CFM 2-4, CFM 5-17), el modo es siempre `proxy` ya que el cuidador responde.

## `respondent` y `respondent_relationship`

Cuando el modo de administración es `proxy` o `mixed`, registrar quién respondió y su relación con el sujeto. `respondent` es una referencia o descripción de la persona que respondió. `respondent_relationship` usa el vocabulario `relationship-type` (por ej. padre/madre, cónyuge, cuidador).
