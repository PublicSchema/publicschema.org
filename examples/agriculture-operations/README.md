# Agriculture operations fixtures

These synthetic JSON-LD fixtures use the generated PublicSchema catalog keys.
Agriculture concepts use the `agri/` namespace and water authorization uses the
`environment/` namespace. Facility functions, service types and input product
categories are published codes; operators are `AssetPartyRole` records and
producer-organization members are `InstitutionalRole` records. Vessel, product
and irrigation quantities use UCUM units with `unit_scheme`
`http://unitsofmeasure.org`.

Native medical exchange examples, including veterinary medicines, are
maintained in [`examples/fhir-registry/`](../fhir-registry/), whose FHIR tests
carry the medical negative coverage.
