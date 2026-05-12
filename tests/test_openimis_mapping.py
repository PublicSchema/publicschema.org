"""Tests for the OpenIMIS hybrid FHIR R4 + internal-model mapping.

Validates:
1. Structural integrity of external/openimis/matching.yaml (required keys,
   required per-entry fields, allowed surface values, no duplicates).
2. Referential integrity: every v2_vocabulary in matching.yaml resolves to a
   real PublicSchema vocabulary.
3. Content expectations: locked decisions from the FHIR re-targeting are
   present (Insuree/Patient surface is fhir_r4, BeneficiaryStatus surface is
   internal_model with api_coverage=none, gender-type uses FHIR
   administrative-gender codes, etc.).
4. No em dashes in matching.yaml.
"""

import re
from functools import lru_cache

import pytest
import yaml

from tests.conftest import SCHEMA_DIR, V2_ROOT
from tests.schema_reader import raw_schema

MATCHING_PATH = V2_ROOT / "external" / "openimis" / "matching.yaml"
ALLOWED_SURFACES = {"fhir_r4", "internal_model"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
FHIR_RESOURCES = {
    "Patient",
    "Group",
    "Coverage",
    "Claim",
    "ClaimResponse",
    "Organization",
    "Location",
    "Practitioner",
    "PractitionerRole",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def matching():
    with open(MATCHING_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def all_vocabularies():
    """Vocabularies keyed as their build output key: 'id' or 'domain/id'."""
    return raw_schema()["vocabularies"]


def _resolve_vocab(ref: str, all_vocabularies: dict) -> dict | None:
    """Resolve a matching.yaml vocabulary reference.

    matching.yaml uses short ids (e.g. 'enrollment-status') even for
    domain-namespaced vocabs (sp/enrollment-status). Fall back to a bare-id
    lookup when the prefixed key is absent.
    """
    if ref in all_vocabularies:
        return all_vocabularies[ref]
    for vocab in all_vocabularies.values():
        if vocab["id"] == ref:
            return vocab
    return None


def _kebab_to_pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in value.split("-") if part)


@lru_cache
def _authored_permissible_value_keys() -> dict[str, set[str]]:
    """Return LinkML enum permissible-value keys by vocabulary id."""
    doc = yaml.safe_load((SCHEMA_DIR / "vocabularies.yaml").read_text()) or {}
    result = {}
    for enum_name, enum_def in (doc.get("enums") or {}).items():
        vocab_id = "-".join(
            part.lower() for part in re.split(r"(?<!^)(?=[A-Z])", enum_name) if part
        )
        result[vocab_id] = set((enum_def.get("permissible_values") or {}).keys())
    return result


def _valid_value_targets(ref: str, all_vocabularies: dict) -> set[str]:
    vocab = _resolve_vocab(ref, all_vocabularies)
    if vocab is None:
        return set()
    targets = {str(v["code"]) for v in vocab.get("values", [])}
    targets.update(
        str(v["standard_code"]) for v in vocab.get("values", []) if "standard_code" in v
    )
    targets.update(_authored_permissible_value_keys().get(vocab["id"], set()))
    targets.update(_authored_permissible_value_keys().get(_kebab_to_pascal(vocab["id"]), set()))
    return targets


# ---------------------------------------------------------------------------
# Structural validation
# ---------------------------------------------------------------------------

class TestStructure:
    def test_file_exists_and_parses(self, matching):
        assert isinstance(matching, dict)

    def test_required_top_level_keys(self, matching):
        for key in [
            "system",
            "system_version",
            "source_repository",
            "source_branch",
            "fhir_repository",
            "fhir_branch",
            "matches",
            "no_match",
        ]:
            assert key in matching, f"matching.yaml missing top-level key: {key}"

    def test_system_identifier(self, matching):
        assert matching["system"] == "openimis"

    def test_system_version_is_string(self, matching):
        assert isinstance(matching["system_version"], str)
        assert matching["system_version"], "system_version must not be empty"

    def test_fhir_repository_is_openimis_fhir(self, matching):
        assert matching["fhir_repository"] == (
            "https://github.com/openimis/openimis-be-api_fhir_r4_py"
        )

    def test_vocabulary_matches_required_fields(self, matching):
        """Every match entry must identify both sides, declare surface, and
        carry notes. external_source is required for all entries."""
        missing = []
        for i, entry in enumerate(matching["matches"]):
            tag = entry.get("v2_vocabulary", f"[{i}]")
            for field in [
                "v2_vocabulary",
                "external_vocabulary",
                "surface",
                "external_source",
                "confidence",
                "notes",
            ]:
                if field not in entry:
                    missing.append(f"matches[{i}] ({tag}) missing '{field}'")
        assert missing == [], "\n".join(missing)

    def test_fhir_r4_entries_declare_fhir_resource(self, matching):
        """Entries with surface=fhir_r4 must declare which FHIR resource they
        map to so integrators know where to look in the API."""
        bad = []
        for entry in matching["matches"]:
            if entry.get("surface") != "fhir_r4":
                continue
            if "fhir_resource" not in entry:
                bad.append(
                    f"{entry['v2_vocabulary']}: surface=fhir_r4 but "
                    f"fhir_resource not set"
                )
        assert bad == [], "\n".join(bad)

    def test_fhir_resource_values_in_known_set(self, matching):
        """fhir_resource values must be one of the known FHIR resource types."""
        bad = []
        for entry in matching["matches"]:
            resource = entry.get("fhir_resource")
            if resource is None:
                continue
            if resource not in FHIR_RESOURCES:
                bad.append(
                    f"{entry['v2_vocabulary']}: unknown fhir_resource={resource!r}"
                )
        assert bad == [], "\n".join(bad)

    def test_internal_model_entries_declare_api_coverage_none(self, matching):
        """Entries with surface=internal_model must also declare
        api_coverage: none to make the 'no FHIR surface' intent explicit."""
        bad = []
        for entry in matching["matches"]:
            if entry.get("surface") != "internal_model":
                continue
            if entry.get("api_coverage") != "none":
                bad.append(
                    f"{entry['v2_vocabulary']}: surface=internal_model but "
                    f"api_coverage={entry.get('api_coverage')!r}"
                )
        assert bad == [], "\n".join(bad)

    def test_no_match_entries_have_reason(self, matching):
        missing = []
        for i, entry in enumerate(matching["no_match"]):
            tag = (
                entry.get("v2_vocabulary")
                or entry.get("external_vocabulary")
                or f"[{i}]"
            )
            if "reason" not in entry:
                missing.append(f"no_match {tag} missing 'reason'")
        assert missing == [], "\n".join(missing)


# ---------------------------------------------------------------------------
# Allowed value enumerations
# ---------------------------------------------------------------------------

class TestAllowedValues:
    def test_surface_values_in_enum(self, matching):
        bad = []
        for entry in matching["matches"]:
            if entry["surface"] not in ALLOWED_SURFACES:
                bad.append(f"{entry['v2_vocabulary']}: surface={entry['surface']!r}")
        assert bad == [], "\n".join(bad)

    def test_confidence_values_in_enum(self, matching):
        bad = []
        for entry in matching["matches"]:
            if entry["confidence"] not in ALLOWED_CONFIDENCE:
                bad.append(
                    f"{entry['v2_vocabulary']}: confidence={entry['confidence']!r}"
                )
        assert bad == [], "\n".join(bad)


# ---------------------------------------------------------------------------
# Referential integrity: matching.yaml -> schema
# ---------------------------------------------------------------------------

class TestReferentialIntegrity:
    def test_vocabulary_match_targets_exist(self, matching, all_vocabularies):
        missing = []
        for entry in matching["matches"]:
            if _resolve_vocab(entry["v2_vocabulary"], all_vocabularies) is None:
                missing.append(entry["v2_vocabulary"])
        assert missing == [], f"Unknown v2_vocabulary references: {missing}"

    def test_no_match_vocabulary_targets_exist(self, matching, all_vocabularies):
        """v2_vocabulary references in no_match must resolve (external_vocabulary
        entries have no v2 target and are not checked)."""
        missing = []
        for entry in matching["no_match"]:
            if "v2_vocabulary" not in entry:
                continue
            if _resolve_vocab(entry["v2_vocabulary"], all_vocabularies) is None:
                missing.append(entry["v2_vocabulary"])
        assert missing == [], f"Unknown no_match v2_vocabulary references: {missing}"

    def test_value_mapping_targets_are_canonical_codes(self, matching, all_vocabularies):
        """Every non-null value_mapping target must be a canonical code in the
        referenced v2 vocabulary."""
        bad = []
        for entry in matching["matches"]:
            vm = entry.get("value_mapping") or {}
            vocab = _resolve_vocab(entry["v2_vocabulary"], all_vocabularies)
            if vocab is None:
                continue  # caught by test_vocabulary_match_targets_exist
            canonical = _valid_value_targets(entry["v2_vocabulary"], all_vocabularies)
            for src, target in vm.items():
                if target is None:
                    continue
                if str(target) not in canonical:
                    bad.append(
                        f"{entry['v2_vocabulary']}: {src!r} maps to {target!r} "
                        f"which is not a canonical code"
                    )
        assert bad == [], "Invalid value_mapping targets:\n" + "\n".join(bad)

    def test_no_vocabulary_in_both_match_and_no_match(self, matching):
        matched = {e["v2_vocabulary"] for e in matching["matches"]}
        overlap = [
            e["v2_vocabulary"]
            for e in matching["no_match"]
            if e.get("v2_vocabulary") in matched
        ]
        assert overlap == [], (
            f"Vocabularies in both matches and no_match: {overlap}"
        )


# ---------------------------------------------------------------------------
# Locked decisions: specific structural choices must remain as agreed
# ---------------------------------------------------------------------------

class TestLockedDecisions:
    """Guards against regressions of the FHIR re-targeting work."""

    def test_gender_type_uses_fhir_r4_surface(self, matching):
        """gender-type must target the FHIR R4 surface (administrative-gender
        CodeSystem via Patient.gender), not the raw tblGender internal model."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "gender-type"),
            None,
        )
        assert entry is not None, "gender-type entry missing from matching.yaml"
        assert entry["surface"] == "fhir_r4", (
            "gender-type should target fhir_r4 surface (administrative-gender)"
        )
        assert entry["fhir_resource"] == "Patient"

    def test_gender_type_uses_administrative_gender_codes(self, matching):
        """The FHIR administrative-gender CodeSystem uses male/female/other/unknown.
        The value_mapping keys must be those FHIR string codes, not tblGender
        single-letter codes (M/F/O)."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "gender-type"),
            None,
        )
        assert entry is not None
        vm_keys = set(entry["value_mapping"].keys())
        assert {"male", "female", "other", "unknown"}.issubset(vm_keys), (
            f"gender-type value_mapping should use FHIR administrative-gender codes; "
            f"got keys: {vm_keys}"
        )

    def test_enrollment_status_is_internal_model(self, matching):
        """BeneficiaryStatus (enrollment-status) lives in the social_protection
        Django module with no FHIR surface. Must be flagged as internal_model
        with api_coverage=none."""
        entry = next(
            (
                e
                for e in matching["matches"]
                if e["v2_vocabulary"] == "enrollment-status"
            ),
            None,
        )
        assert entry is not None, "enrollment-status missing from matching.yaml"
        assert entry["surface"] == "internal_model"
        assert entry.get("api_coverage") == "none"

    def test_group_role_is_internal_model(self, matching):
        """GroupIndividual.Role lives in openimis-be-individual_py with no
        FHIR surface. Must be flagged as internal_model with api_coverage=none."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "group-role"),
            None,
        )
        assert entry is not None, "group-role missing from matching.yaml"
        assert entry["surface"] == "internal_model"
        assert entry.get("api_coverage") == "none"

    def test_payment_status_is_internal_model(self, matching):
        """BenefitConsumptionStatus lives in openimis-be-payroll_py with no
        FHIR surface. Must be flagged as internal_model with api_coverage=none."""
        entry = next(
            (
                e
                for e in matching["matches"]
                if e["v2_vocabulary"] == "payment-status"
            ),
            None,
        )
        assert entry is not None, "payment-status missing from matching.yaml"
        assert entry["surface"] == "internal_model"
        assert entry.get("api_coverage") == "none"

    def test_group_type_uses_fhir_r4_surface(self, matching):
        """FamilyType is carried as a FHIR extension on the Group resource.
        The match target must use the fhir_r4 surface."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "group-type"),
            None,
        )
        assert entry is not None, "group-type missing from matching.yaml"
        assert entry["surface"] == "fhir_r4"
        assert entry["fhir_resource"] == "Group"

    def test_identifier_type_uses_fhir_r4_surface(self, matching):
        """IdentificationType is carried in Patient.identifier type coding.
        The match target must use the fhir_r4 surface."""
        entry = next(
            (
                e
                for e in matching["matches"]
                if e["v2_vocabulary"] == "identifier-type"
            ),
            None,
        )
        assert entry is not None, "identifier-type missing from matching.yaml"
        assert entry["surface"] == "fhir_r4"
        assert entry["fhir_resource"] == "Patient"

    def test_fhir_r4_sources_reference_fhir_module(self, matching):
        """All fhir_r4 entries must cite files within the
        api_fhir_r4/ module directory so citations are traceable."""
        bad = []
        for entry in matching["matches"]:
            if entry.get("surface") != "fhir_r4":
                continue
            src = entry.get("external_source", "")
            if not src.startswith("api_fhir_r4/"):
                bad.append(
                    f"{entry['v2_vocabulary']}: external_source={src!r} does "
                    f"not start with api_fhir_r4/"
                )
        assert bad == [], "\n".join(bad)

    def test_internal_model_sources_reference_django_module_paths(self, matching):
        """All internal_model entries must cite a Django module path ending in
        .py, not a FHIR module path."""
        bad = []
        for entry in matching["matches"]:
            if entry.get("surface") != "internal_model":
                continue
            src = entry.get("external_source", "")
            if not src.endswith(".py"):
                bad.append(
                    f"{entry['v2_vocabulary']}: external_source={src!r} should "
                    f"be a .py Django model file"
                )
        assert bad == [], "\n".join(bad)


# ---------------------------------------------------------------------------
# Em dash hygiene
# ---------------------------------------------------------------------------

class TestNoEmDashes:
    def test_matching_yaml_has_no_em_dashes(self):
        text = MATCHING_PATH.read_text()
        assert "—" not in text, (
            "matching.yaml contains em dashes (—); use commas, colons, "
            "semicolons, periods, or parentheses instead."
        )
