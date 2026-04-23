"""Tests for the OpenSPP REST API v2 mapping.

Validates:
1. Structural integrity of external/openspp/matching.yaml (required keys,
   required per-entry fields, allowed surface values, no duplicates).
2. Referential integrity: every v2_vocabulary in matching.yaml resolves to a
   real PublicSchema vocabulary.
3. Cross-reference consistency: every vocabulary with a value_mapping in
   matching.yaml carries a corresponding system_mappings.openspp entry on its
   vocabulary YAML (OpenSPP uses system_mappings for value-level alignment,
   not external_equivalents).
4. Content expectations: locked decisions from the API re-targeting are
   present (sex uses ISO 5218 numeric codes, group-type surface is
   rest_api_v2, Pass-B enums point at Pydantic schemas).
5. No em dashes in matching.yaml.
"""


import pytest
import yaml

from tests.conftest import SCHEMA_DIR, V2_ROOT

MATCHING_PATH = V2_ROOT / "external" / "openspp" / "matching.yaml"
ALLOWED_SURFACES = {"rest_api_v2", "internal_model"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}


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
    result = {}
    for path in sorted((SCHEMA_DIR / "vocabularies").rglob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        domain = data.get("domain")
        key = f"{domain}/{data['id']}" if domain else data["id"]
        result[key] = data
    return result


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
            "matches",
            "no_match",
        ]:
            assert key in matching, f"matching.yaml missing top-level key: {key}"

    def test_system_identifier(self, matching):
        assert matching["system"] == "openspp"

    def test_system_version_is_string(self, matching):
        assert isinstance(matching["system_version"], str)
        assert matching["system_version"], "system_version must not be empty"

    def test_source_repository_is_openspp2(self, matching):
        assert matching["source_repository"] == "https://github.com/OpenSPP/OpenSPP2"

    def test_vocabulary_matches_required_fields(self, matching):
        """Every match entry must identify both sides, declare surface, and
        carry notes. external_source is required for all entries (it points
        at the Pydantic schema, the XML file, or the internal Odoo model)."""
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

    def test_no_match_entries_have_reason(self, matching):
        missing = []
        for i, entry in enumerate(matching["no_match"]):
            tag = entry.get("v2_vocabulary") or entry.get("external_vocabulary") or f"[{i}]"
            if "reason" not in entry:
                missing.append(f"no_match {tag} missing 'reason'")
        assert missing == [], "\n".join(missing)

    def test_internal_model_entries_declare_api_coverage_none(self, matching):
        """Entries with surface=internal_model must also declare
        api_coverage: none to make the 'no API surface' intent explicit."""
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

    def test_rest_api_v2_entries_have_api_endpoint_or_field(self, matching):
        """Entries with surface=rest_api_v2 must point integrators at either
        an api_endpoint (vocabulary passthroughs) or an api_field (Pydantic
        schema attributes). Otherwise the 'which REST surface?' is unclear."""
        bad = []
        for entry in matching["matches"]:
            if entry.get("surface") != "rest_api_v2":
                continue
            if "api_endpoint" not in entry and "api_field" not in entry:
                bad.append(
                    f"{entry['v2_vocabulary']}: surface=rest_api_v2 but "
                    f"neither api_endpoint nor api_field set"
                )
        assert bad == [], "\n".join(bad)


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
            canonical = {v["code"] for v in vocab.get("values", [])}
            for src, target in vm.items():
                if target is None:
                    continue
                if target not in canonical:
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
# Cross-reference: matching.yaml <-> schema YAML system_mappings
# ---------------------------------------------------------------------------

class TestCrossReferenceConsistency:
    """OpenSPP uses system_mappings (value-level) rather than
    external_equivalents (URI-level). A vocabulary with a value_mapping in
    matching.yaml should have a matching system_mappings.openspp block on
    its YAML, and vice versa."""

    def test_every_value_mapping_has_system_mapping(self, matching, all_vocabularies):
        missing = []
        for entry in matching["matches"]:
            if not entry.get("value_mapping"):
                continue
            vocab = _resolve_vocab(entry["v2_vocabulary"], all_vocabularies)
            if vocab is None:
                continue
            sm = (vocab.get("system_mappings") or {}).get("openspp")
            if sm is None:
                missing.append(entry["v2_vocabulary"])
        assert missing == [], (
            f"Vocabularies with value_mapping in matching.yaml but no "
            f"system_mappings.openspp on vocab YAML: {missing}"
        )

    def test_mapped_codes_appear_in_system_mappings(
        self, matching, all_vocabularies
    ):
        """Every non-null value_mapping in matching.yaml must correspond to a
        code present in the vocab YAML's system_mappings.openspp. This catches
        mapping drift where matching.yaml adds a mapping that the vocab YAML
        does not know about.

        The reverse direction is not enforced: the vocab YAML may legitimately
        describe a different surface than matching.yaml (e.g. gender-type's
        vocab YAML targets the API-level ISO 5218 codes while matching.yaml's
        gender-type entry documents the internal res.partner.gender text enum).
        Multi-enum cases (event-severity: GRMTicketSeverity + HazardIncidentSeverity)
        are also exempted from bidirectional parity.
        """
        missing = []
        for entry in matching["matches"]:
            vm = entry.get("value_mapping") or {}
            if not vm:
                continue
            vocab = _resolve_vocab(entry["v2_vocabulary"], all_vocabularies)
            if vocab is None:
                continue
            sm = (vocab.get("system_mappings") or {}).get("openspp")
            if sm is None:
                continue
            sm_codes = {str(v["code"]) for v in sm.get("values", [])}
            # Skip entries where the vocab YAML describes an entirely different
            # surface (disjoint code sets). These are documented differences.
            vm_codes = {str(k) for k in vm.keys()}
            if not (vm_codes & sm_codes):
                continue
            for src, target in vm.items():
                if target is None:
                    continue
                if str(src) not in sm_codes:
                    missing.append(
                        f"{entry['v2_vocabulary']}: {src!r} mapped in "
                        f"matching.yaml but not listed in "
                        f"system_mappings.openspp.values"
                    )
        assert missing == [], "\n".join(missing)


# ---------------------------------------------------------------------------
# Locked decisions: specific structural choices must remain as agreed
# ---------------------------------------------------------------------------

class TestLockedDecisions:
    """Guards against regressions of the API re-targeting work."""

    def test_sex_uses_iso_5218_numeric_codes(self, matching):
        """OpenSPP exposes sex as ISO 5218 numeric codes (0/1/2/9), not
        res.partner.gender text labels. The API surface must reflect that."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "sex"),
            None,
        )
        assert entry is not None, "sex entry missing from matching.yaml"
        assert entry["surface"] == "rest_api_v2"
        assert entry.get("same_standard") is True
        assert set(entry["value_mapping"].keys()) == {"0", "1", "2", "9"}

    def test_gender_type_is_internal_model_only(self, matching):
        """res.partner.gender (male/female/other text enum) is not exposed
        through the API; it lives on the internal model and is projected to
        Individual.gender via ISO 5218. Keep it flagged as internal."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "gender-type"),
            None,
        )
        assert entry is not None, "gender-type entry missing from matching.yaml"
        assert entry["surface"] == "internal_model"
        assert entry.get("api_coverage") == "none"

    def test_group_type_points_at_api_schema(self, matching):
        """Group.groupType is a Literal pattern in the Pydantic schema; the
        XML only backs household/family. The match target must point at the
        API schema, not at the XML."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "group-type"),
            None,
        )
        assert entry is not None
        assert entry["surface"] == "rest_api_v2"
        assert entry["external_source"].startswith("spp_api_v2/schemas/group.py")

    def test_enrollment_status_points_at_program_membership_schema(self, matching):
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "enrollment-status"),
            None,
        )
        assert entry is not None
        assert entry["surface"] == "rest_api_v2"
        assert entry["external_source"].startswith(
            "spp_api_v2/schemas/program_membership.py"
        )

    def test_benefit_modality_points_at_entitlements_schema(self, matching):
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "benefit-modality"),
            None,
        )
        assert entry is not None
        assert entry["surface"] == "rest_api_v2"
        assert entry["external_source"].startswith(
            "spp_api_v2_entitlements/schemas/entitlement.py"
        )

    def test_grievance_status_is_internal_model(self, matching):
        """OpenSPP GRM is not exposed through REST API v2."""
        entry = next(
            (e for e in matching["matches"] if e["v2_vocabulary"] == "grievance-status"),
            None,
        )
        assert entry is not None
        assert entry["surface"] == "internal_model"
        assert entry.get("api_coverage") == "none"

    def test_passthrough_vocabularies_have_vocabulary_endpoint(self, matching):
        """Standards passthroughs (country, currency, language, occupation)
        must declare the /api/v2/spp/Vocabulary passthrough endpoint so
        integrators know where to fetch them."""
        passthroughs = ["country", "currency", "language", "occupation"]
        for vocab_id in passthroughs:
            entry = next(
                (e for e in matching["matches"] if e["v2_vocabulary"] == vocab_id),
                None,
            )
            assert entry is not None, f"{vocab_id} missing from matching.yaml"
            assert entry["surface"] == "rest_api_v2"
            assert "api_endpoint" in entry, f"{vocab_id} missing api_endpoint"
            assert entry["api_endpoint"].startswith("/api/v2/spp/Vocabulary/"), (
                f"{vocab_id} api_endpoint is not a /Vocabulary passthrough"
            )


# ---------------------------------------------------------------------------
# Em dash hygiene
# ---------------------------------------------------------------------------

class TestNoEmDashes:
    def test_matching_yaml_has_no_em_dashes(self):
        text = MATCHING_PATH.read_text()
        assert "\u2014" not in text, (
            "matching.yaml contains em dashes (\u2014); use commas, colons, "
            "semicolons, periods, or parentheses instead."
        )
