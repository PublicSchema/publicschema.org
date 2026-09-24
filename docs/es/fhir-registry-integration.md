# Integración del registro con FHIR

Use recursos FHIR nativos para las definiciones de medicamentos y el contenido de directorios sanitarios. PublicSchema aporta la identidad intersectorial del sujeto y los vínculos calificados a entradas de registro. No reproduce el modelo de recursos médicos ni requiere un servidor FHIR para esta integración basada en archivos.

El [ejemplo ejecutable](../../examples/fhir-registry/) contiene dos documentos separados:

- `bundle.fhir.json` es un Bundle FHIR R5 nativo de tipo colección con 19 recursos. Su tipo de medio es `application/fhir+json`.
- `registry-links.json` es un envoltorio de adaptador en JSON ordinario que contiene sujetos de PublicSchema, entradas RegistryEntry, vínculos RecordReference, asociaciones explícitas con recursos y hechos de origen sin correspondencia. Los campos de su envoltorio son configuración de aplicación de ejemplo, no nuevos términos del vocabulario de PublicSchema ni un perfil FHIR publicado.

Ejecute desde la raíz del repositorio, después de la [configuración de desarrollo habitual](../../CONTRIBUTING.md):

```bash
uv run --locked python examples/fhir-registry/validate.py
uv run --locked pytest tests/test_fhir_registry.py -q
```

Estos comandos usan las dependencias de Python y los artefactos locales existentes. No requieren conexión de red, instalación de Java, servicio de terminología ni un registro en funcionamiento. El verificador informa 19 recursos, 19 entradas de registro, 20 referencias FHIR locales y cinco vínculos de consumidor. Para otro extracto proporcionado, pase `--bundle PATH --links PATH`.

## Versión y selección de recursos

Este ejemplo fija **FHIR R5 5.0.0** y los perfiles base publicados `http://hl7.org/fhir/StructureDefinition/{ResourceType}|5.0.0`, incluido Bundle. Cada recurso declara ese perfil exacto en `meta.profile`. Estos perfiles base no establecen la conformidad con una guía de implementación jurisdiccional, EMA UPD, ISO IDMP ni un contrato de intercambio clínico. Varios recursos de definición de medicamentos son de uso a prueba (Trial Use), con distintos niveles de madurez.

R5 es el contrato seleccionado para este ejemplo porque aporta los recursos de definición de medicamentos y los campos de directorio que se usan juntos aquí. R4 tiene un [modelo MedicinalProduct](https://hl7.org/fhir/R4/medicinalproduct.html) diferente; la familia de recursos de definición también existe en R4B, pero este ejemplo valida solo R5. Un intercambio R4 o R4B existente debe conservar la versión y los perfiles que requiere y usar una correspondencia explícita, en lugar de volver a etiquetar su carga útil como R5. Consulte la [orientación entre versiones](https://hl7.org/fhir/R5/versions.html) de HL7.

| Aspecto | Recurso nativo y ejemplo |
| --- | --- |
| Definiciones de productos de uso humano y veterinario | [MedicinalProductDefinition](https://hl7.org/fhir/R5/medicinalproductdefinition.html), con registros de producto distintos y `domain`. Ninguno de los dos registros denota un lote físico, una prescripción ni la intercambiabilidad con el otro producto. |
| Funciones de los ingredientes y detalle de las sustancias | [Ingredient](https://hl7.org/fhir/R5/ingredient.html) apunta a su producto mediante `for` y a [SubstanceDefinition](https://hl7.org/fhir/R5/substancedefinition.html) mediante `substance.code.reference`. Los datos de prueba conservan una razón numérica de concentración y los sistemas de unidades. |
| Forma preparada y uso veterinario | [AdministrableProductDefinition](https://hl7.org/fhir/R5/administrableproductdefinition-definitions.html) usa `formOf`, la vía, las especies de destino y tiempos de espera específicos por tejido. El intervalo sintético de cero días para la leche es explícito; un uso no autorizado nunca debe codificarse como un tiempo de espera de cero. |
| Configuración del envase | [PackagedProductDefinition](https://hl7.org/fhir/R5/packagedproductdefinition-definitions.html) usa `packageFor`. Una configuración de envase tiene su propia identidad; el contenido fabricado detallado y los lotes quedan fuera de estos datos de prueba. |
| Permiso de comercialización médica | [RegulatedAuthorization](https://hl7.org/fhir/R5/regulatedauthorization-definitions.html) tiene una referencia al sujeto, una jurisdicción, un titular, un regulador y un período de validez propios. El permiso no es la identidad ni la disponibilidad del producto. |
| Prestador, local, servicio | [Organization](https://hl7.org/fhir/R5/organization-definitions.html), [Location](https://hl7.org/fhir/R5/location-definitions.html) y [HealthcareService](https://hl7.org/fhir/R5/healthcareservice-definitions.html). `HealthcareService.providedBy` identifica al prestador clínico, mientras que `Location.managingOrganization` identifica a la organización responsable del aprovisionamiento y el mantenimiento. FHIR interpreta un `providedBy` ausente como la `managingOrganization` de la Location, por lo que debe completarse `providedBy` siempre que el prestador sea distinto de la organización gestora. Este contrato exige `providedBy` en todo HealthcareService, y los datos de prueba usan organizaciones diferentes. |
| Acreditación de la organización | [Organization.qualification](https://hl7.org/fhir/R5/organization-definitions.html#Organization.qualification) de R5, con código, emisor, identificador y período. Esto no convierte una acreditación limitada al local en una cualificación de la organización. |
| Conectividad técnica | [Endpoint](https://hl7.org/fhir/R5/endpoint-definitions.html) conserva el tipo de conexión, el tipo de carga útil, el tipo MIME y la dirección. Un endpoint listado no se contacta y no otorga ningún acceso. |

Los conceptos clínicos son deliberadamente sintéticos y suelen expresarse con `CodeableConcept.text`. Quien adopte este enfoque debe seleccionar las terminologías de origen reales y los perfiles publicados aplicables. El ejemplo no introduce un nuevo sistema de códigos médicos.

## Contrato de identidad y de resolución local

Para cada recurso FHIR, una asociación vincula una `RegistryEntry` existente con un `fhir_full_url` exacto, un `resource_type`, un `profile` fijado y un par `system`/`value` de identificador de negocio. Estos valores identifican cosas distintas:

| Valor | Significado |
| --- | --- |
| `(register_uri, record_id)` | Clave calificada de la entrada de PublicSchema. `record_id` sigue siendo una cadena y conserva los ceros a la izquierda. |
| `subject_uri` | Aserción de identidad explícita para la cosa o la definición descrita. No se copia de la URL del registro FHIR. |
| `fullUrl` FHIR e `id` del recurso | Dirección e identidad lógica local del registro FHIR de origen. |
| `identifier.system` e `identifier.value` FHIR | Un identificador de negocio de origen. La coincidencia de este par comprueba la correspondencia declarada; no demuestra la autoridad de la fuente ni fusiona identidades. |

`Organization` y `health/HealthFacility` de PublicSchema aportan en el documento complementario identidades intersectoriales útiles por sí mismas. Su detalle médico permanece en FHIR nativo. HealthFacility denota un local físico y no equivale a toda Location de FHIR. Este ejemplo exige que la Location asociada tenga `mode: instance` y una clasificación explícita de sitio o edificio (`si`/`bu` en `http://terminology.hl7.org/CodeSystem/location-physical-type`); se rechazan las ubicaciones conceptuales y virtuales.

Las entradas de medicamentos y sustancias omiten el `subject_type` opcional de PublicSchema: el ejemplo no crea una clase médica nativa de reemplazo ni usa una clase de recurso FHIR como prueba del tipo de un sujeto del mundo real. En su lugar, cada vínculo de consumidor declara `expected_resource_type`, que se comprueba contra el registro nativo resuelto. El valor devuelto incluye el recurso FHIR sin cambios y el `subject_uri` afirmado por separado.

Todos los recursos provienen del Bundle local proporcionado. Las referencias absolutas deben coincidir con un `fullUrl` exacto; las referencias relativas `ResourceType/id` se resuelven con respecto a la URL base de la entrada de origen. Cada fullUrl debe concordar con el tipo y el id reales de su recurso. Los destinos de las referencias se comprueban frente a las restricciones `targetProfile` de las StructureDefinition de R5 publicadas; un `Reference.type` o un `Reference.identifier` explícitos también deben concordar con el registro resuelto. La forma en que está escrita una URL no basta por sí sola.

La resolución de entradas calificadas devuelve `resolved`, `missing-record` o `missing-resource`. Las discrepancias de identidad y de tipo son errores. El ejemplo exige que sus cinco vínculos de consumidor se resuelvan. `RegistryEntry.source_records` puede conservar un puntero de procedencia no resuelto, pero ese puntero no se trata como una fuente verificada. Ninguna URL de registro, endpoint, sistema de identificadores, contexto ni URL de perfil desencadena una solicitud remota.

Este contrato, acotado deliberadamente, rechaza perfiles adicionales, extensiones, extensiones modificadoras, reglas implícitas, recursos contenidos, Bundles anidados, referencias a versiones específicas, referencias FHIR solo con identificador y rutas de referencia no descritas por los perfiles de recursos cargados. Admitir cualquiera de ellos requiere un cambio explícito en el adaptador y sus artefactos aplicables. Un FHIR válido fuera de este contrato no es por ello un FHIR inválido.

El JSON FHIR nativo tiene su propia serialización. No añada el contexto JSON-LD de PublicSchema, no renombre `resourceType` como `@type` ni describa este Bundle como JSON-LD. Los consumidores RDF deben usar la [representación RDF de FHIR](https://hl7.org/fhir/R5/rdf.html), que es independiente.

## Correspondencia de entradas planas de registros sanitarios con FHIR

PublicSchema no tiene clases nativas para producto medicinal, servicio de atención sanitaria ni acreditación. Los intercambios entre registros suelen llevar estos hechos en entradas planas. Las filas siguientes nombran entradas y campos de origen habituales y el recurso FHIR R5 que lleva cada uno. Son decisiones de correspondencia, no un conversor general ni afirmaciones de equivalencia exacta. Conserve la fuente original y registre explícitamente todo campo sin correspondencia antes de reemplazar los datos de origen de quien adopte este enfoque.

| Entrada o campo de origen | Destino FHIR y condiciones |
| --- | --- |
| `MedicinalProduct`, `VeterinaryMedicinalProduct` | Use MedicinalProductDefinition. `name` corresponde a un nombre de producto, `identifiers` a identificadores de negocio y `medicinal_classification` a la clasificación, solo después de conservar el esquema y el significado del código. Seleccione `combinedPharmaceuticalDoseForm` para `medicinal_dose_form` solo cuando describa la misma forma a nivel de producto. El dominio veterinario no determina por sí mismo las especies de destino ni autoriza el uso. |
| `MedicinalIngredient`, `medicinal_ingredients` | Use Ingredient y sus referencias `for`. `ingredient_substance` puede hacer referencia a SubstanceDefinition. Un `ingredient_function` de origen que mezcla las funciones de principio activo y excipiente con funciones más precisas requiere decidir si cada valor corresponde a `role` o a `function` de FHIR. Haga corresponder `strength_numerator`/`strength_denominator` con la razón de presentación o de concentración apropiada solo cuando se conozca la base de medición. |
| `AdministrableProduct` | Use AdministrableProductDefinition. `presentation_of` corresponde a `formOf`, `administrable_dose_form` a `administrableDoseForm` y `administration_routes` a las estructuras de vía cuando sus significados coinciden. No existe un campo general `name` directo. Sus relaciones detalladas con ingredientes usan `for` de Ingredient; su `ingredient` codificado es una representación diferente. Conserve un nombre que de otro modo quedaría sin correspondencia o un vínculo de origen no admitido. |
| `PackagedMedicinalProduct` | Use PackagedProductDefinition. `name`, los identificadores y `package_description` pueden conservarse allí. Revise `packaged_medicines` como `packageFor`, que identifica el producto asociado, por separado del contenido real de `packaging.containedItem`. `package_type` y `package_quantity` requieren revisar el nivel de envasado y las unidades; una cantidad de sustancia no es un recuento de envases. |
| `HealthcareServiceOffering` | Use HealthcareService para `name`, `healthcare_provider`/`providedBy`, `service_facilities`/`location` y la clasificación del servicio de la fuente. Seleccione `category`, `type` o `specialty` para `healthcare_service_kind` según el significado. Un `service_channel` textual no tiene un campo general exacto. Para `service_endpoints`, distinga una referencia a un registro Endpoint de su `address` de red; exija los detalles de conexión y de carga útil que faltan antes de crear un Endpoint nativo. |
| `valid_from` y `valid_to` del servicio | HealthcareService de R5 base no tiene un período de vigencia general para la oferta de servicio. `active`, `availability` y los horarios de apertura no pueden reemplazarlo. Conserve ambas fechas de origen como sin correspondencia hasta que un perfil publicado aplicable o una extensión justificada lleve ese hecho. |
| `FacilityManagementAssignment` | Una asignación de gestión de una instalación es ambigua. Determine primero si la fuente afirma la explotación del servicio, el mantenimiento del local, la propiedad o la gobernanza institucional. Location.managingOrganization puede llevar una aserción de mantenimiento vigente solo cuando esa función esté establecida. No tiene período de gestión, por lo que los `valid_from`/`valid_to` de origen no se trasladan a esa referencia simple. Las funciones fechadas sobre activos físicos que se necesiten de forma independiente usan `AssetPartyRole` con un significado de función explícito. |
| `FacilityAddressAssignment` | Location nativa puede conservar un Address con su período de uso. La `AssetAddressAssignment` intersectorial sigue siendo útil para el historial de locales escolares y agropecuarios. Conserve la finalidad física o postal. Una SpatialGeometry arbitraria separada no puede comprimirse en `Location.position`, que es un punto con latitud y longitud y altitud opcional. Conserve la geometría no admitida mediante la entrada intersectorial y los vínculos de origen. |
| `HealthcareAccreditation` | La cualificación de una organización puede usar Organization.qualification, conservando el identificador, el código de cualificación, el emisor y el período aplicable. Un sujeto limitado al local, un `accreditation_standard` detallado o un `accreditation_scope` no tienen aquí un campo equivalente de forma automática. Conserve esas aserciones y sus pruebas sin correspondencia hasta que se seleccione un perfil aplicable. No infiera una acreditación de toda la organización a partir de un certificado de un sitio. |
| `Authorization`, `Registration`, `ServiceCapacityObservation` genéricos | Se conservan por sus significados intersectoriales. Prefiera RegulatedAuthorization para los intercambios nativos de autorizaciones médicas; esto no hace equivalentes todos los campos generales de autorización. No se afirma ninguna equivalencia FHIR para la observación genérica de capacidad. Un intercambio de informes sanitarios necesita un perfil para su medida real. |

Los límites de las fechas requieren una decisión explícita. Un `valid_to` de origen suele significar la última fecha aplicable. `end_date` de PublicSchema es el último día efectivo, y [Period](https://hl7.org/fhir/R5/datatypes-definitions.html#Period) de FHIR también incluye su fin, aunque admite precisión parcial y horas. Confirme el límite de la fuente antes de convertir; no invente marcas de tiempo ni copie un período en otro hecho.

El documento complementario muestra `migration_outcomes` con `state: unmapped`, el RecordReference original, la ruta de origen, el valor de origen y el motivo. Sus ejemplos conservan una fecha de inicio general del servicio, una fecha de fin de gestión ambigua y un sujeto de acreditación limitado al local. Use las relaciones `source_records` y `EvidenceAssertion` existentes para conservar la procedencia en un registro real. Este ejemplo muestra cómo informar hechos no resueltos; no convierte automáticamente los registros heredados ni promete un viaje de ida y vuelta sin pérdidas.

## Qué establecen las comprobaciones

`validate.py` usa el archivo oficial de JSON Schema sin modificar y las StructureDefinition base publicadas en [artifacts](../../examples/fhir-registry/artifacts/). Comprueba sus resúmenes SHA-256 antes de usarlos. Los archivos suman unos 650 KB comprimidos, no añaden ninguna dependencia y no se descargan en tiempo de ejecución. Las pruebas de Python también validan las instancias del documento complementario de PublicSchema frente a los esquemas de PublicSchema generados reales.

JSON Schema comprueba la estructura y las restricciones codificadas en ese artefacto. El adaptador comprueba además las identidades locales, los tipos de destino, los perfiles esperados y los identificadores de negocio descritos arriba. No evalúa las invariantes FHIRPath, todas las reglas de elección y cardinalidad, los enlaces terminológicos, la completitud de la narrativa, la corrección clínica ni los perfiles jurisdiccionales. Esta distinción sigue la [orientación de validación de FHIR](https://hl7.org/fhir/R5/validation.html).

Para una comprobación de autoría independiente, descargue el [validador HL7 6.9.12](https://github.com/hapifhir/org.hl7.fhir.core/releases/tag/6.9.12) fijado en un almacenamiento temporal. Requiere Java; el JAR ocupa unos 187 MB y no es una dependencia del repositorio ni de tiempo de ejecución. El script envoltorio verifica el SHA-256 `0e53ab1d1a6f1e35f505255c0b8ce10a35fcf27e6e96b503640f784cd07e5ad6` antes de la ejecución.

```bash
curl -fsSL https://github.com/hapifhir/org.hl7.fhir.core/releases/download/6.9.12/validator_cli.jar \
  -o /tmp/publicschema-fhir-validator-6.9.12.jar
uv run --locked python examples/fhir-registry/official_validate.py \
  --prepare-cache --cache-home /tmp/publicschema-fhir-cache
uv run --locked python examples/fhir-registry/official_validate.py \
  --jar /tmp/publicschema-fhir-validator-6.9.12.jar \
  --cache-home /tmp/publicschema-fhir-cache \
  --output /tmp/publicschema-fhir-outcome.json
```

La preparación descarga explícitamente versiones fijas desde `https://packages2.fhir.org/packages/{name}/{version}`: `hl7.fhir.r5.core#5.0.0`, `hl7.fhir.xver-extensions#0.1.0`, `hl7.terminology.r5#6.2.0`, `hl7.fhir.uv.extensions.r5#5.2.0`, `hl7.terminology.r5#7.1.0`, `hl7.fhir.uv.extensions.r5#5.3.0` y `hl7.terminology#7.3.0`. Use una caché dedicada. Los paquetes existentes se conservan; un conjunto de versiones diferente se informa para su revisión. Se comprueban las versiones y los metadatos de los paquetes; a diferencia de los artefactos incluidos en el repositorio y del JAR, el ejemplo no fija byte a byte el contenido descargado en la caché.

La validación en sí prohíbe el acceso a la red en la configuración de la herramienta oficial, desactiva su recuperador de recursos, usa `-tx n/a`, fija R5 y una jurisdicción global, y activa las comprobaciones de referencias. Las invariantes de FHIR siguen activadas. El script envoltorio examina el OperationOutcome devuelto y termina con un fallo ante problemas de nivel error o fatal, aunque el proceso Java haya devuelto cero. Pase `--bundle PATH` para otro Bundle nativo.

Lea las advertencias y la información del resultado. En este modo sin conexión, las cantidades UCUM y el tipo MIME FHIR del ejemplo no pueden recibir validación de un servidor de terminología, y el enlace de código base de la cualificación de la organización no tiene ninguna fuente contra la que comprobarse. Por lo tanto, un recuento de errores en cero sigue siendo más limitado que la conformidad FHIR completa. Un intercambio real sigue necesitando sus perfiles elegidos, su política terminológica, la autoridad de la fuente y las comprobaciones de autorización de los consumidores.
