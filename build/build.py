"""Builds PublicSchema outputs from YAML source files.

Reads all YAML files from schema/ and generates:
1. vocabulary.json: full vocabulary as structured JSON
2. context.jsonld: JSON-LD context mapping IDs to URIs
3. schemas/*.schema.json: one JSON Schema per concept (for VC validation)
"""

import json
import sys
from pathlib import Path

import yaml


# Type mappings from YAML types to JSON Schema
TYPE_MAP = {
    "string": {"type": "string"},
    "date": {"type": "string", "format": "date"},
    "datetime": {"type": "string", "format": "date-time"},
    "integer": {"type": "integer"},
    "decimal": {"type": "number"},
    "boolean": {"type": "boolean"},
    "uri": {"type": "string", "format": "uri"},
}

# Type mappings from YAML types to JSON-LD @type coercion values.
# Only non-string types need coercion; plain strings are left as bare URIs.
JSONLD_TYPE_COERCION = {
    "date": "xsd:date",
    "datetime": "xsd:dateTime",
    "integer": "xsd:integer",
    "decimal": "xsd:decimal",
    "boolean": "xsd:boolean",
    "uri": "@id",
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _load_all_yaml(directory: Path) -> dict[str, dict]:
    result = {}
    if not directory.exists():
        return result
    for p in sorted(directory.glob("*.yaml")):
        data = _load_yaml(p)
        if "id" in data:
            result[data["id"]] = data
    return result


def _normalize_property_entry(entry) -> dict:
    """Normalize a property entry to {id}."""
    if isinstance(entry, str):
        return {"id": entry}
    return {"id": entry["id"]}


def _compute_uri(base_uri: str, domain: str | None, id_str: str) -> str:
    """Compute a URI with optional domain namespace segment."""
    if domain:
        return f"{base_uri}{domain}/{id_str}"
    return f"{base_uri}{id_str}"


def _compute_path(domain: str | None, id_str: str) -> str:
    """Compute a URL path with optional domain namespace segment."""
    if domain:
        return f"/{domain}/{id_str}"
    return f"/{id_str}"


def _compute_property_domain_namespace(
    prop_id: str,
    concepts_raw: dict[str, dict],
    properties_raw: dict[str, dict] | None = None,
) -> str | None:
    """Derive a property's domain namespace from the concepts that use it.

    If the property has an explicit ``domain_override`` field, that value
    is used directly (None for universal, a domain code for domain-specific).
    Otherwise, if all concepts using this property share the same non-null
    domain, the property gets that domain. Otherwise it's universal (None).
    """
    # Check for explicit override in the property's source YAML
    if properties_raw and prop_id in properties_raw:
        prop_data = properties_raw[prop_id]
        if "domain_override" in prop_data:
            return prop_data["domain_override"]

    domains = set()
    for concept_data in concepts_raw.values():
        for entry in concept_data.get("properties", []):
            pid = entry["id"] if isinstance(entry, dict) else entry
            if pid == prop_id:
                domains.add(concept_data.get("domain"))
    # Only assign a domain if all using concepts share exactly one non-null domain
    if len(domains) == 1:
        sole_domain = next(iter(domains))
        if sole_domain is not None:
            return sole_domain
    return None


def _compute_vocabulary_domain_namespace(
    vocab_id: str,
    properties_raw: dict[str, dict],
    concepts_raw: dict[str, dict],
) -> str | None:
    """Derive a vocabulary's domain namespace from the properties that reference it.

    If all properties referencing this vocabulary share the same non-null
    domain namespace, the vocabulary gets that domain. Otherwise it's universal.
    """
    domains = set()
    for prop_id, prop_data in properties_raw.items():
        if prop_data.get("vocabulary") == vocab_id:
            prop_ns = _compute_property_domain_namespace(prop_id, concepts_raw, properties_raw)
            domains.add(prop_ns)
    if len(domains) == 1:
        sole_domain = next(iter(domains))
        if sole_domain is not None:
            return sole_domain
    return None


def _property_to_json_schema(prop_data: dict, vocabularies: dict) -> dict:
    """Convert a property definition to a JSON Schema property definition."""
    prop_type = prop_data.get("type", "string")
    cardinality = prop_data.get("cardinality", "single")
    vocab_ref = prop_data.get("vocabulary")

    # If property has a vocabulary, generate enum constraint
    if vocab_ref and vocab_ref in vocabularies:
        vocab = vocabularies[vocab_ref]
        codes = [v["code"] for v in vocab.get("values", [])]
        item_schema = {"type": "string", "enum": codes}
    elif prop_type.startswith("concept:"):
        # Reference to another concept: accept object or string
        item_schema = {"type": ["object", "string"]}
    else:
        item_schema = dict(TYPE_MAP.get(prop_type, {"type": "string"}))

    if cardinality == "multiple":
        return {"type": "array", "items": item_schema}
    return item_schema


def build_vocabulary(schema_dir: Path) -> dict:
    """Build the full vocabulary output from YAML source files.

    Returns a dict with keys: meta, concepts, properties, vocabularies,
    context, concept_schemas.
    """
    meta = _load_yaml(schema_dir / "_meta.yaml")
    base_uri = meta.get("base_uri", "https://publicschema.org/")

    concepts_raw = _load_all_yaml(schema_dir / "concepts")
    properties_raw = _load_all_yaml(schema_dir / "properties")
    vocabularies_raw = _load_all_yaml(schema_dir / "vocabularies")

    # Compute property domains (which concepts use each property)
    property_domains: dict[str, list[str]] = {
        pid: [] for pid in properties_raw
    }
    for concept_id, concept_data in concepts_raw.items():
        for entry in concept_data.get("properties", []):
            prop_id = entry["id"] if isinstance(entry, dict) else entry
            if prop_id in property_domains:
                property_domains[prop_id].append(concept_id)

    # Build output concepts
    out_concepts = {}
    for concept_id, data in concepts_raw.items():
        domain = data.get("domain")
        out_concepts[concept_id] = {
            "id": concept_id,
            "domain": domain,
            "uri": _compute_uri(base_uri, domain, concept_id),
            "path": _compute_path(domain, concept_id),
            "maturity": data.get("maturity"),
            "definition": data.get("definition", {}),
            "properties": [
                _normalize_property_entry(e)
                for e in data.get("properties", [])
            ],
            "subtypes": data.get("subtypes", []),
            "supertypes": data.get("supertypes", []),
            "convergence": data.get("convergence"),
        }

    # Build output properties
    out_properties = {}
    for prop_id, data in properties_raw.items():
        prop_ns = _compute_property_domain_namespace(prop_id, concepts_raw, properties_raw)
        out_properties[prop_id] = {
            "id": prop_id,
            "uri": _compute_uri(base_uri, prop_ns, prop_id),
            "path": _compute_path(prop_ns, prop_id),
            "maturity": data.get("maturity"),
            "definition": data.get("definition", {}),
            "type": data.get("type"),
            "cardinality": data.get("cardinality"),
            "vocabulary": data.get("vocabulary"),
            "references": data.get("references"),
            "used_by": property_domains.get(prop_id, []),
            "schema_org_equivalent": data.get("schema_org_equivalent"),
            "data_classification": data.get("data_classification"),
            "convergence": data.get("convergence"),
        }

    # Build output vocabularies
    out_vocabularies = {}
    for vocab_id, data in vocabularies_raw.items():
        vocab_ns = _compute_vocabulary_domain_namespace(
            vocab_id, properties_raw, concepts_raw,
        )
        vocab_base = _compute_uri(base_uri, vocab_ns, f"vocab/{vocab_id}")
        values = []
        for v in data.get("values", []):
            value_out = {
                "code": v["code"],
                "uri": f"{vocab_base}/{v['code']}",
                "label": v.get("label", {}),
                "standard_code": v.get("standard_code"),
                "definition": v.get("definition", {}),
            }
            if v.get("level") is not None:
                value_out["level"] = v["level"]
            if v.get("parent_code") is not None:
                value_out["parent_code"] = v["parent_code"]
            values.append(value_out)
        out_vocabularies[vocab_id] = {
            "id": vocab_id,
            "domain": vocab_ns,
            "uri": vocab_base,
            "path": _compute_path(vocab_ns, f"vocab/{vocab_id}"),
            "maturity": data.get("maturity"),
            "definition": data.get("definition", {}),
            "standard": data.get("standard"),
            "values": values,
            "system_mappings": data.get("system_mappings"),
        }

    # Build JSON-LD context (uses the computed URIs from output objects).
    # Context URIs get a .jsonld suffix so they dereference on static hosts
    # (GitHub Pages) where content negotiation is unavailable.
    context_map = {
        "@vocab": base_uri,
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "schema": "https://schema.org/",
        "ps": "https://publicschema.org/meta/",
    }
    for concept_id, concept_out in out_concepts.items():
        context_map[concept_id] = concept_out["uri"] + ".jsonld"
    for prop_id, prop_out in out_properties.items():
        prop_uri = prop_out["uri"] + ".jsonld"
        prop_type = properties_raw[prop_id].get("type", "string")
        # concept:X references get @type: @id
        if prop_type.startswith("concept:"):
            context_map[prop_id] = {"@id": prop_uri, "@type": "@id"}
        elif prop_type in JSONLD_TYPE_COERCION:
            context_map[prop_id] = {
                "@id": prop_uri,
                "@type": JSONLD_TYPE_COERCION[prop_type],
            }
        else:
            context_map[prop_id] = prop_uri
        # Add camelCase alias for schema.org equivalent properties
        schema_eq = properties_raw[prop_id].get("schema_org_equivalent")
        if schema_eq and schema_eq.startswith("schema:"):
            alias = schema_eq.split(":", 1)[1]
            # Alias points to the same context entry as the original property
            context_map[alias] = context_map[prop_id]
    version = meta.get("version", "0.1.0")
    # Use major.minor for context versioning (drop patch)
    version_short = ".".join(version.split(".")[:2])
    context = {
        "@id": f"{base_uri}ctx/v{version_short}.jsonld",
        "@context": context_map,
    }

    # Build JSON Schema per concept
    concept_schemas = {}
    for concept_id, data in concepts_raw.items():
        schema_props = {}
        for entry in data.get("properties", []):
            norm = _normalize_property_entry(entry)
            prop_id = norm["id"]
            if prop_id in properties_raw:
                schema_props[prop_id] = _property_to_json_schema(
                    properties_raw[prop_id], vocabularies_raw,
                )

        concept_domain = data.get("domain")
        schema_base = f"{base_uri}{concept_domain}/" if concept_domain else base_uri
        concept_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"{schema_base}schemas/{concept_id}.schema.json",
            "title": concept_id,
            "type": "object",
            "properties": schema_props,
        }
        concept_schemas[concept_id] = concept_schema

    # Build credential schemas (VC envelope wrapping concept schemas)
    credentials_raw = _load_all_yaml(schema_dir / "credentials")
    credential_schemas = {}
    for cred_id, cred_data in credentials_raw.items():
        subject_concept_id = cred_data.get("subject_concept")
        if not subject_concept_id or subject_concept_id not in concept_schemas:
            continue

        # Start with the subject concept's properties as credentialSubject
        subject_schema = dict(concept_schemas[subject_concept_id])
        subject_props = dict(subject_schema.get("properties", {}))

        # Add nested included concepts as sub-objects
        for included_id in cred_data.get("included_concepts", []):
            if included_id in concept_schemas:
                nested = dict(concept_schemas[included_id])
                nested_obj = {
                    "type": "object",
                    "properties": nested.get("properties", {}),
                }
                if "required" in nested:
                    nested_obj["required"] = nested["required"]
                # Use lowercase concept name as the property key
                subject_props[included_id[0].lower() + included_id[1:]] = nested_obj

        # Build VC envelope schema
        credential_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"{base_uri}schemas/credentials/{cred_id}.schema.json",
            "title": cred_id,
            "type": "object",
            "properties": {
                "@context": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "type": {
                    "type": "array",
                    "items": {"type": "string"},
                    "contains": {"const": cred_id},
                },
                "credentialSubject": {
                    "type": "object",
                    "properties": subject_props,
                },
            },
        }
        credential_schemas[cred_id] = credential_schema

    return {
        "meta": meta,
        "concepts": out_concepts,
        "properties": out_properties,
        "vocabularies": out_vocabularies,
        "context": context,
        "concept_schemas": concept_schemas,
        "credential_schemas": credential_schemas,
    }


def write_outputs(result: dict, dist_dir: Path):
    """Write build outputs to the dist directory."""
    from build.export import generate_all_downloads

    dist_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir = dist_dir / "schemas"
    schemas_dir.mkdir(exist_ok=True)

    # vocabulary.json (everything except context and concept_schemas)
    vocabulary = {
        "meta": result["meta"],
        "concepts": result["concepts"],
        "properties": result["properties"],
        "vocabularies": result["vocabularies"],
    }
    (dist_dir / "vocabulary.json").write_text(
        json.dumps(vocabulary, indent=2, ensure_ascii=False) + "\n"
    )

    # context.jsonld
    (dist_dir / "context.jsonld").write_text(
        json.dumps(result["context"], indent=2, ensure_ascii=False) + "\n"
    )

    # Per-concept JSON Schemas
    for concept_id, schema in result["concept_schemas"].items():
        filename = f"{concept_id.lower()}.schema.json"
        (schemas_dir / filename).write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
        )

    # Credential schemas (VC envelope)
    cred_schemas = result.get("credential_schemas", {})
    if cred_schemas:
        creds_dir = schemas_dir / "credentials"
        creds_dir.mkdir(exist_ok=True)
        for cred_id, schema in cred_schemas.items():
            filename = f"{cred_id}.schema.json"
            (creds_dir / filename).write_text(
                json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
            )

    # CSV and Excel downloads per concept
    downloads_dir = dist_dir / "downloads"
    generate_all_downloads(result, downloads_dir)


def main():
    """CLI entry point for build."""
    schema_dir = Path("schema")
    dist_dir = Path("dist")

    if len(sys.argv) > 1:
        schema_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        dist_dir = Path(sys.argv[2])

    result = build_vocabulary(schema_dir)
    write_outputs(result, dist_dir)
    print(f"Built {len(result['concepts'])} concepts, "
          f"{len(result['properties'])} properties, "
          f"{len(result['vocabularies'])} vocabularies.")


if __name__ == "__main__":
    main()
