"""Invariants for the ConsentRecord / PrivacyNotice hierarchy introduced by ADR-009.

These tests guard the key decisions in ADR-009:
- ConsentRecord and PrivacyNotice are concrete root-namespace concepts.
- data_subject ranges over Party (Person or Group, not Farm).
- controllers, recipients, witnessed_by, indicated_by reference the right concepts.
- 10 new vocabularies load and carry the expected maturity and values.
- The declared terms-fields carry immutable_after_status: given, and non-terms fields do not.
- Bibliography informs links into the new concepts.
- ConsentRecord definition anchors honesty (six legal bases) and operational
  reality (bulk community intake).
"""

from __future__ import annotations

import yaml

from tests.conftest import SCHEMA_DIR


CONCEPTS = SCHEMA_DIR / "concepts"
PROPERTIES = SCHEMA_DIR / "properties"
VOCABULARIES = SCHEMA_DIR / "vocabularies"
BIBLIOGRAPHY = SCHEMA_DIR / "bibliography"


CONSENT_VOCABULARIES = [
    "consent-record-type",
    "legal-basis",
    "special-category-basis",
    "consent-status",
    "collection-medium",
    "consent-expression",
    "delegation-type",
    "withdrawal-channel",
    "recipient-role",
    "organization-type",
]

# Terms-fields: the properties whose values must not change after the record
# reaches status=given. Sourced from ADR-009 decision 12 and the plan.
IMMUTABLE_AFTER_GIVEN = {
    "data_subject",
    "controllers",
    "recipients",
    "recipient_role",
    "allowed_recipient_categories",
    "purposes",
    "personal_data_categories",
    "processing_operations",
    "legal_basis",
    "special_category_basis",
    "notice_ref",
    "notice_version",
    "effective_date",
    "jurisdiction",
    "collection_medium",
    "consent_expression",
}


def load(path):
    with path.open() as f:
        return yaml.safe_load(f)


class TestConsentRecordConcept:
    def test_exists_and_concrete(self):
        cr = load(CONCEPTS / "consent-record.yaml")
        assert cr["id"] == "ConsentRecord"
        assert cr.get("abstract") is not True

    def test_is_root_namespace(self):
        """ConsentRecord is universal, not domain-scoped."""
        cr = load(CONCEPTS / "consent-record.yaml")
        assert cr.get("domain") in (None, "")

    def test_has_no_supertype(self):
        cr = load(CONCEPTS / "consent-record.yaml")
        assert cr.get("supertypes", []) == []

    def test_multilingual_definition(self):
        cr = load(CONCEPTS / "consent-record.yaml")
        for lang in ("en", "fr", "es"):
            assert lang in cr["definition"], f"Missing {lang} definition"
            assert cr["definition"][lang].strip()

    def test_definition_anchors_legal_basis_honesty(self):
        """First sentence frames consent as one of six bases, not the only basis."""
        cr = load(CONCEPTS / "consent-record.yaml")
        defn = cr["definition"]["en"].lower()
        assert "six" in defn and "legal bas" in defn, (
            "ConsentRecord definition must anchor that consent is one of six legal bases"
        )

    def test_definition_anchors_bulk_intake(self):
        """Community intake is the operational norm; the schema does not distinguish it from office workflow."""
        cr = load(CONCEPTS / "consent-record.yaml")
        defn = cr["definition"]["en"].lower()
        assert "bulk" in defn or "community intake" in defn or "community-intake" in defn, (
            "ConsentRecord definition must mention bulk / community intake as operational reality"
        )


class TestPrivacyNoticeConcept:
    def test_exists_and_concrete(self):
        pn = load(CONCEPTS / "privacy-notice.yaml")
        assert pn["id"] == "PrivacyNotice"
        assert pn.get("abstract") is not True

    def test_is_root_namespace(self):
        pn = load(CONCEPTS / "privacy-notice.yaml")
        assert pn.get("domain") in (None, "")

    def test_multilingual_definition(self):
        pn = load(CONCEPTS / "privacy-notice.yaml")
        for lang in ("en", "fr", "es"):
            assert lang in pn["definition"]
            assert pn["definition"][lang].strip()

    def test_has_effective_date_in_validity_group(self):
        """ADR-009 decision 14: PrivacyNotice Validity group covers effective_date, expiry_date, jurisdiction."""
        pn = load(CONCEPTS / "privacy-notice.yaml")
        assert "effective_date" in pn["properties"]
        validity = next(
            g for g in pn["property_groups"] if g["category"] == "consent_validity"
        )
        assert "effective_date" in validity["properties"]


class TestDataSubjectProperty:
    def test_type_is_party(self):
        ds = load(PROPERTIES / "data_subject.yaml")
        assert ds["type"] == "concept:Party"
        assert ds["references"] == "Party"

    def test_cardinality_single(self):
        ds = load(PROPERTIES / "data_subject.yaml")
        assert ds["cardinality"] == "single"

    def test_is_immutable_after_given(self):
        ds = load(PROPERTIES / "data_subject.yaml")
        assert ds.get("immutable_after_status") == "given"


class TestControllersProperty:
    def test_references_organization(self):
        c = load(PROPERTIES / "controllers.yaml")
        assert c["references"] == "Organization"
        assert c["type"] == "concept:Organization"

    def test_cardinality_multiple(self):
        """Plural on both ConsentRecord and PrivacyNotice. No singular controller variant."""
        c = load(PROPERTIES / "controllers.yaml")
        assert c["cardinality"] == "multiple"


class TestRecipientsProperty:
    def test_references_organization(self):
        r = load(PROPERTIES / "recipients.yaml")
        assert r["references"] == "Organization"

    def test_cardinality_multiple(self):
        r = load(PROPERTIES / "recipients.yaml")
        assert r["cardinality"] == "multiple"


class TestIndicatedByProperty:
    def test_references_agent(self):
        p = load(PROPERTIES / "indicated_by.yaml")
        assert p["references"] == "Agent"


class TestWitnessedByProperty:
    def test_references_person(self):
        p = load(PROPERTIES / "witnessed_by.yaml")
        assert p["references"] == "Person"

    def test_cardinality_multiple(self):
        p = load(PROPERTIES / "witnessed_by.yaml")
        assert p["cardinality"] == "multiple"


class TestVocabularies:
    def test_all_consent_vocabularies_load(self):
        for vid in CONSENT_VOCABULARIES:
            data = load(VOCABULARIES / f"{vid}.yaml")
            assert data["id"] == vid, f"{vid}.yaml id mismatch"

    def test_consent_record_type_values(self):
        v = load(VOCABULARIES / "consent-record-type.yaml")
        codes = {val["code"] for val in v["values"]}
        assert codes == {"internal_record", "receipt"}

    def test_legal_basis_is_normative(self):
        """Law-locked values (GDPR Art 6(1)) are locked at normative."""
        v = load(VOCABULARIES / "legal-basis.yaml")
        assert v["maturity"] == "normative"

    def test_consent_status_is_candidate(self):
        """DPV-aligned lifecycle states justify candidate per ADR-009 decision 5."""
        v = load(VOCABULARIES / "consent-status.yaml")
        assert v["maturity"] == "candidate"

    def test_withdrawal_channel_includes_non_digital(self):
        """Paper, verbal, and community-worker channels are non-negotiable."""
        v = load(VOCABULARIES / "withdrawal-channel.yaml")
        codes = {val["code"] for val in v["values"]}
        assert {"paper", "verbal", "community_worker"} <= codes
        assert len(v["values"]) == 8


class TestImmutabilityAnnotation:
    def test_all_terms_fields_are_immutable(self):
        for prop_id in sorted(IMMUTABLE_AFTER_GIVEN):
            prop = load(PROPERTIES / f"{prop_id}.yaml")
            assert prop.get("immutable_after_status") == "given", (
                f"{prop_id} should carry immutable_after_status: given"
            )

    def test_lifecycle_and_evidence_fields_are_not_immutable(self):
        """Non-terms fields (status, withdrawal, evidence) must NOT be annotated."""
        non_terms = [
            "status",
            "withdrawal_channel",
            "withdrawal_reason",
            "refusal_reason",
            "signed_date",
            "verified_by",
            "verified_date",
            "evidence_ref",
        ]
        for prop_id in non_terms:
            prop = load(PROPERTIES / f"{prop_id}.yaml")
            assert prop.get("immutable_after_status") is None, (
                f"{prop_id} must NOT carry immutable_after_status"
            )


class TestBibliographyInforms:
    def test_dpv_informs_both_concepts(self):
        bib = load(BIBLIOGRAPHY / "w3c-dpv.yaml")
        concepts = set(bib["informs"]["concepts"])
        assert {"ConsentRecord", "PrivacyNotice"} <= concepts

    def test_iso_27560_informs_consent_record(self):
        bib = load(BIBLIOGRAPHY / "iso-27560.yaml")
        assert "ConsentRecord" in bib["informs"]["concepts"]

    def test_iso_29184_informs_privacy_notice(self):
        bib = load(BIBLIOGRAPHY / "iso-29184.yaml")
        assert "PrivacyNotice" in bib["informs"]["concepts"]

    def test_govstack_consent_informs_consent_record(self):
        bib = load(BIBLIOGRAPHY / "govstack-consent.yaml")
        assert "ConsentRecord" in bib["informs"]["concepts"]
