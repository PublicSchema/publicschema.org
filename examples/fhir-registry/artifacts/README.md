# Published FHIR R5 artifacts

These are HL7 FHIR **R5 5.0.0** artifacts retrieved from its permanent release paths. [manifest.json](manifest.json) records each source URL, canonical/version, and SHA-256 digest.

- `fhir.schema.json.zip` is the original upstream archive, preserved byte for byte. Its `fhir.schema.json` member declares JSON Schema Draft 6.
- `base-profiles.zip` is a local ZIP container for eleven unmodified upstream `*.profile.json` documents. Member bytes are preserved; ZIP packaging is local. These are the published base StructureDefinitions for Bundle and the ten resource kinds used by the example. Their snapshots supply reference target constraints, not a new PublicSchema medical model.

The loader validates archive and profile-member hashes. Updating an artifact requires an explicit release/profile review, manifest update, and relevant tests. There is no automatic refresh.

FHIR specification content is made available under [CC0](https://hl7.org/fhir/R5/license.html). FHIR and the FHIR logo are HL7 trademarks. These archives do not redistribute the terminology datasets referenced by the profiles and do not grant rights to external code systems. HL7 does not endorse this integration.

The full Java validator and its package cache are deliberately separate authoring tools. They are not vendored, installed by normal project setup, or required by the example's default command.
