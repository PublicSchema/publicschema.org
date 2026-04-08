"""Tests for the vocabulary sync infrastructure.

TDD: these tests define expected behavior before implementation.
"""

import json
import textwrap

import pytest
import yaml

from build.sync_standards import (
    merge_values,
    parse_csv,
    parse_fhir_codesystem,
    parse_github_json,
    parse_isco_json,
    parse_iso_xml,
    parse_semicolon_delimited,
    parse_tsv,
)


# ---------------------------------------------------------------------------
# Format handler tests
# ---------------------------------------------------------------------------


class TestParseFhirCodesystem:
    def test_extracts_codes_and_labels(self):
        data = json.dumps({
            "resourceType": "CodeSystem",
            "concept": [
                {"code": "male", "display": "Male", "definition": "Male"},
                {"code": "female", "display": "Female", "definition": "Female"},
                {"code": "other", "display": "Other", "definition": "Other"},
            ],
        })
        result = parse_fhir_codesystem(data)
        assert len(result) == 3
        assert result[0]["code"] == "male"
        assert result[0]["label"] == {"en": "Male"}
        assert result[0]["standard_code"] == "male"

    def test_derives_snake_case_from_display(self):
        """FHIR codes like 'M' become snake_case of display name."""
        data = json.dumps({
            "resourceType": "CodeSystem",
            "concept": [
                {"code": "M", "display": "Married"},
                {"code": "S", "display": "Never Married"},
                {"code": "T", "display": "Domestic partner"},
            ],
        })
        result = parse_fhir_codesystem(data)
        assert result[0]["code"] == "married"
        assert result[0]["standard_code"] == "M"
        assert result[1]["code"] == "never_married"
        assert result[2]["code"] == "domestic_partner"

    def test_handles_missing_display(self):
        data = json.dumps({
            "resourceType": "CodeSystem",
            "concept": [
                {"code": "UNK", "definition": "Unknown"},
            ],
        })
        result = parse_fhir_codesystem(data)
        assert result[0]["label"] == {"en": "UNK"}
        assert result[0]["code"] == "unk"

    def test_empty_concept_list(self):
        data = json.dumps({"resourceType": "CodeSystem", "concept": []})
        result = parse_fhir_codesystem(data)
        assert result == []


class TestParseGithubJson:
    def test_extracts_country_codes(self):
        data = json.dumps([
            {
                "name": "Australia",
                "alpha-2": "AU",
                "alpha-3": "AUS",
                "country-code": "036",
                "region": "Oceania",
            },
            {
                "name": "Brazil",
                "alpha-2": "BR",
                "alpha-3": "BRA",
                "country-code": "076",
                "region": "Americas",
            },
        ])
        result = parse_github_json(data)
        assert len(result) == 2
        assert result[0]["code"] == "au"
        assert result[0]["label"] == {"en": "Australia"}
        assert result[0]["standard_code"] == "AU"

    def test_empty_array(self):
        result = parse_github_json("[]")
        assert result == []


class TestParseIsoXml:
    def test_extracts_currencies(self):
        data = textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <ISO_4217 Pblshd="2024-06-25">
              <CcyTbl>
                <CcyNtry>
                  <CtryNm>UNITED STATES OF AMERICA (THE)</CtryNm>
                  <CcyNm>US Dollar</CcyNm>
                  <Ccy>USD</Ccy>
                  <CcyNbr>840</CcyNbr>
                  <CcyMnrUnts>2</CcyMnrUnts>
                </CcyNtry>
                <CcyNtry>
                  <CtryNm>EURO AREA</CtryNm>
                  <CcyNm>Euro</CcyNm>
                  <Ccy>EUR</Ccy>
                  <CcyNbr>978</CcyNbr>
                  <CcyMnrUnts>2</CcyMnrUnts>
                </CcyNtry>
              </CcyTbl>
            </ISO_4217>
        """)
        result = parse_iso_xml(data)
        assert len(result) == 2
        assert result[0]["code"] == "usd"
        assert result[0]["label"] == {"en": "US Dollar"}
        assert result[0]["standard_code"] == "USD"

    def test_skips_entries_without_currency_code(self):
        """Some entries (e.g., Antarctica) have no currency code."""
        data = textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <ISO_4217 Pblshd="2024-06-25">
              <CcyTbl>
                <CcyNtry>
                  <CtryNm>ANTARCTICA</CtryNm>
                  <CcyNm>No universal currency</CcyNm>
                </CcyNtry>
                <CcyNtry>
                  <CtryNm>JAPAN</CtryNm>
                  <CcyNm>Yen</CcyNm>
                  <Ccy>JPY</Ccy>
                  <CcyNbr>392</CcyNbr>
                  <CcyMnrUnts>0</CcyMnrUnts>
                </CcyNtry>
              </CcyTbl>
            </ISO_4217>
        """)
        result = parse_iso_xml(data)
        assert len(result) == 1
        assert result[0]["code"] == "jpy"

    def test_deduplicates_currencies(self):
        """Multiple countries can use the same currency (e.g., USD)."""
        data = textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <ISO_4217 Pblshd="2024-06-25">
              <CcyTbl>
                <CcyNtry>
                  <CtryNm>UNITED STATES</CtryNm>
                  <CcyNm>US Dollar</CcyNm>
                  <Ccy>USD</Ccy>
                  <CcyNbr>840</CcyNbr>
                  <CcyMnrUnts>2</CcyMnrUnts>
                </CcyNtry>
                <CcyNtry>
                  <CtryNm>ECUADOR</CtryNm>
                  <CcyNm>US Dollar</CcyNm>
                  <Ccy>USD</Ccy>
                  <CcyNbr>840</CcyNbr>
                  <CcyMnrUnts>2</CcyMnrUnts>
                </CcyNtry>
              </CcyTbl>
            </ISO_4217>
        """)
        result = parse_iso_xml(data)
        assert len(result) == 1


class TestParseTsv:
    def test_extracts_languages(self):
        data = "Id\tPart2B\tPart2T\tPart1\tScope\tLanguage_Type\tRef_Name\tComment\n"
        data += "eng\t\t\ten\tI\tL\tEnglish\t\n"
        data += "fra\t\t\tfr\tI\tL\tFrench\t\n"
        data += "spa\t\t\tes\tI\tL\tSpanish\t\n"
        result = parse_tsv(data)
        assert len(result) == 3
        assert result[0]["code"] == "eng"
        assert result[0]["label"] == {"en": "English"}
        assert result[0]["standard_code"] == "eng"

    def test_empty_tsv(self):
        data = "Id\tPart2B\tPart2T\tPart1\tScope\tLanguage_Type\tRef_Name\tComment\n"
        result = parse_tsv(data)
        assert result == []


class TestParseSemicolonDelimited:
    def test_extracts_scripts(self):
        data = textwrap.dedent("""\
            # ISO 15924 script codes
            # Some header comment
            Latn;215;Latin;latin;;2004-05-01;2004-05-29
            Cyrl;220;Cyrillic;cyrillique;;2004-05-01;2004-05-29
            Arab;160;Arabic;arabe;;2004-05-01;2004-05-29
        """)
        result = parse_semicolon_delimited(data)
        assert len(result) == 3
        assert result[0]["code"] == "latn"
        assert result[0]["label"] == {"en": "Latin"}
        assert result[0]["standard_code"] == "Latn"

    def test_skips_comment_lines(self):
        data = "# comment\n# another comment\n"
        result = parse_semicolon_delimited(data)
        assert result == []


class TestParseIscoJson:
    def test_extracts_all_levels(self):
        data = json.dumps([
            {
                "name": "1 - Managers",
                "children": [
                    {
                        "name": "11 - Chief executives, senior officials and legislators",
                        "children": [
                            {
                                "name": "111 - Legislators and senior officials",
                                "children": [
                                    {"name": "1111 - Legislators"},
                                    {"name": "1112 - Senior government officials"},
                                ],
                            },
                        ],
                    },
                    {
                        "name": "12 - Administrative and commercial managers",
                        "children": [],
                    },
                ],
            },
        ])
        result = parse_isco_json(data)
        codes = {r["standard_code"] for r in result}
        # All 4 levels should be present
        assert codes == {"1", "11", "12", "111", "1111", "1112"}

    def test_major_group_has_level_1_no_parent(self):
        data = json.dumps([
            {"name": "1 - Managers", "children": []},
        ])
        result = parse_isco_json(data)
        assert len(result) == 1
        assert result[0]["standard_code"] == "1"
        assert result[0]["level"] == 1
        assert result[0].get("parent_code") is None
        assert result[0]["code"] == "managers_1"

    def test_sub_major_group_has_level_2_with_parent(self):
        data = json.dumps([
            {
                "name": "1 - Managers",
                "children": [
                    {"name": "11 - Chief executives", "children": []},
                ],
            },
        ])
        result = parse_isco_json(data)
        sub_major = [r for r in result if r["standard_code"] == "11"][0]
        assert sub_major["level"] == 2
        assert sub_major["parent_code"] == "1"

    def test_minor_group_has_level_3(self):
        data = json.dumps([
            {
                "name": "1 - Managers",
                "children": [
                    {
                        "name": "11 - Chief executives",
                        "children": [
                            {"name": "111 - Legislators", "children": []},
                        ],
                    },
                ],
            },
        ])
        result = parse_isco_json(data)
        minor = [r for r in result if r["standard_code"] == "111"][0]
        assert minor["level"] == 3
        assert minor["parent_code"] == "11"

    def test_unit_group_has_level_4(self):
        data = json.dumps([
            {
                "name": "1 - Managers",
                "children": [
                    {
                        "name": "11 - Chief executives",
                        "children": [
                            {
                                "name": "111 - Legislators",
                                "children": [
                                    {"name": "1111 - Legislators"},
                                ],
                            },
                        ],
                    },
                ],
            },
        ])
        result = parse_isco_json(data)
        unit = [r for r in result if r["standard_code"] == "1111"][0]
        assert unit["level"] == 4
        assert unit["parent_code"] == "111"

    def test_empty_tree(self):
        result = parse_isco_json("[]")
        assert result == []


class TestParseCsv:
    def test_extracts_regions(self):
        # The UN M49 CSV from datasets/country-codes has many columns.
        # We need at least these for region extraction.
        header = "FIFA,Dial,MARC,is_independent,ISO3166-1-Alpha-2,ISO3166-1-Alpha-3,ISO3166-1-numeric,GAUL,FIPS,WMO,ISO4217-currency_alphabetic_code,ISO4217-currency_country_name,ISO4217-currency_minor_unit,ISO4217-currency_name,ISO4217-currency_numeric_code,CLDR display name,Capital,Continent,DS,Developed / Developing Countries,Edgar,FIFA,Geoname ID,Global Code,Global Name,IOC,ITU,Intermediate Region Code,Intermediate Region Name,MARC,Land Locked Developing Countries (LLDC),Languages,Least Developed Countries (LDC),M49,Region Code,Region Name,Sub-region Code,Sub-region Name,TLD,UNTERM Arabic Formal,UNTERM Arabic Short,UNTERM Chinese Formal,UNTERM Chinese Short,UNTERM English Formal,UNTERM English Short,UNTERM French Formal,UNTERM French Short,UNTERM Russian Formal,UNTERM Russian Short,UNTERM Spanish Formal,UNTERM Spanish Short,WMO,is_independent"
        row1 = 'AUS,61,as ,Yes,AU,AUS,036,17,AS,AU,AUD,"AUSTRALIA",2,"Australian Dollar",036,Australia,Canberra,OC,AUS,Developed,2V,AUS,2077456,True,World,AUS,AUS,,,as ,,,036,009,Oceania,053,"Australia and New Zealand",.au,,,,,,Australia,,,,,,,,AU,Yes'
        row2 = 'BRA,55,bl ,Yes,BR,BRA,076,37,BR,BZ,BRL,"BRAZIL",2,"Brazilian Real",986,Brazil,"Brasilia",SA,BR,Developing,D5,BRA,3469034,True,World,BRA,BRA,,,bl ,,,076,019,Americas,005,"South America",.br,,,,,,Brazil,,,,,,,,BZ,Yes'
        data = header + "\n" + row1 + "\n" + row2 + "\n"
        result = parse_csv(data)
        assert len(result) == 2
        assert result[0]["code"] == "au"
        assert result[0]["label"] == {"en": "Australia"}
        assert result[0]["standard_code"] == "036"


# ---------------------------------------------------------------------------
# Merge logic tests
# ---------------------------------------------------------------------------


class TestMergeValues:
    def test_adds_new_values(self):
        existing = [
            {
                "code": "male",
                "label": {"en": "Male", "fr": "Masculin"},
                "definition": {"en": "Male gender."},
            },
        ]
        parsed = [
            {"code": "male", "label": {"en": "Male"}, "standard_code": "male"},
            {"code": "female", "label": {"en": "Female"}, "standard_code": "female"},
        ]
        merged, report = merge_values(existing, parsed)
        assert len(merged) == 2
        codes = [v["code"] for v in merged]
        assert "female" in codes

    def test_preserves_existing_definitions(self):
        existing = [
            {
                "code": "male",
                "label": {"en": "Male"},
                "definition": {"en": "Hand-written definition."},
            },
        ]
        parsed = [
            {"code": "male", "label": {"en": "Male"}, "standard_code": "1"},
        ]
        merged, report = merge_values(existing, parsed)
        assert merged[0]["definition"] == {"en": "Hand-written definition."}

    def test_preserves_existing_translations(self):
        existing = [
            {
                "code": "male",
                "label": {"en": "Male", "fr": "Masculin", "es": "Masculino"},
                "definition": {"en": "Male."},
            },
        ]
        parsed = [
            {"code": "male", "label": {"en": "Male"}, "standard_code": "1"},
        ]
        merged, report = merge_values(existing, parsed)
        assert merged[0]["label"]["fr"] == "Masculin"
        assert merged[0]["label"]["es"] == "Masculino"

    def test_reports_removed_codes(self):
        existing = [
            {
                "code": "old_code",
                "label": {"en": "Old"},
                "definition": {"en": "Old."},
            },
        ]
        parsed = [
            {"code": "new_code", "label": {"en": "New"}, "standard_code": "new"},
        ]
        merged, report = merge_values(existing, parsed)
        assert "old_code" in report["removed"]

    def test_updates_standard_code(self):
        existing = [
            {
                "code": "male",
                "label": {"en": "Male"},
                "definition": {"en": "Male."},
            },
        ]
        parsed = [
            {"code": "male", "label": {"en": "Male"}, "standard_code": "1"},
        ]
        merged, report = merge_values(existing, parsed)
        assert merged[0]["standard_code"] == "1"

    def test_updates_english_label(self):
        existing = [
            {
                "code": "male",
                "label": {"en": "Mal"},
                "definition": {"en": "Male."},
            },
        ]
        parsed = [
            {"code": "male", "label": {"en": "Male"}, "standard_code": "1"},
        ]
        merged, report = merge_values(existing, parsed)
        assert merged[0]["label"]["en"] == "Male"

    def test_report_lists_added_codes(self):
        existing = []
        parsed = [
            {"code": "male", "label": {"en": "Male"}, "standard_code": "1"},
            {"code": "female", "label": {"en": "Female"}, "standard_code": "2"},
        ]
        merged, report = merge_values(existing, parsed)
        assert set(report["added"]) == {"male", "female"}

    def test_new_value_has_no_redundant_definition(self):
        """New values from sync do not get a definition that duplicates the label."""
        existing = []
        parsed = [
            {"code": "male", "label": {"en": "Male"}, "standard_code": "1"},
        ]
        merged, report = merge_values(existing, parsed)
        assert "definition" not in merged[0]

    def test_preserves_level_and_parent_code_on_new(self):
        """New values with level and parent_code carry them through merge."""
        existing = []
        parsed = [
            {
                "code": "managers",
                "label": {"en": "Managers"},
                "standard_code": "1",
                "level": 1,
            },
            {
                "code": "chief_executives",
                "label": {"en": "Chief executives"},
                "standard_code": "11",
                "level": 2,
                "parent_code": "1",
            },
        ]
        merged, report = merge_values(existing, parsed)
        assert merged[0]["level"] == 1
        assert merged[0].get("parent_code") is None
        assert merged[1]["level"] == 2
        assert merged[1]["parent_code"] == "1"

    def test_updates_level_and_parent_code_on_existing(self):
        """Existing values get level/parent_code updated from parsed data."""
        existing = [
            {
                "code": "chief_executives",
                "label": {"en": "Chief executives", "fr": "Dirigeants"},
                "standard_code": "11",
            },
        ]
        parsed = [
            {
                "code": "chief_executives",
                "label": {"en": "Chief executives"},
                "standard_code": "11",
                "level": 2,
                "parent_code": "1",
            },
        ]
        merged, report = merge_values(existing, parsed)
        assert merged[0]["level"] == 2
        assert merged[0]["parent_code"] == "1"
        # Translations preserved
        assert merged[0]["label"]["fr"] == "Dirigeants"
