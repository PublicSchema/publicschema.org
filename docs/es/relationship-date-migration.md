# Conversión de fechas de relación

Las relaciones que se indican a continuación usan `start_date` y `end_date`, según la
[convención para relaciones](/docs/schema-design/#5-contexto-temporal). Los registros de origen
que llevan un par `valid_from` y `valid_to` para ellas suelen describir una validez
calendaria inclusiva.

Las definiciones publicadas usan días calendario completos, y tanto el día de inicio como
el de fin están incluidos: `end_date` es el último día efectivo
([ADR-027](../../decisions/027-end-date-boundary.md)). Por lo tanto, un par de origen inclusivo
se convierte cambiando el nombre de sus claves. Estos campos no son marcas de tiempo y no
describen el momento en que una fuente registró un hecho.

## Relaciones que usan fechas de inicio y de fin

| Relación | Qué acotan las fechas |
| --- | --- |
| HoldingParcelLink | El período durante el cual una finca utiliza una parcela. |
| AnimalResidence | El período durante el cual un animal o un grupo se mantiene en el sitio agropecuario identificado. |
| AnimalResponsibility | El período de la responsabilidad declarada como poseedor, propietario u otra. |
| AgriculturalServiceRole | El período en que se actúa como el prestador de servicios descrito. |
| IdentifierAssignment | El período de asignación de un identificador al sujeto. |
| NameUsage | El período de uso del nombre para el sujeto en su contexto declarado. |
| ContactPoint | El período de uso del canal de comunicación para contactar al sujeto. |
| AssetPartyRole | El período de la responsabilidad declarada sobre un activo físico. |
| AssetAddressAssignment | El período durante el cual la dirección se aplica al activo para su finalidad declarada. |

RegistryEntry y Registration conservan `valid_from`/`valid_to` inclusivos, incluidas
las especializaciones de inscripción registral y de autorización. AgriculturalParcel conserva la validez
de su descripción; Certification y LandTenureAssertion conservan
su validez de certificación o su validez jurídica sustantiva. No convierta estas fechas
porque se convierta una relación relativa al mismo sujeto. `recorded_at` tampoco cambia.

## Conservar cada día efectivo

Solo después de establecer que la fuente usa días calendario completos inclusivos:

1. Copie un `valid_from` presente sin cambios en `start_date`.
2. Copie un `valid_to` presente sin cambios en `end_date`.
3. Elimine las claves de origen. Conserve como omitido cada límite omitido.

Por ejemplo:

```json
{"@type":"AgriculturalServiceRole","valid_from":"2026-12-31","valid_to":"2026-12-31"}
```

se convierte en:

```json
{"@type":"AgriculturalServiceRole","start_date":"2026-12-31","end_date":"2026-12-31"}
```

Ambos describen un único día efectivo. Un fin ausente sigue siendo desconocido; no se
reemplaza por una fecha máxima ni se trata como prueba de validez perpetua. La precisión
desconocida, las fechas parciales, las marcas de tiempo y las convenciones de límites no especificadas requieren
aclaración de la fuente. Una fuente cuyo fin es el primer día en que la validez deja de
aplicarse no es inclusiva: reste un día a su fin, o aclárelo, antes de
usar la herramienta auxiliar.

## Interpretar las asignaciones de instalaciones de origen

Los registros de origen suelen indicar solo que una organización gestiona una instalación, sin
distinguir la explotación del local de su mantenimiento o de su propiedad. Examine las
pruebas de la fuente antes de seleccionar un código de función, con su esquema, para AssetPartyRole.
Haga corresponder la instalación con `subject_uri` y la organización con `asset_actor`, con un
`asset_role_type` explícito. Conserve la identidad del sujeto físico. Si las
pruebas establecen varias responsabilidades, represente aserciones distintas y
conserve sus vínculos de origen. No invente esas responsabilidades ni afirme que una
declaración genérica de gestión las demuestra.

Para un registro de origen que asigna una dirección a una instalación:

| Hecho de origen | AssetAddressAssignment |
| --- | --- |
| La instalación | `subject_uri`, que remite a la instalación física |
| La dirección | `assigned_address`, que conserva el Address |
| Una posición o geometría en la asignación | Ningún campo en la asignación; registre una posición en el `location` del Address o en el `spatial_geometry` del activo |
| Ninguna finalidad explícita | Añada un `address_purpose` respaldado por la fuente como CodedValue, conservando su esquema. |

Elegir la función o la finalidad de la dirección es un paso semántico que la herramienta auxiliar no
realiza. Solo convierte las fechas de un AssetPartyRole o de un AssetAddressAssignment
después de que estén presentes el activo, su parte o dirección, y un código de función o de finalidad
calificado por su esquema. La presencia de un código no demuestra las pruebas de su fuente; eso
sigue siendo responsabilidad de quien implementa.

Para los hechos médicos ya representados en FHIR nativo, conserve esa
representación seleccionada. Una aserción compartida sobre el patrimonio inmobiliario solo tiene razón de ser cuando los consumidores
la necesitan de forma independiente. Consulte [responsabilidades y direcciones de las instalaciones](/docs/facility-roles/).

## Usar la herramienta auxiliar acotada

La herramienta auxiliar, basada en la biblioteca estándar, lee un documento JSON y escribe un resultado completo
en la salida estándar. No reescribe su entrada ni usa la compilación del vocabulario como
marco de conversión. Espera registros ya puestos en correspondencia con los tipos de PublicSchema
anteriores que todavía llevan el `valid_from`/`valid_to` de la fuente. Examine primero
el contrato de la fuente y luego ejecute desde la raíz del repositorio:

```bash
uv run --locked python examples/relationship-date-migration/migrate.py \
  --source-boundary inclusive-calendar-days \
  examples/relationship-date-migration/source-records.json
```

Compare el resultado con `examples/relationship-date-migration/records.json`.
Si guarda su propio resultado, elija un archivo de salida distinto del de entrada. La
entrada lleva claves de fecha de origen y no debe validarse como carga útil de relación
de PublicSchema antes de la conversión.

El punto de entrada de Python es
`migrate_relationship_dates(document, source_boundary="inclusive-calendar-days")`.
Devuelve una copia profunda. Volver a pasar el resultado es idempotente y no
requiere una declaración de límite de la fuente cuando no quedan fechas de validez de origen. Cualquier
diagnóstico lanza MigrationError; la CLI emite diagnósticos JSON en la salida de error
estándar, termina con el código de estado 2 y no emite ningún documento parcial en la salida estándar.
Las rutas usan el escape de JSON Pointer. El argumento original y el archivo de entrada permanecen
sin cambios tanto en caso de éxito como de fallo.

La herramienta auxiliar acepta el alias compacto `@type` de cada relación y su identificador exacto
de PublicSchema, como IRI compacto `publicschema:` o como URI absoluto.
HoldingParcelLink, AnimalResidence y AgriculturalServiceRole están en el dominio `agri/`;
las demás relaciones están en la raíz. Los identificadores de tipo se conservan. Se rechaza un
espacio de nombres arbitrario con el mismo nombre local, así como los tipos múltiples
que involucran estas relaciones. La interpretación de alias del contexto y el JSON-LD expandido
requieren un adaptador aparte. Las demás clases, incluidos los tipos de registros de origen que aún no
se han puesto en correspondencia con PublicSchema, conservan sus fechas originales.

Los pares de fechas mixtos, de origen y actuales, se rechazan aunque parezcan concordar.
Concílielos a partir de la fuente. Las fechas exactas imposibles, los intervalos efectivos
invertidos y la precisión no admitida tienen diagnósticos de campo distintos y
deterministas.

Ejecute las comprobaciones específicas:

```bash
uv run --locked pytest tests/test_relationship_date_migration.py
```

Las pruebas comparan la pertenencia de los días efectivos antes y después de la conversión, incluidos casos de mes, año,
día bisiesto y un solo día. Cubren límites desconocidos, identificadores de clase no admitidos,
el significado de las asignaciones de instalaciones, límites omitidos, idempotencia y
fallo atómico. Los datos de prueba convertidos también se comprueban frente al JSON Schema generado real
y a las salidas SHACL expandidas con el contexto. Se comprueba la jerarquía de clases generada
en busca de descendientes de cada relación convertida, de modo que un subtipo afectado
no pueda quedar silenciosamente fuera de los tipos admitidos por la herramienta auxiliar. Los campos opcionales del vocabulario
no imponen por sí mismos todas las reglas de perfil.
