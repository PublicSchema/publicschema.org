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

from tests.schema_reader import bibliography, concept, property_, vocabulary

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


class TestConsentRecordConcept:
    def test_exists_and_concrete(self):
        cr = concept("ConsentRecord")
        assert cr["id"] == "ConsentRecord"
        assert cr.get("abstract") is not True

    def test_is_root_namespace(self):
        """ConsentRecord is universal, not domain-scoped."""
        cr = concept("ConsentRecord")
        assert cr.get("domain") in (None, "")

    def test_has_no_supertype(self):
        cr = concept("ConsentRecord")
        assert cr.get("supertypes", []) == []

    def test_multilingual_definition(self):
        cr = concept("ConsentRecord")
        for lang in ("en", "fr", "es"):
            assert lang in cr["definition"], f"Missing {lang} definition"
            assert cr["definition"][lang].strip()

    def test_definition_anchors_legal_basis_honesty(self):
        """First sentence frames consent as one of six bases, not the only basis."""
        cr = concept("ConsentRecord")
        defn = cr["definition"]["en"].lower()
        assert "six" in defn and "legal bas" in defn, (
            "ConsentRecord definition must anchor that consent is one of six legal bases"
        )

    def test_definition_anchors_bulk_intake(self):
        """Community intake is the operational norm; the schema does not distinguish it from office workflow."""
        cr = concept("ConsentRecord")
        defn = cr["definition"]["en"].lower()
        assert "bulk" in defn or "community intake" in defn or "community-intake" in defn, (
            "ConsentRecord definition must mention bulk / community intake as operational reality"
        )


class TestPrivacyNoticeConcept:
    def test_exists_and_concrete(self):
        pn = concept("PrivacyNotice")
        assert pn["id"] == "PrivacyNotice"
        assert pn.get("abstract") is not True

    def test_is_root_namespace(self):
        pn = concept("PrivacyNotice")
        assert pn.get("domain") in (None, "")

    def test_multilingual_definition(self):
        pn = concept("PrivacyNotice")
        for lang in ("en", "fr", "es"):
            assert lang in pn["definition"]
            assert pn["definition"][lang].strip()

    def test_has_effective_date_in_validity_group(self):
        """ADR-009 decision 14: PrivacyNotice Validity group covers effective_date, expiry_date, jurisdiction."""
        pn = concept("PrivacyNotice")
        assert "effective_date" in pn["properties"]
        validity = next(
            g for g in pn["property_groups"] if g["category"] == "consent_validity"
        )
        assert "effective_date" in validity["properties"]


class TestDataSubjectProperty:
    def test_type_is_party(self):
        ds = property_("data_subject")
        assert ds["type"] == "concept:Party"
        assert ds["references"] == "Party"

    def test_cardinality_single(self):
        ds = property_("data_subject")
        assert ds["cardinality"] == "single"

    def test_is_immutable_after_given(self):
        ds = property_("data_subject")
        assert ds.get("immutable_after_status") == "given"


class TestControllersProperty:
    def test_references_organization(self):
        c = property_("controllers")
        assert c["references"] == "Organization"
        assert c["type"] == "concept:Organization"

    def test_cardinality_multiple(self):
        """Plural on both ConsentRecord and PrivacyNotice. No singular controller variant."""
        c = property_("controllers")
        assert c["cardinality"] == "multiple"


class TestRecipientsProperty:
    def test_references_organization(self):
        r = property_("recipients")
        assert r["references"] == "Organization"

    def test_cardinality_multiple(self):
        r = property_("recipients")
        assert r["cardinality"] == "multiple"


class TestIndicatedByProperty:
    def test_references_agent(self):
        p = property_("indicated_by")
        assert p["references"] == "Agent"


class TestWitnessedByProperty:
    def test_references_person(self):
        p = property_("witnessed_by")
        assert p["references"] == "Person"

    def test_cardinality_multiple(self):
        p = property_("witnessed_by")
        assert p["cardinality"] == "multiple"


class TestVocabularies:
    def test_all_consent_vocabularies_load(self):
        for vid in CONSENT_VOCABULARIES:
            data = vocabulary(vid)
            assert data["id"] == vid, f"{vid}.yaml id mismatch"

    def test_consent_record_type_values(self):
        v = vocabulary("consent-record-type")
        codes = {val["code"] for val in v["values"]}
        assert codes == {"internal_record", "receipt"}

    def test_legal_basis_is_normative(self):
        """Law-locked values (GDPR Art 6(1)) are locked at normative."""
        v = vocabulary("legal-basis")
        assert v["maturity"] == "normative"

    def test_consent_status_is_candidate(self):
        """DPV-aligned lifecycle states justify candidate per ADR-009 decision 5."""
        v = vocabulary("consent-status")
        assert v["maturity"] == "candidate"

    def test_withdrawal_channel_includes_non_digital(self):
        """Paper, verbal, and community-worker channels are non-negotiable."""
        v = vocabulary("withdrawal-channel")
        codes = {val["code"] for val in v["values"]}
        assert {"paper", "verbal", "community_worker"} <= codes
        assert len(v["values"]) == 8


class TestImmutabilityAnnotation:
    def test_all_terms_fields_are_immutable(self):
        for prop_id in sorted(IMMUTABLE_AFTER_GIVEN):
            prop = property_(prop_id)
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
            prop = property_(prop_id)
            assert prop.get("immutable_after_status") is None, (
                f"{prop_id} must NOT carry immutable_after_status"
            )


class TestBibliographyInforms:
    def test_dpv_informs_both_concepts(self):
        bib = bibliography("w3c-dpv")
        concepts = set(bib["informs"]["concepts"])
        assert {"ConsentRecord", "PrivacyNotice"} <= concepts

    def test_iso_27560_informs_consent_record(self):
        bib = bibliography("iso-27560")
        assert "ConsentRecord" in bib["informs"]["concepts"]

    def test_iso_29184_informs_privacy_notice(self):
        bib = bibliography("iso-29184")
        assert "PrivacyNotice" in bib["informs"]["concepts"]

    def test_govstack_consent_informs_consent_record(self):
        bib = bibliography("govstack-consent")
        assert "ConsentRecord" in bib["informs"]["concepts"]
