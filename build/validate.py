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

from build.loader import load_all_yaml, load_vocabularies_with_paths, load_yaml

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

    meta = load_yaml(meta_path)
    meta_schema = _load_json_schema("meta.schema.json")
    errors.extend(_validate_against_schema(meta, meta_schema, "_meta.yaml"))
    if errors:
        return errors

    languages = meta.get("languages", ["en"])

    # Load all files
    concepts = load_all_yaml(schema_dir / "concepts")
    properties = load_all_yaml(schema_dir / "properties")
    vocabularies = load_all_yaml(schema_dir / "vocabularies")
    vocabularies_with_paths = load_vocabularies_with_paths(schema_dir / "vocabularies")
    bibliography = load_all_yaml(schema_dir / "bibliography")

    # Load categories (optional file)
    categories_path = schema_dir / "categories.yaml"
    categories = load_yaml(categories_path) if categories_path.exists() else {}
    if categories:
        categories_schema = _load_json_schema("categories.schema.json")
        errors.extend(_validate_against_schema(
            categories, categories_schema, "categories.yaml",
        ))
    category_ids = set(categories.keys())

    # Build lookup indexes.
    # concept_ids: bare short names (e.g. "Enrollment"), used for referential
    #   integrity checks where YAML references (supertypes, bibliography informs)
    #   also use bare names.
    # concept_keys: composite keys (e.g. "sp/Enrollment", "Person"), used to
    #   detect duplicate concept definitions that would silently overwrite each
    #   other in the build pipeline's internal keying.
    concept_ids = set()
    concept_keys: set[str] = set()
    for data in concepts.values():
        if "id" not in data:
            continue
        bare_id = data["id"]
        domain = data.get("domain")
        composite = f"{domain}/{bare_id}" if domain else bare_id
        concept_ids.add(bare_id)
        if composite in concept_keys:
            errors.append(ValidationError(
                bare_id,
                f"Duplicate concept key '{composite}': two concept files produce the same "
                f"domain-qualified identifier. Rename one of them.",
            ))
        concept_keys.add(composite)
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
        if "label" in data:
            errors.extend(_check_multilingual(
                data["label"], languages, filename, "label",
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

    # age_applicability cross-check against WG/CFM bibliography citations.
    # Each Washington Group instrument implies a set of age bands that every
    # cited property must include. Properties may declare additional bands
    # (e.g. difficulty_seeing is cited in WG-SS (adults) and in CFM (both
    # child bands)). The rule only enforces the minimum set implied by
    # the cited bibliographies.
    #
    # CFM citations imply at least one child band because individual CFM
    # items target either the 2-4 variant, the 5-17 variant, or both. We
    # therefore require any CFM-cited property to carry at least one of
    # {child_2_4, child_5_17}. A stricter "both bands" rule would fail on
    # items like difficulty_playing that exist only in the CFM 2-4 stem.
    WG_BAND_IMPLICATIONS = {
        "washington-group-ss": {"adult"},
        "washington-group-es": {"adult"},
    }
    CFM_CHILD_BANDS = {"child_2_4", "child_5_17"}
    property_bib_ids: dict[str, set[str]] = {pid: set() for pid in property_ids}
    for _bib_filename, bib_data in bibliography.items():
        bib_id = bib_data.get("id")
        if not bib_id:
            continue
        for pid in (bib_data.get("informs") or {}).get("properties", []) or []:
            if pid in property_bib_ids:
                property_bib_ids[pid].add(bib_id)
    for filename, data in properties.items():
        pid = data.get("id")
        if not pid:
            continue
        declared = set(data.get("age_applicability") or [])
        cites = property_bib_ids.get(pid, set())
        for bib_id, required in WG_BAND_IMPLICATIONS.items():
            if bib_id in cites and not required.issubset(declared):
                missing = sorted(required - declared)
                errors.append(ValidationError(
                    filename,
                    f"Property '{pid}' is cited in bibliography '{bib_id}' "
                    f"but age_applicability is missing required band(s): "
                    f"{', '.join(missing)}",
                ))
        if "washington-group-cfm" in cites and not (declared & CFM_CHILD_BANDS):
            errors.append(ValidationError(
                filename,
                f"Property '{pid}' is cited in bibliography "
                f"'washington-group-cfm' but age_applicability is missing "
                f"at least one child band (expected one of: "
                f"child_2_4, child_5_17)",
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

    # property_groups validation: category references and completeness
    for filename, data in concepts.items():
        groups = data.get("property_groups")
        if not groups:
            continue
        concept_id = data.get("id", filename)

        # Check that every category ID references a defined category
        for group in groups:
            cat = group.get("category", "")
            if cat and category_ids and cat not in category_ids:
                errors.append(ValidationError(
                    filename,
                    f"property_groups references category '{cat}' "
                    f"which is not defined in categories.yaml",
                ))

        # Completeness: every own + inherited property must appear in groups.
        # Collect all properties that should appear on this concept.
        all_expected = set()
        # Own properties
        for prop_entry in data.get("properties", []):
            pid = prop_entry["id"] if isinstance(prop_entry, dict) else prop_entry
            all_expected.add(pid)
        # Inherited properties (walk supertype chain)
        visited_supers: set[str] = set()
        _collect_inherited_ids(
            data, concept_by_id, all_expected, visited_supers,
        )
        # Collect all properties listed in groups
        grouped_ids = set()
        for group in groups:
            for pid in group.get("properties", []):
                grouped_ids.add(pid)

        missing = all_expected - grouped_ids
        if missing:
            missing_sorted = ", ".join(sorted(missing))
            errors.append(ValidationError(
                filename,
                f"property_groups on '{concept_id}' is missing properties: "
                f"{missing_sorted}. These would silently vanish from the "
                f"concept page.",
            ))

        # Check that grouped properties actually exist
        for group in groups:
            for pid in group.get("properties", []):
                if pid not in property_ids:
                    errors.append(ValidationError(
                        filename,
                        f"property_groups references property '{pid}' "
                        f"which is not defined in properties/",
                    ))

    return errors


def _collect_inherited_ids(
    concept_data: dict,
    concept_by_id: dict[str, tuple[str, dict]],
    result: set[str],
    visited: set[str],
) -> None:
    """Walk the supertype chain and collect all inherited property IDs."""
    for st in concept_data.get("supertypes", []):
        if st in visited or st not in concept_by_id:
            continue
        visited.add(st)
        _, parent_data = concept_by_id[st]
        for prop_entry in parent_data.get("properties", []):
            pid = prop_entry["id"] if isinstance(prop_entry, dict) else prop_entry
            result.add(pid)
        _collect_inherited_ids(parent_data, concept_by_id, result, visited)


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
