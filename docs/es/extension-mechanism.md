# Extensión de PublicSchema

## Principios

PublicSchema es descriptivo, no normativo. Los sistemas adoptan los conceptos, propiedades y vocabularios que les aplican. Cuando un sistema necesita algo que PublicSchema no ofrece, lo extiende usando su propio espacio de nombres.

JSON-LD hace esto sencillo: cualquier término que no esté en el contexto de PublicSchema puede definirse en un contexto adicional.

## Cómo extender

### Añadir propiedades personalizadas a un concepto de PublicSchema

Use una segunda entrada `@context` con su propio espacio de nombres:

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/",
      "beneficiary_category": "myorg:beneficiary_category",
      "proxy_score_v2": {
        "@id": "myorg:proxy_score_v2",
        "@type": "xsd:decimal"
      }
    }
  ],
  "type": "Person",
  "given_name": "Amina",
  "family_name": "Diallo",
  "beneficiary_category": "ultra_poor",
  "proxy_score_v2": 23.7
}
```

Los términos de PublicSchema (`given_name`, `family_name`) se resuelven como URIs de PublicSchema. Sus términos personalizados (`beneficiary_category`, `proxy_score_v2`) se resuelven como URIs de su espacio de nombres. Ambos coexisten sin conflicto.

### Añadir valores de vocabulario personalizados

Si un vocabulario de PublicSchema no cubre los códigos de su sistema, extiéndalo:

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/"
    }
  ],
  "type": "Enrollment",
  "beneficiary": "...",
  "program_ref": "...",
  "enrollment_status": "myorg:waitlisted"
}
```

El verificador observa que `enrollment_status` tiene un valor de su espacio de nombres, no del conjunto canónico de PublicSchema. Puede elegir aceptarlo, mapearlo a un valor canónico o marcarlo para revisión.

### Añadir conceptos completamente nuevos

Defina su concepto en su propio espacio de nombres:

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/",
      "CaseManagementRecord": "myorg:CaseManagementRecord",
      "case_worker": {"@id": "myorg:case_worker", "@type": "@id"},
      "case_notes": "myorg:case_notes"
    }
  ],
  "type": "CaseManagementRecord",
  "beneficiary": "did:web:example.gov/persons/123",
  "case_worker": "did:web:example.gov/staff/456",
  "case_notes": "Follow-up visit scheduled for 2025-04-15"
}
```

Tenga en cuenta que `beneficiary` sigue resolviendo a la definición de PublicSchema, aunque se use en un concepto personalizado. Reutilice los términos de PublicSchema donde apliquen.

## Reglas prácticas

1. **Reutilice antes de inventar.** Consulte la lista de propiedades de PublicSchema antes de definir una propiedad personalizada. Si existe una propiedad con la semántica correcta, úsela.

2. **Ponga su espacio de nombres en sus extensiones.** Nunca defina un término sin prefijo que pudiera colisionar con una futura adición de PublicSchema. Use siempre un prefijo de espacio de nombres (`myorg:custom_field`).

3. **Documente sus extensiones.** Publique su contexto extendido en una URL estable para que otros sistemas puedan entender sus datos.

4. **Proponga hacia arriba.** Si su extensión resulta útil en múltiples sistemas, propóngala para su inclusión en PublicSchema. El vocabulario crece a través del uso en el mundo real, no del diseño en comité.

## Para emisores de credenciales

Al emitir una credencial verificable que usa extensiones:

- Incluya la URL de su contexto después del contexto de PublicSchema en la lista `@context`
- Use el tipo de credencial de PublicSchema (p. ej., `EnrollmentCredential`) más su propio tipo si es necesario
- Las propiedades extendidas siguen las mismas directrices de sensibilidad: anótelas como `standard`, `sensitive` o `restricted` (consulte [Diseño de esquema: Anotaciones de sensibilidad](../schema-design/#9-sensitivity-annotations))

Los verificadores que entiendan su contexto procesarán las extensiones. Los verificadores que no lo entiendan seguirán comprendiendo todos los términos de PublicSchema.
