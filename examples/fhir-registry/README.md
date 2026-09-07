# Native FHIR registry example

Run from the repository root:

```bash
uv run --locked python examples/fhir-registry/validate.py
uv run --locked pytest tests/test_fhir_registry.py -q
```

`bundle.fhir.json` is native FHIR R5 5.0.0 (`application/fhir+json`), with human and veterinary medicinal definitions and a healthcare directory. `registry-links.json` is a separate ordinary JSON envelope using PublicSchema identities and record references. All records and clinical details are synthetic.

The default checker uses local official artifacts and makes no network requests. It checks structure and the documented link contract, not full FHIR conformance. The optional `official_validate.py` invokes the pinned HL7 Java validator during authoring. See the [integration guide](../../docs/fhir-registry-integration.md) for the exact contract, migration decisions, setup commands, and validation limits.
