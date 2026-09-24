# Funciones de las instalaciones

Use `AssetPartyRole` para una aserción necesaria de forma independiente sobre quién es propietario de un local físico,
quién lo explota o quién lo mantiene. Mantenga la identidad de la instalación separada de cada
actor y de su prestador institucional. Un campus escolar puede cambiar de operador
sin convertirse en otro campus; lo mismo se aplica a los locales agropecuarios y al
patrimonio inmobiliario de un hospital.

Este es un uso intersectorial de la relación sobre activos físicos.
`School`, `HealthFacility` y `AgriculturalFacility` conservan sus significados
distintos. Una `Farm` es una unidad económica de producción, y un `ProviderSite` puede ser
virtual. Ninguno se convierte en un activo físico por el mero hecho de tener un operador o
una dirección.

## Indicar la responsabilidad

El ejemplo usa el esquema de PublicSchema
`https://publicschema.org/vocab/asset-role-type` para `asset_role_type`. Ese esquema
también define `keeper` para un tenedor registrado.

| Código | Significado | No establece |
| --- | --- | --- |
| `owner` | El actor es propietario del activo físico identificado. | El título sobre la tierra, la propiedad del prestador institucional ni la explotación de la instalación. |
| `operator` | El actor explota el local identificado para su finalidad operativa. | La propiedad, el mantenimiento del local, la gobernanza escolar ni la responsabilidad de productor agropecuario. |
| `upkeep` | El actor es responsable del aprovisionamiento y el mantenimiento del local. | La identidad del prestador de servicios ni del propietario. |

Use una aserción separada para cada responsabilidad, incluso cuando un mismo actor tenga varias.
El campo sigue abierto: una fuente puede conservar en su lugar su propio esquema, siempre que ese
esquema publique sus significados y su URI acompañe al código. Una palabra no calificada como `manager` no resuelve estas
distinciones.

`asset_actor` identifica a una persona, una organización o un grupo, incluidos los
subtipos institucionales apropiados. Las instalaciones agropecuarias también registran a su operador
como un AssetPartyRole, de modo que un vivero explotado conjuntamente puede tener un
AssetPartyRole fechado cuyo actor es un InformalGroup. No reformule el grupo como una
Organization. Un agente de software no es un actor del activo.

## Mantener las direcciones separadas

`AssetAddressAssignment` asocia un activo físico con un Address durante un
período. Usa `subject_uri`, `assigned_address`, `address_purpose`, `start_date`
y `end_date`. El Address, la geometría, la Location geográfica con nombre y la instalación
física siguen siendo sujetos identificados por separado.

El ejemplo usa `physical` y `postal` del esquema de PublicSchema
`https://publicschema.org/vocab/address-purpose`. Un cambio postal no
afirma que la instalación se haya trasladado. Una posición para la dirección corresponde al
`location` del Address; una forma para un edificio corresponde a su `spatial_geometry`,
con una codificación y un sistema de referencia de coordenadas explícitos. La escuela del ejemplo
conserva su dirección física mientras su apartado postal cambia un mes después de que cambie su
operador.

La conversión de registros de origen de direcciones de instalaciones necesita una finalidad
de dirección indicada explícitamente para cada asignación. La [guía de conversión de fechas de relación](/docs/relationship-date-migration/)
describe la correspondencia de campos y la conversión de fechas. No infiere si la finalidad es física o postal
a partir del texto de la dirección.

## Leer los recorridos sintéticos

`examples/facility-roles/records.json` contiene tres historiales de patrimonio inmobiliario:

| Recorrido | Cambio | Aserciones conservadas de forma independiente |
| --- | --- | --- |
| Campus escolar Riverside | Un EducationProvider sustituye a otro como operador del local el 1 de julio de 2026. Su dirección postal cambia el 1 de agosto. | El campus, el propietario público, la organización de mantenimiento y la dirección física conservan sus identidades. Un ProviderSite separado vincula la impartición educativa con el campus; otro ProviderSite es enteramente virtual. |
| Local de secado y almacenamiento de granos | Una Person sustituye a otra como operador del almacén el 1 de marzo de 2026. La dirección postal cambia el 1 de abril. | El local conserva su identidad. Una ProducerOrganization tiene aserciones de propiedad y de mantenimiento identificadas por separado. La Farm y su responsabilidad de productor siguen siendo independientes. |
| Local del hospital East | La organización que mantiene el patrimonio inmobiliario cambia el 1 de septiembre de 2026. | El HealthFacility físico, el operador hospitalario institucional y el propietario público del patrimonio inmobiliario siguen siendo independientes y no cambian. |

Dos registros ServiceCapacityObservation describen además 160 plazas de aprendizaje con personal asignado
en la escuela y 42 camas con personal asignado en el hospital, cada una en un momento de observación
explícito. Ambas conservan su esquema de medida local y un QuantityValue con la unidad UCUM
`1`. Las observaciones remiten a las instalaciones físicas identificadas por separado,
no a sus organizaciones prestadoras. Estos recuentos fechados no establecen la disponibilidad
actual, la acreditación ni una correspondencia con un recurso FHIR.

El ejemplo del hospital responde a una pregunta intersectorial sobre el patrimonio inmobiliario. `health/HealthFacility`
tiene una correspondencia cercana con Location de FHIR R5, y el intercambio médico debe conservar los
recursos FHIR nativos seleccionados y sus identidades de origen.
`Location.managingOrganization` de FHIR R5 identifica a la organización responsable
del aprovisionamiento y el mantenimiento del local. Es una única referencia opcional, sin
un período de responsabilidad en ese elemento. Por lo tanto, un AssetPartyRole fechado
no es un sustituto exacto. Un código de operador o de propietario no debe hacerse corresponder allí
solo por su etiqueta. Consulte la [definición de Location de FHIR R5](https://hl7.org/fhir/R5/location-definitions.html#Location.managingOrganization)
y la [orientación de integración con FHIR](/docs/fhir-registry-integration/).

Las direcciones FHIR ya tienen un período de uso. Una aserción de dirección de un activo
necesaria de forma independiente no requiere duplicar un hecho de dirección médica nativo,
y la asignación en sí no es un Address de FHIR. Conserve la representación de origen
seleccionada y compare explícitamente la semántica de los intervalos antes de proyectar
fechas. Consulte [Address.period de FHIR R5](https://hl7.org/fhir/R5/datatypes-definitions.html#Address.period).

## Ejecutar el ejemplo

Desde la raíz del repositorio:

```bash
uv run --locked python examples/facility-roles/validate_profile.py
uv run --locked pytest tests/test_facility_roles.py
```

El perfil de ejemplo exige URI de instalación y de actor resueltos localmente y un
código de función o de finalidad de dirección declarado. Admite los tipos concretos de instalación, actor
y grupo que se enumeran en `validate_profile.py`. Los tipos adicionales y los
esquemas de origen requieren una decisión de perfil; la sintaxis del URI por sí sola no puede establecer
que un destino sea una instalación física o un actor permitido. El ejemplo usa
registros identificados de nivel superior para las referencias y no recupera URI remotos.

`start_date` y `end_date` incluyen ambos su día calendario, de modo que `end_date` es el
último día en que la responsabilidad está en vigor. Una función anterior que termina el 30 de junio y la
que la sustituye a partir del 1 de julio no se superponen. Se exige una fecha de fin igual o posterior a la fecha de inicio
cuando se conocen ambas fechas. Las fechas ausentes siguen siendo desconocidas, y `effective_on` devuelve un resultado desconocido
cuando esos límites ausentes impiden una respuesta afirmativa. No se impone ninguna regla de unicidad
a actores o funciones simultáneos; la exclusividad requiere una regla de la fuente
aplicable.

Las pruebas validan los mismos registros mediante el JSON Schema generado y
SHACL expandido con el contexto, y luego aplican el perfil de ejemplo. También muestran que un
URI bien formado que apunta a un sitio de prestador virtual supera el campo de actor del activo con forma de URI
del vocabulario, pero no cumple la regla de actor del perfil, y que un
grupo puede tener una responsabilidad fechada. Las referencias de dirección tipadas tienen comprobaciones
SHACL separadas. Son ejemplos ejecutables locales, no una aplicación en tiempo de ejecución ni una
afirmación de conformidad para quienes lo adopten.
