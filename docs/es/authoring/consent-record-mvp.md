# Registro de consentimiento: conjunto mínimo viable

Cuando un formulario recopila el consentimiento antes de proceder con una encuesta o registro, las siguientes propiedades de PublicSchema proporcionan un ConsentRecord mínimo viable. Los programas pueden agregar más campos, pero estas cinco propiedades capturan la cadena esencial quién-qué-cuándo que los marcos de auditoría y protección de datos requieren.

## Propiedades

| Propiedad | Tipo | Propósito |
|---|---|---|
| `consent_given` | booleano | Si el sujeto dio su consentimiento. Condición para continuar. |
| `consenting_party` | referencia (Person) | Quién dio el consentimiento (el sujeto, o un tutor para menores). |
| `consent_date` | fecha | Cuándo se dio el consentimiento. |
| `purpose` | cadena (vocabulario: `consent-purpose`) | Qué cubre el consentimiento (por ej. registro, compartir datos, investigación). |
| `privacy_notice_version` | cadena | Qué versión del aviso de privacidad se presentó. |

## Notas de uso

- Si el consentimiento es rechazado (`consent_given: false`), el formulario debe detenerse o bifurcarse. El ConsentRecord se crea de todos modos para documentar el rechazo.
- Para encuestas de hogares, crear un solo ConsentRecord por hogar (no por miembro), a menos que los miembros sean encuestados individualmente.
- `privacy_notice_version` permite a los auditores verificar que se mostró el aviso correcto. Almacenar el identificador de versión, no el texto completo del aviso.

## Véase también

- [ADR-009: ConsentRecord y capa de gobernanza de datos](../../decisions/009-consent.md)
- [Concepto ConsentRecord](../../schema/concepts/consent-record.yaml)
