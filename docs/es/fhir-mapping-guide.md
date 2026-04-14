# Guía de correspondencia FHIR

Esta guía explica cómo intercambiar los datos de discapacidad y funcionamiento de PublicSchema a través de FHIR R4. Cubre las dos formas comunes (`Observation` para resultados procesados, `QuestionnaireResponse` para capturas brutas de encuesta), el sistema de codificación LOINC, y dónde termina PublicSchema y comienza la elección del implementador.

Alcance: las propiedades de funcionamiento del Washington Group (WG-SS, WG-ES, CFM WG/UNICEF), así como las propiedades antropométricas y de embarazo que los programas de protección social reciben habitualmente de los sistemas de salud.

## Por qué FHIR importa para la protección social

Los datos sobre discapacidad y estado funcional provienen frecuentemente de los sistemas de salud. Cuando esos datos fluyen hacia los programas de protección social (elegibilidad para transferencias monetarias, asignación por discapacidad, derivaciones), el formato de intercambio suele ser FHIR.

PublicSchema no impone FHIR. Documenta la correspondencia para que los implementadores alineen su código con las observaciones codificadas en LOINC sin inventar su propia representación.

## Los dos patrones

- **`Observation`**: un resultado procesado, almacenado una vez en un registro de beneficiarios. `Observation.code` lleva el código LOINC de la pregunta WG; `valueCodeableConcept` lleva la respuesta (no_difficulty, some_difficulty, a_lot_of_difficulty, cannot_do).
- **`QuestionnaireResponse`**: la captura bruta del formulario tal como fue administrado, con todos los ítems del panel, el orden preservado y las trazas de lógica de salto. Apunta al panel LOINC WG-SS en `http://loinc.org/q/90151-4`.

Los sistemas de SP que reciben WG-SS desde una encuesta normalmente reciben un `QuestionnaireResponse` y luego derivan `Observation` por ítem para las reglas de elegibilidad.

## Códigos LOINC

El panel WG-SS es LOINC `90151-4`. Los códigos de ítem individuales de WG-SS, WG-ES y CFM están disponibles a través del CSV de publicación de LOINC (cuenta gratuita requerida en loinc.org), el servidor de terminología FHIR de LOINC (`https://fhir.loinc.org`), o la tabla de correspondencia LOINC publicada por el Washington Group.

Si no existe un código LOINC para un ítem determinado, los implementadores usan un `CodeSystem` local y documentan la laguna. No inventar códigos LOINC.

## Véase también

- La versión en inglés de esta guía contiene los ejemplos JSON completos y la discusión detallada de IPS y perfiles nacionales.
- [Guía de interoperabilidad y correspondencia](/es/docs/interoperability-guide/)
- [Divulgación selectiva](/es/docs/selective-disclosure/)
