# Guía de JSON-LD y credenciales verificables

Esta guía explica cómo usar PublicSchema con contextos JSON-LD y credenciales verificables SD-JWT. Esta es una de las varias formas de usar PublicSchema. Consulte [Casos de uso](/docs/use-cases/) para una visión general más amplia de los patrones de integración, muchos de los cuales no requieren JSON-LD ni credenciales verificables.

## Qué usa este camino

Este camino de integración se basa en los siguientes artefactos de PublicSchema:

- **Contexto JSON-LD**: mapea nombres de propiedad a URIs estables con información de tipo
- **Esquemas JSON**: esquemas de validación por concepto y por credencial
- **Tipos de credencial**: esquemas SD-JWT VC para IdentityCredential, EnrollmentCredential, PaymentCredential

Para la lista completa de artefactos disponibles, consulte [Artefactos disponibles](#artefactos-disponibles) a continuación.

## Inicio rápido

### 1. Referencie el contexto

Añada el contexto de PublicSchema a sus documentos JSON-LD:

```json
{
  "@context": "https://publicschema.org/ctx/draft.jsonld",
  "type": "Person",
  "given_name": "Amina",
  "family_name": "Diallo",
  "date_of_birth": "1988-03-15"
}
```

Esto hace que sus datos sean legibles por máquina. Cualquier sistema que entienda el contexto de PublicSchema puede procesarlos.

### 2. Valide sus datos

Use los esquemas JSON generados para validar datos en tiempo de ejecución:

```python
import json
import jsonschema

# Load the schema for the concept you're using
schema = json.load(open("person.schema.json"))

# Validate your data
data = {"given_name": "Amina", "date_of_birth": "1988-03-15", "gender": "female"}
jsonschema.validate(data, schema)
```

Los esquemas están disponibles en `https://publicschema.org/schemas/{Concept}.schema.json`.

### 3. Use los códigos de vocabulario canónicos

Cuando su sistema almacena estado de inscripción, estado de pago, género, etc., mapee sus códigos internos a los canónicos de PublicSchema:

| Su sistema | PublicSchema | Vocabulario |
|---|---|---|
| `ACTV` | `active` | enrollment-status |
| `M` | `male` | gender-type |
| `BANK` | `bank_transfer` | delivery-channel |

El archivo `vocabulary.json` contiene la lista completa de vocabularios con todos los códigos, definiciones y correspondencias de sistemas.

### 4. Emita credenciales verificables

Use los tipos de credencial de PublicSchema para emitir credenciales verificables SD-JWT:

```json
{
  "iss": "did:web:your-system.example.gov",
  "sub": "did:web:your-system.example.gov:persons:4421",
  "iat": 1706745600,
  "nbf": 1706745600,
  "exp": 1738435200,
  "vct": "https://publicschema.org/schemas/credentials/EnrollmentCredential",
  "_sd_alg": "sha-256",
  "cnf": {
    "jwk": { "kty": "EC", "crv": "P-256", "x": "...", "y": "..." }
  },
  "credentialSubject": {
    "type": "Person",
    "_sd": ["...hash(given_name)...", "...hash(family_name)..."],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "is_enrolled": true,
      "enrollment_date": "2025-01-15",
      "_sd": ["...hash(program_ref)..."]
    }
  }
}
```

### 5. Implemente la divulgación selectiva

Consulte las definiciones de tipos de credencial en la guía de [Divulgación selectiva](/docs/selective-disclosure/) para determinar qué afirmaciones deben ser divulgables selectivamente en las credenciales verificables SD-JWT. Cada tipo de credencial especifica qué afirmaciones se divulgan siempre y cuáles se envuelven en `_sd` (reveladas solo cuando se necesitan).

## Correspondencia de sistemas

Si su sistema usa nombres de campo o códigos diferentes, use los `system_mappings` en los archivos YAML de vocabulario para traducir. Cada entrada de sistema lista sus valores con el código original, la etiqueta legible y el valor canónico al que se mapea. Por ejemplo, el vocabulario gender-type incluye:

```yaml
system_mappings:
  openimis:
    vocabulary_name: Gender
    values:
      - code: "M"
        label: Male
        maps_to: male
      - code: "F"
        label: Female
        maps_to: female
      - code: "O"
        label: Other
        maps_to: other
    unmapped_canonical: [not_stated]
  dci:
    vocabulary_name: GenderCode
    values:
      - code: "1"
        label: Male
        maps_to: male
      - code: "2"
        label: Female
        maps_to: female
      - code: "0"
        label: Not stated
        maps_to: not_stated
```

La lista `unmapped_canonical` muestra qué valores de PublicSchema no tienen equivalente en ese sistema, haciendo explícitas las brechas en ambas direcciones. Consulte el [Ejemplo de correspondencia](/docs/mapping-example/) para un recorrido completo.

## Artefactos disponibles

| Artefacto | URL | Descripción |
|---|---|---|
| Contexto JSON-LD | [`/ctx/draft.jsonld`](/ctx/draft.jsonld) | Mapea nombres de propiedad a URIs |
| Vocabulario completo (JSON-LD) | [`/v/draft/publicschema.jsonld`](/v/draft/publicschema.jsonld) | Vocabulario completo como un @graph JSON-LD único |
| Vocabulario completo (Turtle) | [`/v/draft/publicschema.ttl`](/v/draft/publicschema.ttl) | Vocabulario completo como RDF/Turtle |
| Formas SHACL | [`/v/draft/publicschema.shacl.ttl`](/v/draft/publicschema.shacl.ttl) | Formas de validación para todos los conceptos |
| Vocabulario JSON | [`/vocabulary.json`](/vocabulary.json) | Vocabulario completo con todos los conceptos, propiedades y vocabularios |
| Esquemas de concepto | `/schemas/{Concept}.schema.json` | Esquema JSON por concepto |
| Esquemas de credencial | `/schemas/credentials/{Type}.schema.json` | Esquema JSON SD-JWT VC por tipo de credencial |

## Interoperabilidad con schema.org

PublicSchema declara equivalencias con schema.org para las propiedades que se superponen. El contexto JSON-LD incluye alias en camelCase:

- `given_name` y `givenName` ambos resuelven a `https://publicschema.org/given_name`
- `date_of_birth` y `birthDate` ambos resuelven a `https://publicschema.org/date_of_birth`
- `start_date` y `startDate` ambos resuelven a `https://publicschema.org/start_date`

Use la convención de nomenclatura que prefiera su sistema. Ambas son válidas en el contexto.

## Comportamiento de respaldo de `@vocab`

El contexto de PublicSchema declara `"@vocab": "https://publicschema.org/"`. Esto significa que cualquier clave JSON que no esté explícitamente definida en el contexto se expandirá sin advertencia a `https://publicschema.org/{key}`. Por ejemplo, un error tipográfico como `"givn_name"` se expandiría a `https://publicschema.org/givn_name` en lugar de producir un error.

Los procesadores JSON-LD no detectarán esto. Para capturar errores tipográficos y propiedades no declaradas, valide sus datos contra el esquema JSON del concepto que está usando. El esquema JSON solo permite propiedades declaradas, por lo que `"givn_name"` fallaría la validación.

## Correspondencia de `alternateName` de schema.org

La propiedad `preferred_name` de PublicSchema se mapea al `alternateName` de schema.org como un `broadMatch`, no un `exactMatch`. El `alternateName` de schema.org cubre cualquier nombre alternativo (apodos, nombres anteriores, abreviaciones), mientras que `preferred_name` es específicamente el nombre con el que la persona prefiere ser identificada. Si su sistema usa `alternateName` de schema.org, tenga en cuenta que es semánticamente más amplio.

## Extensión de PublicSchema

Consulte el [Mecanismo de extensión](/docs/extension-mechanism/) para saber cómo añadir propiedades personalizadas, valores de vocabulario y conceptos usando su propio espacio de nombres junto con los términos de PublicSchema.

## Pasos siguientes

- Para un enfoque más ligero que no requiere JSON-LD, consulte la [Guía de adopción de vocabulario](/docs/vocabulary-adoption-guide/).
- Para mapear campos entre sistemas existentes, consulte la [Guía de interoperabilidad y correspondencia](/docs/interoperability-guide/).
- Para diseñar un nuevo sistema compatible, consulte la [Guía de diseño de modelo de datos](/docs/data-model-guide/).
- Para escenarios concretos que muestran cómo se usa PublicSchema, consulte [Casos de uso](/docs/use-cases/).
