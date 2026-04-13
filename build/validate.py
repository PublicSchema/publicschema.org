"""Validates PublicSchema YAML source files.

Checks:
1. YAML files conform to JSON Schema format specs
2. Referential integrity (property refs, vocabulary refs, concept refs)
3. Multilingual completeness (all configured languages present)
4. No orphaned properties (defined but unused by any concept)
"""

import json
import sys
from pathlib import Path

import jsonschema
import yaml


SCHEMAS_DIR = Path(__file__).parent / "schemas"


class ValidationError:
    """A single validation issue with context."""

    def __init__(self, file: str, message: str, severity: str = "error"):
        self.file = file
        self.message = message
        self.severity = severity

    def __str__(self):
        return f"{self.file}: {self.message}"

    def __repr__(self):
        return f"ValidationError({self.file!r}, {self.message!r}, severity={self.severity!r})"


def _load_json_schema(name: str) -> dict:
    path = SCHEMAS_DIR / name
    return json.loads(path.read_text())


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _load_all_yaml(directory: Path) -> dict[str, dict]:
    """Load all YAML files from a directory, keyed by filename."""
    result = {}
    if not directory.exists():
        return result
    for p in sorted(directory.rglob("*.yaml")):
        result[p.name] = _load_yaml(p)
    return result


def _load_vocabularies_with_paths(directory: Path) -> list[tuple[Path, dict]]:
    """Load vocabulary YAMLs with their relative paths for domain validation."""
    result = []
    if not directory.exists():
        return result
    for p in sorted(directory.rglob("*.yaml")):
        rel = p.relative_to(directory)
        result.append((rel, _load_yaml(p)))
    return result


def _validate_against_schema(
    data: dict, schema: dict, filename: str
) -> list[ValidationError]:
    """Validate a data dict against a JSON Schema."""
    errors = []
    validator = jsonschema.Draft202012Validator(schema)
    for error in validator.iter_errors(data):
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else ""
        location = f" at {path}" if path else ""
        errors.append(ValidationError(filename, f"{error.message}{location}"))
    return errors


def _check_multilingual(
    data: dict,
    languages: list[str],
    filename: str,
    field_path: str,
    maturity: str = "normative",
) -> list[ValidationError]:
    """Check that a multilingual dict has all required languages.

    At draft maturity, only English is required; missing translations for
    other languages produce warnings. At candidate or normative maturity,
    all configured languages are required (errors).
    """
    issues = []
    if not isinstance(data, dict):
        return issues
    for lang in languages:
        if lang not in data:
            if maturity == "draft" and lang != "en":
                issues.append(ValidationError(
                    filename,
                    f"Missing '{lang}' translation in {field_path}",
                    severity="warning",
                ))
            else:
                issues.append(ValidationError(
                    filename,
                    f"Missing '{lang}' translation in {field_path}",
                ))
    return issues


def validate_schema_dir(schema_dir: Path) -> list[ValidationError]:
    """Validate all YAML source files in a schema directory.

    Returns a list of ValidationError objects. Empty list means valid.
    """
    errors = []

    # Load meta
    meta_path = schema_dir / "_meta.yaml"
    if not meta_path.exists():
        errors.append(ValidationError("_meta.yaml", "Missing _meta.yaml"))
        return errors

    meta = _load_yaml(meta_path)
    meta_schema = _load_json_schema("meta.schema.json")
    errors.extend(_validate_against_schema(meta, meta_schema, "_meta.yaml"))
    if errors:
        return errors

    languages = meta.get("languages", ["en"])

    # Load all files
    concepts = _load_all_yaml(schema_dir / "concepts")
    properties = _load_all_yaml(schema_dir / "properties")
    vocabularies = _load_all_yaml(schema_dir / "vocabularies")
    vocabularies_with_paths = _load_vocabularies_with_paths(schema_dir / "vocabularies")
    bibliography = _load_all_yaml(schema_dir / "bibliography")

    # Build lookup indexes
    concept_ids = {data["id"] for data in concepts.values() if "id" in data}
    property_ids = {data["id"] for data in properties.values() if "id" in data}

    # Vocabularies are referenced by their canonical form: '<domain>/<id>' for
    # domain-scoped vocabularies (living in a subdirectory) and bare '<id>' for
    # universal ones (living at the vocabularies/ root). The YAML ``domain``
    # field must match the subdirectory name; YAML ``id`` must be the bare id.
    vocabulary_ids: set[str] = set()
    for rel_path, data in vocabularies_with_paths:
        if "id" not in data:
            continue
        filename = rel_path.name
        vocab_id = data["id"]
        yaml_domain = data.get("domain")
        parts = rel_path.parts
        if len(parts) == 1:
            # Root-level vocabulary: must have no domain field (or domain: null)
            if yaml_domain:
                errors.append(ValidationError(
                    filename,
                    f"Root-level vocabulary has 'domain: {yaml_domain}' but lives at vocabularies/ root; "
                    f"move the file to vocabularies/{yaml_domain}/ or remove the domain field",
                ))
                continue
            vocabulary_ids.add(vocab_id)
        else:
            # Subdirectory vocabulary: one directory level, domain must match
            subdir = parts[0]
            if len(parts) > 2:
                errors.append(ValidationError(
                    filename,
                    f"Vocabulary nested more than one level deep ({rel_path}); use vocabularies/<domain>/<id>.yaml",
                ))
                continue
            if yaml_domain != subdir:
                errors.append(ValidationError(
                    filename,
                    f"Vocabulary in 'vocabularies/{subdir}/' must declare 'domain: {subdir}' "
                    f"(found {yaml_domain!r})",
                ))
                continue
            if "/" in vocab_id:
                errors.append(ValidationError(
                    filename,
                    f"Vocabulary 'id' must be bare (no slash); got '{vocab_id}'. "
                    f"The domain segment is derived from the 'domain' field.",
                ))
                continue
            vocabulary_ids.add(f"{subdir}/{vocab_id}")

    # Load JSON Schemas for validation
    concept_schema = _load_json_schema("concept.schema.json")
    property_schema = _load_json_schema("property.schema.json")
    vocabulary_schema = _load_json_schema("vocabulary.schema.json")
    bibliography_schema = _load_json_schema("bibliography.schema.json")

    # Validate concepts
    for filename, data in concepts.items():
        errors.extend(_validate_against_schema(data, concept_schema, filename))
        # Multilingual checks on definition
        if "definition" in data:
            errors.extend(_check_multilingual(
                data["definition"], languages, filename, "definition",
                maturity=data.get("maturity", "draft"),
            ))

    # Validate properties
    for filename, data in properties.items():
        errors.extend(_validate_against_schema(data, property_schema, filename))
        if "definition" in data:
            errors.extend(_check_multilingual(
                data["definition"], languages, filename, "definition",
                maturity=data.get("maturity", "draft"),
            ))

    # Validate vocabularies
    for filename, data in vocabularies.items():
        errors.extend(_validate_against_schema(data, vocabulary_schema, filename))
        if "definition" in data:
            errors.extend(_check_multilingual(
                data["definition"], languages, filename, "definition",
                maturity=data.get("maturity", "draft"),
            ))
        # Check each value's multilingual fields (only require English;
        # synced vocabularies from external sources lack translations)
        for i, value in enumerate(data.get("values", [])):
            if "label" in value:
                errors.extend(_check_multilingual(
                    value["label"], ["en"], filename,
                    f"values[{i}].label",
                ))
            if "definition" in value:
                errors.extend(_check_multilingual(
                    value["definition"], ["en"], filename,
                    f"values[{i}].definition",
                ))

    # Referential integrity: concept -> property references
    used_property_ids = set()
    for filename, data in concepts.items():
        for prop_entry in data.get("properties", []):
            prop_id = prop_entry["id"] if isinstance(prop_entry, dict) else prop_entry
            used_property_ids.add(prop_id)
            if prop_id not in property_ids:
                errors.append(ValidationError(
                    filename,
                    f"Property '{prop_id}' referenced but not defined in properties/",
                ))

    # Referential integrity: property -> vocabulary references
    for filename, data in properties.items():
        vocab_ref = data.get("vocabulary")
        if vocab_ref and vocab_ref not in vocabulary_ids:
            errors.append(ValidationError(
                filename,
                f"Vocabulary '{vocab_ref}' referenced but not defined in vocabularies/",
            ))

    # Referential integrity: property -> concept references
    for filename, data in properties.items():
        concept_ref = data.get("references")
        if concept_ref and concept_ref not in concept_ids:
            errors.append(ValidationError(
                filename,
                f"Concept '{concept_ref}' referenced but not defined in concepts/",
            ))

    # Orphaned properties (defined but not used by any concept)
    for filename, data in properties.items():
        prop_id = data.get("id")
        if prop_id and prop_id not in used_property_ids:
            errors.append(ValidationError(
                filename,
                f"Property '{prop_id}' is defined but not used by any concept (orphaned)",
            ))

    # Referential integrity: concept -> supertype/subtype references
    for filename, data in concepts.items():
        for supertype in data.get("supertypes", []):
            if supertype not in concept_ids:
                errors.append(ValidationError(
                    filename,
                    f"Supertype '{supertype}' referenced but not defined in concepts/",
                ))
        for subtype in data.get("subtypes", []):
            if subtype not in concept_ids:
                errors.append(ValidationError(
                    filename,
                    f"Subtype '{subtype}' referenced but not defined in concepts/",
                ))

    # Supertype/subtype symmetry
    concept_by_id = {}
    for filename, data in concepts.items():
        cid = data.get("id")
        if cid:
            concept_by_id[cid] = (filename, data)

    for cid, (filename, data) in concept_by_id.items():
        for supertype in data.get("supertypes", []):
            if supertype in concept_by_id:
                parent_data = concept_by_id[supertype][1]
                if cid not in parent_data.get("subtypes", []):
                    errors.append(ValidationError(
                        filename,
                        f"'{cid}' lists '{supertype}' as supertype, but '{supertype}' does not list '{cid}' as subtype",
                    ))
        for subtype in data.get("subtypes", []):
            if subtype in concept_by_id:
                child_data = concept_by_id[subtype][1]
                if cid not in child_data.get("supertypes", []):
                    errors.append(ValidationError(
                        filename,
                        f"'{cid}' lists '{subtype}' as subtype, but '{subtype}' does not list '{cid}' as supertype",
                    ))

    # Validate bibliography entries
    for filename, data in bibliography.items():
        errors.extend(_validate_against_schema(data, bibliography_schema, filename))

    # Bibliography cross-reference integrity: every ID in `informs` must exist
    for filename, data in bibliography.items():
        informs = data.get("informs") or {}
        for cid in informs.get("concepts", []):
            if cid not in concept_ids:
                errors.append(ValidationError(
                    filename,
                    f"Bibliography 'informs.concepts' references concept '{cid}' which is not defined",
                ))
        for vid in informs.get("vocabularies", []):
            if vid not in vocabulary_ids:
                errors.append(ValidationError(
                    filename,
                    f"Bibliography 'informs.vocabularies' references vocabulary '{vid}' which is not defined",
                ))
        for pid in informs.get("properties", []):
            if pid not in property_ids:
                errors.append(ValidationError(
                    filename,
                    f"Bibliography 'informs.properties' references property '{pid}' which is not defined",
                ))

    # Vocabulary value code uniqueness
    for filename, data in vocabularies.items():
        codes = [v["code"] for v in data.get("values", []) if "code" in v]
        seen = set()
        for code in codes:
            if code in seen:
                errors.append(ValidationError(
                    filename,
                    f"Duplicate value code '{code}' in vocabulary",
                ))
            seen.add(code)

    return errors


def main():
    """CLI entry point for validation."""
    schema_dir = Path("schema")
    if len(sys.argv) > 1:
        schema_dir = Path(sys.argv[1])

    issues = validate_schema_dir(schema_dir)
    warnings = [i for i in issues if i.severity == "warning"]
    errors = [i for i in issues if i.severity == "error"]

    if warnings:
        print(f"{len(warnings)} warning(s):", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("Validation passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
