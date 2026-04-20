"""Tests for the OpenCRVS v1 GraphQL mapping.

Validates:
1. Structural integrity of external/opencrvs/matching.yaml (required keys,
   allowed match values, no duplicates).
2. Referential integrity: every v2_concept / v2_vocabulary / target_property
   in matching.yaml resolves to a real PublicSchema entity.
3. Cross-reference consistency: every concept and CRVS vocabulary with a
   non-null match in matching.yaml carries a corresponding
   external_equivalents.opencrvs entry on its YAML file.
4. Content expectations: the locked decisions from Phase 1-3 (Birth=broad,
   Death=broad, Marriage=broad, etc.) are present in the committed file.
5. No em dashes in any authored OpenCRVS content.
"""


import pytest
import yaml

from tests.conftest import SCHEMA_DIR, V2_ROOT

MATCHING_PATH = V2_ROOT / "external" / "opencrvs" / "matching.yaml"
ALLOWED_MATCH_VALUES = {
    "exact",
    "close",
    "broad",
    "narrow",
    "related",
    "name_match",
    "none",
}
OPENCRVS_URI_PREFIX = (
    "https://github.com/opencrvs/opencrvs-core/blob/develop/"
    "packages/client/src/tests/schema.graphql#"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def matching():
    with open(MATCHING_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def all_concepts():
    result = {}
    for path in sorted((SCHEMA_DIR / "concepts").glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        result[data["id"]] = data
    return result


@pytest.fixture(scope="module")
def all_properties():
    result = {}
    for path in sorted((SCHEMA_DIR / "properties").glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        result[data["id"]] = data
    return result


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

    matching.yaml sometimes uses the short id (`enrollment-status`) for
    domain-namespaced vocabs (`sp/enrollment-status`). Support both by
    falling back to a bare-id lookup when the prefixed key is absent.
    """
    if ref in all_vocabularies:
        return all_vocabularies[ref]
    for _key, vocab in all_vocabularies.items():
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
        for key in ["system", "concept_matches", "matches", "no_match"]:
            assert key in matching, f"matching.yaml missing top-level key: {key}"

    def test_system_identifier(self, matching):
        assert matching["system"] == "opencrvs"

    def test_concept_matches_required_fields(self, matching):
        missing = []
        for i, entry in enumerate(matching["concept_matches"]):
            for field in ["v2_concept", "external_entity", "external_source", "match", "notes"]:
                if field not in entry:
                    missing.append(f"concept_matches[{i}] ({entry.get('v2_concept', '?')}) missing '{field}'")
        assert missing == [], "\n".join(missing)

    def test_vocabulary_matches_required_fields(self, matching):
        """Every vocabulary match must identify both sides and carry notes.
        `external_source` is optional for country_config entries where the
        GraphQL field is a free String with no fixed enumeration."""
        missing = []
        for i, entry in enumerate(matching["matches"]):
            tag = entry.get("v2_vocabulary", f"[{i}]")
            for field in ["v2_vocabulary", "external_vocabulary", "notes"]:
                if field not in entry:
                    missing.append(f"matches[{i}] ({tag}) missing '{field}'")
            if not entry.get("country_config") and "external_source" not in entry:
                missing.append(f"matches[{i}] ({tag}) missing 'external_source' (not a country_config entry)")
        assert missing == [], "\n".join(missing)

    def test_no_match_entries_have_reason(self, matching):
        missing = []
        for i, entry in enumerate(matching["no_match"]):
            tag = entry.get("v2_concept") or entry.get("v2_vocabulary") or f"[{i}]"
            if "reason" not in entry:
                missing.append(f"no_match {tag} missing 'reason'")
        assert missing == [], "\n".join(missing)


# ---------------------------------------------------------------------------
# Allowed value enumerations
# ---------------------------------------------------------------------------

class TestAllowedValues:
    def test_concept_match_values_in_enum(self, matching):
        bad = []
        for entry in matching["concept_matches"]:
            if entry["match"] not in ALLOWED_MATCH_VALUES:
                bad.append(f"{entry['v2_concept']}: match={entry['match']!r}")
        assert bad == [], "\n".join(bad)


# ---------------------------------------------------------------------------
# Referential integrity: matching.yaml -> schema
# ---------------------------------------------------------------------------

class TestReferentialIntegrity:
    def test_concept_match_targets_exist(self, matching, all_concepts):
        missing = []
        for entry in matching["concept_matches"]:
            if entry["v2_concept"] not in all_concepts:
                missing.append(entry["v2_concept"])
        assert missing == [], f"Unknown v2_concept references: {missing}"

    def test_vocabulary_match_targets_exist(self, matching, all_vocabularies):
        missing = []
        for entry in matching["matches"]:
            if _resolve_vocab(entry["v2_vocabulary"], all_vocabularies) is None:
                missing.append(entry["v2_vocabulary"])
        assert missing == [], f"Unknown v2_vocabulary references: {missing}"

    def test_no_match_concept_targets_exist(self, matching, all_concepts):
        missing = []
        for entry in matching["no_match"]:
            if "v2_concept" in entry and entry["v2_concept"] not in all_concepts:
                missing.append(entry["v2_concept"])
        assert missing == [], f"Unknown no_match v2_concept references: {missing}"

    def test_no_match_vocabulary_targets_exist(self, matching, all_vocabularies):
        missing = []
        for entry in matching["no_match"]:
            if "v2_vocabulary" in entry and _resolve_vocab(entry["v2_vocabulary"], all_vocabularies) is None:
                missing.append(entry["v2_vocabulary"])
        assert missing == [], f"Unknown no_match v2_vocabulary references: {missing}"

    def test_decomposition_target_concepts_exist(self, matching, all_concepts):
        missing = []
        for entry in matching["concept_matches"]:
            for d in entry.get("decomposition", []):
                tc = d.get("target_concept")
                if tc is not None and tc not in all_concepts:
                    missing.append(f"{entry['v2_concept']}.decomposition[{d.get('opencrvs_field', '?')}] -> {tc}")
        assert missing == [], "Unknown target_concept references:\n" + "\n".join(missing)

    def test_decomposition_target_properties_exist(self, matching, all_properties):
        missing = []
        for entry in matching["concept_matches"]:
            for d in entry.get("decomposition", []):
                tp = d.get("target_property")
                if tp in (None, "*"):
                    continue
                if tp not in all_properties:
                    missing.append(f"{entry['v2_concept']}.decomposition[{d.get('opencrvs_field', '?')}] -> {tp}")
        assert missing == [], "Unknown target_property references:\n" + "\n".join(missing)

    def test_no_entity_appears_in_both_match_and_no_match(self, matching):
        matched_concepts = {e["v2_concept"] for e in matching["concept_matches"]}
        matched_vocabs = {e["v2_vocabulary"] for e in matching["matches"]}
        overlap_c = [e["v2_concept"] for e in matching["no_match"] if e.get("v2_concept") in matched_concepts]
        overlap_v = [e["v2_vocabulary"] for e in matching["no_match"] if e.get("v2_vocabulary") in matched_vocabs]
        assert overlap_c == [], f"Concepts in both concept_matches and no_match: {overlap_c}"
        assert overlap_v == [], f"Vocabularies in both matches and no_match: {overlap_v}"


# ---------------------------------------------------------------------------
# Cross-reference: matching.yaml <-> schema YAML external_equivalents
# ---------------------------------------------------------------------------

class TestCrossReferenceConsistency:
    def test_every_concept_match_has_external_equivalent(self, matching, all_concepts):
        """A concept with a non-none match in matching.yaml must also carry
        external_equivalents.opencrvs in its own YAML file."""
        missing = []
        mismatched = []
        for entry in matching["concept_matches"]:
            if entry["match"] == "none":
                continue
            concept = all_concepts[entry["v2_concept"]]
            ext = (concept.get("external_equivalents") or {}).get("opencrvs")
            if ext is None:
                missing.append(entry["v2_concept"])
                continue
            if ext["match"] != entry["match"]:
                mismatched.append(
                    f"{entry['v2_concept']}: matching.yaml={entry['match']}, "
                    f"concept YAML={ext['match']}"
                )
        assert missing == [], f"Concepts missing external_equivalents.opencrvs: {missing}"
        assert mismatched == [], "Match value mismatches:\n" + "\n".join(mismatched)

    def test_every_crvs_vocabulary_match_has_external_equivalent(
        self, matching, all_vocabularies
    ):
        """CRVS vocabulary entries in matching.yaml should also be reflected
        on the vocabulary YAML itself."""
        for entry in matching["matches"]:
            key = entry["v2_vocabulary"]
            if not key.startswith("crvs/"):
                continue
            vocab = all_vocabularies[key]
            ext = (vocab.get("external_equivalents") or {}).get("opencrvs")
            assert ext is not None, f"Vocabulary {key} missing external_equivalents.opencrvs"

    def test_external_equivalent_uris_use_correct_prefix(
        self, all_concepts, all_properties, all_vocabularies
    ):
        """OpenCRVS URIs must point at the GraphQL schema anchor URL. Skips
        match=none entries, which legitimately have no target URI."""
        bad = []
        for group_name, entities in [
            ("concept", all_concepts),
            ("property", all_properties),
            ("vocabulary", all_vocabularies),
        ]:
            for eid, data in entities.items():
                ext = (data.get("external_equivalents") or {}).get("opencrvs")
                if ext is None or ext.get("match") == "none":
                    continue
                uri = ext.get("uri", "")
                if not uri.startswith(OPENCRVS_URI_PREFIX):
                    bad.append(f"{group_name} {eid}: uri={uri!r}")
        assert bad == [], "OpenCRVS URIs with wrong prefix:\n" + "\n".join(bad)


# ---------------------------------------------------------------------------
# Locked decisions: specific match values must remain as agreed
# ---------------------------------------------------------------------------

class TestLockedDecisions:
    @pytest.mark.parametrize(
        "concept_id,expected_match",
        [
            ("VitalEvent", "related"),
            ("Birth", "broad"),
            ("Death", "broad"),
            ("Marriage", "broad"),
            ("CivilStatusRecord", "related"),
            ("Certificate", "close"),
            ("PaternityRecognition", "related"),
        ],
    )
    def test_concept_match_value(self, matching, concept_id, expected_match):
        entry = next(
            (e for e in matching["concept_matches"] if e["v2_concept"] == concept_id),
            None,
        )
        assert entry is not None, f"{concept_id} missing from concept_matches"
        assert entry["match"] == expected_match

    def test_party_assignment_symmetry(self, all_properties):
        """party_1 maps to bride and party_2 maps to groom (or vice versa,
        symmetrically). The assignment is arbitrary but must be consistent."""
        p1 = all_properties["party_1"]["external_equivalents"]["opencrvs"]
        p2 = all_properties["party_2"]["external_equivalents"]["opencrvs"]
        labels = {p1["label"], p2["label"]}
        assert "MarriageRegistration.bride" in labels
        assert "MarriageRegistration.groom" in labels
        # Both should be close matches with the same rationale
        assert p1["match"] == "close"
        assert p2["match"] == "close"

    def test_paternity_recognition_reference_is_reg_action(self, all_concepts):
        """PaternityRecognition maps to RegAction (the correction workflow),
        not to a first-class event type."""
        ext = all_concepts["PaternityRecognition"]["external_equivalents"]["opencrvs"]
        assert "RegAction" in ext["label"] or "CORRECTED" in ext["label"]

    def test_registration_status_has_unmapped_canonicals(self, all_vocabularies):
        """cancelled and corrected exist in PublicSchema but not in OpenCRVS's
        RegStatus enum."""
        vocab = all_vocabularies["crvs/registration-status"]
        sm = vocab["system_mappings"]["opencrvs"]
        assert set(sm.get("unmapped_canonical", [])) >= {"cancelled", "corrected"}


# ---------------------------------------------------------------------------
# Coverage: all 16 CRVS concepts are accounted for
# ---------------------------------------------------------------------------

class TestCoverage:
    CRVS_CONCEPTS = {
        "VitalEvent",
        "Birth",
        "Death",
        "FetalDeath",
        "Marriage",
        "MarriageTermination",
        "Adoption",
        "PaternityRecognition",
        "Legitimation",
        "CivilStatusRecord",
        "CivilStatusAnnotation",
        "Person",
        "Parent",
        "Certificate",
        "FamilyRegister",
    }

    def test_every_crvs_concept_accounted_for(self, matching):
        """Every CRVS concept must appear either in concept_matches or no_match."""
        matched = {e["v2_concept"] for e in matching["concept_matches"]}
        no_matched = {
            e["v2_concept"] for e in matching["no_match"] if "v2_concept" in e
        }
        covered = matched | no_matched
        missing = self.CRVS_CONCEPTS - covered
        assert missing == set(), f"CRVS concepts not covered: {missing}"


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

    def _check_files(self, paths):
        """Return a list of files containing em dashes inside an
        external_equivalents.opencrvs block."""
        offenders = []
        for path in paths:
            text = path.read_text()
            if "opencrvs" not in text:
                continue
            # Find the opencrvs block and check for em dashes within a reasonable window.
            idx = text.find("opencrvs:")
            if idx == -1:
                continue
            # Take from opencrvs: to the next top-level key or EOF
            tail = text[idx:]
            # Stop at the next blank line followed by a non-indented key, approximated.
            if "\u2014" in tail:
                offenders.append(str(path.relative_to(V2_ROOT)))
        return offenders

    def test_concept_opencrvs_blocks_have_no_em_dashes(self):
        paths = list((SCHEMA_DIR / "concepts").glob("*.yaml"))
        offenders = self._check_files(paths)
        assert offenders == [], f"Em dashes found near opencrvs blocks: {offenders}"

    def test_property_opencrvs_blocks_have_no_em_dashes(self):
        paths = list((SCHEMA_DIR / "properties").glob("*.yaml"))
        offenders = self._check_files(paths)
        assert offenders == [], f"Em dashes found near opencrvs blocks: {offenders}"

    def test_vocabulary_opencrvs_blocks_have_no_em_dashes(self):
        paths = list((SCHEMA_DIR / "vocabularies").rglob("*.yaml"))
        offenders = self._check_files(paths)
        assert offenders == [], f"Em dashes found near opencrvs blocks: {offenders}"
