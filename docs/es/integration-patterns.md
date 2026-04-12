# Patrones de integración

PublicSchema define qué significan los datos. No define cómo se mueven. Los mismos conceptos, propiedades y códigos de vocabulario funcionan con cualquier transporte: APIs REST, buses de eventos, credenciales verificables, intercambios de archivos y canalizaciones de análisis.

## La capa semántica

![PublicSchema se sitúa entre su modelo interno y cualquier transporte](/images/integration-layer.svg)

Su sistema mapea sus campos y códigos a PublicSchema una sola vez. A partir de ahí, la misma representación canónica fluye por cualquier canal.

Los ejemplos siguientes utilizan el mismo registro de inscripción en cada patrón.

## APIs REST

Exponga los nombres de propiedad y los códigos de vocabulario de PublicSchema en la superficie de su API. Los consumidores obtienen un contrato predecible sin necesidad de conocer su esquema interno.

```json
GET /api/enrollments/4421

{
  "type": "Enrollment",
  "given_name": "Amina",
  "family_name": "Diallo",
  "enrollment_status": "active",
  "enrollment_date": "2025-01-15",
  "program_ref": "cash-transfer-2025"
}
```

Valide las cargas útiles de solicitud y respuesta con los esquemas JSON de PublicSchema en el punto de entrada de la API.

## Sistemas orientados a eventos

Publique eventos de dominio con cargas útiles con forma de PublicSchema. Los suscriptores de diferentes sistemas los consumen sin necesidad de un mapeo de campos bilateral.

```json
{
  "event": "enrollment.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "type": "Enrollment",
    "given_name": "Amina",
    "family_name": "Diallo",
    "enrollment_status": "active",
    "enrollment_date": "2025-01-15",
    "program_ref": "cash-transfer-2025"
  }
}
```

El envoltorio del evento (tipo, marca de tiempo, metadatos de enrutamiento) corresponde a su implementación. La carga útil interior usa PublicSchema.

## Credenciales verificables

Emita credenciales verificables SD-JWT usando los tipos de credencial de PublicSchema. La persona titular controla qué afirmaciones revelar en cada presentación.

```json
{
  "vct": "https://publicschema.org/schemas/credentials/EnrollmentCredential",
  "credentialSubject": {
    "type": "Person",
    "_sd": ["...hash(given_name)...", "...hash(family_name)..."],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "enrollment_date": "2025-01-15",
      "_sd": ["...hash(program_ref)..."]
    }
  }
}
```

Las mismas propiedades aparecen tanto en la respuesta de la API como en la credencial. La diferencia es el modelo de confianza (firmas criptográficas, divulgación selectiva), no el vocabulario.

Consulte la [Guía de divulgación selectiva](/docs/selective-disclosure/) para ver las definiciones de tipos de credencial y las reglas de divulgación.

## Intercambio por lotes y archivos

Exporte datos como archivos CSV o JSON usando los nombres de propiedad de PublicSchema como encabezados de columna. Cualquier sistema con una correspondencia de PublicSchema puede importar el archivo sin procesamiento personalizado.

```csv
given_name,family_name,enrollment_status,enrollment_date,program_ref
Amina,Diallo,active,2025-01-15,cash-transfer-2025
```

Sin API, sin infraestructura. Una tabla de correspondencias y un CSV con columnas bien definidas.

## Almacén de datos y análisis

Use los códigos de vocabulario de PublicSchema como valores de dimensión canónicos. Las consultas entre programas funcionan porque `active` significa lo mismo en todas las tablas de origen.

```sql
SELECT program_ref, enrollment_status, COUNT(*)
FROM enrollment
WHERE enrollment_status = 'active'
GROUP BY program_ref, enrollment_status
```

Cada fuente mapea sus códigos a los códigos de PublicSchema en el momento de la carga. El almacén habla un solo vocabulario.

## Los mismos datos, cualquier transporte

| Capa | Qué provee PublicSchema |
|---|---|
| Conceptos | Definiciones de entidades compartidas (Person, Enrollment) |
| Propiedades | Nombres de campo canónicos (given_name, enrollment_status) |
| Vocabularios | Códigos de valor canónicos (active, suspended, completed) |
| Esquemas JSON | Validación de cargas útiles para APIs, eventos y credenciales |
| Contexto JSON-LD | Resolución de URI legible por máquina para datos enlazados y credenciales verificables |

## Qué guía leer a continuación

- Para alinear códigos de vocabulario sin cambiar su modelo de datos: [Guía de adopción de vocabulario](/docs/vocabulary-adoption-guide/)
- Para mapear campos entre sistemas existentes: [Guía de interoperabilidad y correspondencia](/docs/interoperability-guide/)
- Para diseñar un nuevo sistema compatible: [Guía de diseño de modelo de datos](/docs/data-model-guide/)
- Para usar contextos JSON-LD y emitir credenciales verificables: [Guía de JSON-LD y credenciales verificables](/docs/jsonld-vc-guide/)
- Para escenarios concretos: [Casos de uso](/docs/use-cases/)
