"""Tests for the schema content linter.

TDD: these tests define expected behavior before implementation.
"""

import pytest
import yaml

from build.lint import LintIssue, lint_schema_dir
from tests.conftest import make_concept, make_property, make_vocabulary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rule_codes(issues: list[LintIssue]) -> set[str]:
    """Extract the set of rule codes from lint issues."""
    return {i.rule for i in issues}


def _issues_for_rule(issues: list[LintIssue], rule: str) -> list[LintIssue]:
    """Filter issues to those matching a specific rule code."""
    return [i for i in issues if i.rule == rule]


# ---------------------------------------------------------------------------
# Clean file: zero issues on minimal valid schema
# ---------------------------------------------------------------------------


class TestCleanSchema:
    def test_minimal_valid_schema_has_no_issues(self, tmp_schema):
        """A minimal valid schema with no content should produce zero issues."""
        issues = lint_schema_dir(tmp_schema)
        assert issues == []

    def test_well_formed_content_has_no_issues(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Content that follows all rules should produce zero issues."""
        write_property("given_name.yaml", make_property(
            id="given_name",
            definition={
                "en": "The first given name of the person as recorded in the registry.",
                "fr": "Le premier prénom de la personne.",
                "es": "El primer nombre de pila de la persona.",
            },
        ))
        write_concept("person.yaml", make_concept(
            id="Person",
            maturity="candidate",
            definition={
                "en": "The unique individual human being who is a subject of record.",
                "fr": "L'individu unique qui fait l'objet d'un enregistrement.",
                "es": "El individuo único que es sujeto de registro.",
            },
            properties=["given_name"],
            external_equivalents={
                "semic": {
                    "label": "Person",
                    "uri": "http://www.w3.org/ns/person#Person",
                    "match": "exact",
                },
            },
        ))
        write_vocabulary("gender-type.yaml", make_vocabulary(
            id="gender-type",
            definition={
                "en": "The administrative gender of a person as recorded in a registry.",
                "fr": "Le genre administratif d'une personne.",
                "es": "El género administrativo de una persona.",
            },
            values=[
                {"code": "male", "label": {"en": "Male"}, "definition": {"en": "Male."}},
                {"code": "female", "label": {"en": "Female"}, "definition": {"en": "Female."}},
            ],
        ))
        issues = lint_schema_dir(tmp_schema)
        assert issues == []


# ---------------------------------------------------------------------------
# W001: Jargon in definitions
# ---------------------------------------------------------------------------


class TestW001Jargon:
    def test_detects_jargon_in_concept_definition(
        self, tmp_schema, write_concept
    ):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "A database table that stores entity records.",
                "fr": "Une table de base de données.",
                "es": "Una tabla de base de datos.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W001" in _rule_codes(issues)

    def test_detects_jargon_in_property_definition(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("ref.yaml", make_property(
            id="ref",
            definition={
                "en": "The foreign key to the parent endpoint.",
                "fr": "La clé étrangère.",
                "es": "La clave foránea.",
            },
        ))
        write_concept("thing.yaml", make_concept(
            id="Thing", properties=["ref"],
        ))
        issues = lint_schema_dir(tmp_schema)
        w001 = _issues_for_rule(issues, "W001")
        assert len(w001) >= 1

    def test_clean_definition_no_jargon(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(
            id="Person",
            definition={
                "en": "The unique individual human being who is a subject of record.",
                "fr": "L'individu unique.",
                "es": "El individuo único.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W001" not in _rule_codes(issues)

    def test_field_is_not_flagged(self, tmp_schema, write_concept):
        """The word 'field' has legitimate non-technical uses."""
        write_concept("area.yaml", make_concept(
            id="Area",
            definition={
                "en": "A measurement covering about the length of a football field.",
                "fr": "Un test.",
                "es": "Un test.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W001" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# W002: Short definitions
# ---------------------------------------------------------------------------


class TestW002ShortDefinition:
    def test_short_concept_definition(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "A record.",
                "fr": "Un enregistrement.",
                "es": "Un registro.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W002" in _rule_codes(issues)

    def test_short_property_definition(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("val.yaml", make_property(
            id="val",
            definition={
                "en": "The value.",
                "fr": "La valeur.",
                "es": "El valor.",
            },
        ))
        write_concept("thing.yaml", make_concept(
            id="Thing", properties=["val"],
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W002" in _rule_codes(issues)

    def test_adequate_definition_no_warning(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(
            id="Person",
            definition={
                "en": "The unique individual human being who is a subject of record in a system.",
                "fr": "L'individu unique.",
                "es": "El individuo único.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W002" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# W003: Circular definitions
# ---------------------------------------------------------------------------


class TestW003CircularDefinition:
    def test_circular_concept_definition(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(
            id="Person",
            definition={
                "en": "A Person is a person who exists.",
                "fr": "Une personne est une personne.",
                "es": "Una persona es una persona.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W003" in _rule_codes(issues)

    def test_circular_pascal_case(self, tmp_schema, write_concept):
        """PascalCase IDs should be normalized for comparison."""
        write_concept("gm.yaml", make_concept(
            id="GroupMembership",
            definition={
                "en": "A group membership is a link between a person and a group.",
                "fr": "Un test.",
                "es": "Un test.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W003" in _rule_codes(issues)

    def test_non_circular_definition(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(
            id="Person",
            definition={
                "en": "The unique individual human being who is a subject of record.",
                "fr": "L'individu unique.",
                "es": "El individuo único.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W003" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# W004: Definition missing terminal punctuation
# ---------------------------------------------------------------------------


class TestW004TerminalPunctuation:
    def test_missing_period(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "A record of some kind without a period at the end",
                "fr": "Un enregistrement sans point.",
                "es": "Un registro sin punto.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W004" in _rule_codes(issues)

    def test_folded_string_with_period(self, tmp_schema, write_concept):
        """YAML folded blocks add trailing newlines; must .strip() before checking."""
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "A record of some important kind in a system.\n",
                "fr": "Un enregistrement.\n",
                "es": "Un registro.\n",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W004" not in _rule_codes(issues)

    def test_closing_paren_is_ok(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "A record of some important kind (see also related concepts).",
                "fr": "Un enregistrement (voir aussi).",
                "es": "Un registro (ver también).",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "W004" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# S001: Em dash
# ---------------------------------------------------------------------------


class TestS001EmDash:
    def test_em_dash_in_candidate_definition_is_error(
        self, tmp_schema, write_concept
    ):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            maturity="candidate",
            definition={
                "en": "A record \u2014 an important one.",
                "fr": "Un enregistrement.",
                "es": "Un registro.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        s001 = _issues_for_rule(issues, "S001")
        assert len(s001) >= 1
        assert s001[0].severity == "error"

    def test_em_dash_in_draft_definition_is_warning(
        self, tmp_schema, write_concept
    ):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            maturity="draft",
            definition={
                "en": "A record \u2014 an important one.",
                "fr": "Un enregistrement.",
                "es": "Un registro.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        s001 = _issues_for_rule(issues, "S001")
        assert len(s001) >= 1
        assert s001[0].severity == "warning"

    def test_em_dash_in_label_is_flagged(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            label={"en": "Thing \u2014 Record", "fr": "Chose", "es": "Cosa"},
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "S001" in _rule_codes(issues)

    def test_em_dash_in_convergence_notes_is_warning(
        self, tmp_schema, write_concept
    ):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            maturity="candidate",
            convergence={"notes": "Some text \u2014 with em dash."},
        ))
        issues = lint_schema_dir(tmp_schema)
        s001 = _issues_for_rule(issues, "S001")
        assert len(s001) >= 1
        # Always warning for notes, even at candidate maturity
        assert all(i.severity == "warning" for i in s001)

    def test_no_em_dash_clean(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(id="Thing"))
        issues = lint_schema_dir(tmp_schema)
        assert "S001" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# S002: Label ends with period
# ---------------------------------------------------------------------------


class TestS002LabelPeriod:
    def test_label_with_period(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            label={"en": "Thing.", "fr": "Chose", "es": "Cosa"},
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "S002" in _rule_codes(issues)

    def test_label_without_period(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            label={"en": "Thing", "fr": "Chose", "es": "Cosa"},
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "S002" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# S003: Unexplained ALL CAPS
# ---------------------------------------------------------------------------


class TestS003AllCaps:
    def test_unknown_all_caps_word(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "This concept follows the ZXYWQ standard for records.",
                "fr": "Ce concept suit la norme.",
                "es": "Este concepto sigue la norma.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "S003" in _rule_codes(issues)

    def test_known_acronym_not_flagged(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "This concept follows the ISO and FHIR standards for interoperability.",
                "fr": "Ce concept suit les normes.",
                "es": "Este concepto sigue las normas.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "S003" not in _rule_codes(issues)

    def test_short_caps_not_flagged(self, tmp_schema, write_concept):
        """Words of 1-2 uppercase chars (e.g. 'ID', 'US') are not flagged."""
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={
                "en": "An ID used to identify a record in the US or EU systems.",
                "fr": "Un identifiant.",
                "es": "Un identificador.",
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "S003" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# E001: Malformed URI
# ---------------------------------------------------------------------------


class TestE001MalformedUri:
    def test_malformed_uri(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {"label": "Thing", "uri": "not-a-uri", "match": "exact"},
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E001" in _rule_codes(issues)

    def test_valid_uri(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {
                    "label": "Thing",
                    "uri": "http://example.org/Thing",
                    "match": "exact",
                },
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E001" not in _rule_codes(issues)

    def test_match_none_skips_uri_check(self, tmp_schema, write_concept):
        """Entries with match: none are gap documentation; no URI expected."""
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {"label": "Thing", "match": "none"},
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E001" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# E002: Match without URI
# ---------------------------------------------------------------------------


class TestE002MatchWithoutUri:
    def test_match_present_uri_missing(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {"label": "Thing", "match": "exact"},
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E002" in _rule_codes(issues)

    def test_match_none_not_flagged(self, tmp_schema, write_concept):
        """match: none is intentional gap documentation."""
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {"label": "Thing", "match": "none"},
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E002" not in _rule_codes(issues)

    def test_match_and_uri_present(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {
                    "label": "Thing",
                    "match": "exact",
                    "uri": "http://example.org/Thing",
                },
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E002" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# E003: URI without match
# ---------------------------------------------------------------------------


class TestE003UriWithoutMatch:
    def test_uri_present_match_missing(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {"label": "Thing", "uri": "http://example.org/Thing"},
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E003" in _rule_codes(issues)

    def test_both_present(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            external_equivalents={
                "semic": {
                    "label": "Thing",
                    "match": "exact",
                    "uri": "http://example.org/Thing",
                },
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "E003" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# V001: Single-value vocabulary
# ---------------------------------------------------------------------------


class TestV001SingleValue:
    def test_single_value_vocabulary(
        self, tmp_schema, write_vocabulary
    ):
        write_vocabulary("lone.yaml", make_vocabulary(
            id="lone",
            values=[
                {"code": "only", "label": {"en": "Only"}, "definition": {"en": "The only value."}},
            ],
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "V001" in _rule_codes(issues)

    def test_multi_value_vocabulary(self, tmp_schema, write_vocabulary):
        write_vocabulary("pair.yaml", make_vocabulary(id="pair"))
        issues = lint_schema_dir(tmp_schema)
        # make_vocabulary creates 1 value by default; let's add a second
        write_vocabulary("pair.yaml", make_vocabulary(
            id="pair",
            values=[
                {"code": "a", "label": {"en": "A"}, "definition": {"en": "First."}},
                {"code": "b", "label": {"en": "B"}, "definition": {"en": "Second."}},
            ],
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "V001" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# V002: Large unsynced vocabulary
# ---------------------------------------------------------------------------


class TestV002LargeUnsynced:
    def test_large_vocab_without_sync(self, tmp_schema, write_vocabulary):
        values = [
            {"code": f"val_{i}", "label": {"en": f"Value {i}"}, "definition": {"en": f"Value {i}."}}
            for i in range(51)
        ]
        write_vocabulary("big.yaml", make_vocabulary(id="big", values=values))
        issues = lint_schema_dir(tmp_schema)
        assert "V002" in _rule_codes(issues)

    def test_large_vocab_with_sync(self, tmp_schema, write_vocabulary):
        values = [
            {"code": f"val_{i}", "label": {"en": f"Value {i}"}, "definition": {"en": f"Value {i}."}}
            for i in range(51)
        ]
        write_vocabulary("big.yaml", make_vocabulary(
            id="big",
            values=values,
            sync={"source_url": "https://example.org/data.json", "format": "github-json"},
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "V002" not in _rule_codes(issues)

    def test_small_vocab_no_warning(self, tmp_schema, write_vocabulary):
        write_vocabulary("small.yaml", make_vocabulary(id="small"))
        issues = lint_schema_dir(tmp_schema)
        assert "V002" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# M001: Candidate concept without external equivalents
# ---------------------------------------------------------------------------


class TestM001NoExternalEquivalents:
    def test_candidate_without_externals(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing", maturity="candidate",
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M001" in _rule_codes(issues)

    def test_draft_without_externals_ok(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing", maturity="draft",
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M001" not in _rule_codes(issues)

    def test_candidate_with_externals_ok(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            maturity="candidate",
            external_equivalents={
                "semic": {
                    "label": "Thing",
                    "uri": "http://example.org/Thing",
                    "match": "exact",
                },
            },
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M001" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# M002: Normative concept without property_groups
# ---------------------------------------------------------------------------


class TestM002NoPropertyGroups:
    def test_normative_without_groups(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing", maturity="normative",
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M002" in _rule_codes(issues)

    def test_normative_abstract_exempt(self, tmp_schema, write_concept):
        """Abstract concepts don't have property_groups (their subtypes do)."""
        write_concept("event.yaml", make_concept(
            id="Event", maturity="normative", abstract=True,
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M002" not in _rule_codes(issues)

    def test_normative_with_groups_ok(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(id="name", category="identity"))
        # Write categories.yaml
        categories_path = tmp_schema / "categories.yaml"
        categories_path.write_text(yaml.dump(
            {"identity": {"label": {"en": "Identity"}}},
            allow_unicode=True,
        ))
        write_concept("thing.yaml", make_concept(
            id="Thing",
            maturity="normative",
            properties=["name"],
            property_groups=[
                {"category": "identity", "properties": ["name"]},
            ],
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M002" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# M003: Normative concept without convergence
# ---------------------------------------------------------------------------


class TestM003NoConvergence:
    def test_normative_without_convergence(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing", maturity="normative",
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M003" in _rule_codes(issues)

    def test_normative_with_convergence_ok(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing",
            maturity="normative",
            convergence={"system_count": 3, "total_systems": 6},
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M003" not in _rule_codes(issues)

    def test_draft_without_convergence_ok(self, tmp_schema, write_concept):
        write_concept("thing.yaml", make_concept(
            id="Thing", maturity="draft",
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "M003" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# X001: Unused category
# ---------------------------------------------------------------------------


class TestX001UnusedCategory:
    def test_unused_category(self, tmp_schema, write_concept, write_property):
        categories_path = tmp_schema / "categories.yaml"
        categories_path.write_text(yaml.dump({
            "identity": {"label": {"en": "Identity"}},
            "unused_cat": {"label": {"en": "Unused"}},
        }, allow_unicode=True))
        write_property("name.yaml", make_property(id="name", category="identity"))
        write_concept("thing.yaml", make_concept(
            id="Thing",
            properties=["name"],
            property_groups=[{"category": "identity", "properties": ["name"]}],
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "X001" in _rule_codes(issues)

    def test_all_categories_used(self, tmp_schema, write_concept, write_property):
        categories_path = tmp_schema / "categories.yaml"
        categories_path.write_text(yaml.dump({
            "identity": {"label": {"en": "Identity"}},
        }, allow_unicode=True))
        write_property("name.yaml", make_property(id="name", category="identity"))
        write_concept("thing.yaml", make_concept(
            id="Thing",
            properties=["name"],
            property_groups=[{"category": "identity", "properties": ["name"]}],
        ))
        issues = lint_schema_dir(tmp_schema)
        assert "X001" not in _rule_codes(issues)

    def test_no_categories_file_no_issue(self, tmp_schema):
        """No categories.yaml means nothing to check."""
        issues = lint_schema_dir(tmp_schema)
        assert "X001" not in _rule_codes(issues)


# ---------------------------------------------------------------------------
# main() exit code behavior
# ---------------------------------------------------------------------------


class TestMainExitCode:
    def test_exits_zero_on_warnings_only(
        self, tmp_schema, write_concept, monkeypatch
    ):
        """Warnings should not cause a non-zero exit."""
        # W002: short definition triggers a warning
        write_concept("thing.yaml", make_concept(
            id="Thing",
            definition={"en": "A record.", "fr": "Un test.", "es": "Un test."},
        ))
        from build import lint
        monkeypatch.setattr("sys.argv", ["lint", str(tmp_schema)])
        with pytest.raises(SystemExit) as exc_info:
            lint.main()
        assert exc_info.value.code == 0

    def test_exits_one_on_errors(
        self, tmp_schema, write_concept, monkeypatch
    ):
        """Errors should cause exit code 1."""
        # S001 on candidate with em dash is an error
        write_concept("thing.yaml", make_concept(
            id="Thing",
            maturity="candidate",
            definition={
                "en": "A record \u2014 an important one.",
                "fr": "Un enregistrement.",
                "es": "Un registro.",
            },
        ))
        from build import lint
        monkeypatch.setattr("sys.argv", ["lint", str(tmp_schema)])
        with pytest.raises(SystemExit) as exc_info:
            lint.main()
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# Integration: real schema
# ---------------------------------------------------------------------------


class TestRealSchema:
    def test_linter_runs_on_real_schema_without_crash(self):
        """The linter should be able to process the real schema directory."""
        from pathlib import Path
        schema_dir = Path(__file__).parent.parent / "schema"
        if not schema_dir.exists():
            pytest.skip("Real schema not available")
        issues = lint_schema_dir(schema_dir)
        # We expect some findings (that's the point), but no crashes
        assert isinstance(issues, list)
        for issue in issues:
            assert isinstance(issue, LintIssue)
            assert issue.rule
            assert issue.file
            assert issue.message
