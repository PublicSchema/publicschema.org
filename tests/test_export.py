"""Tests for CSV and Excel export generation.

TDD: these tests define expected behavior before implementation.
"""

import csv
import io
from pathlib import Path

import pytest
from openpyxl import load_workbook

from build.build import build_vocabulary
from build.export import generate_concept_csv, generate_definition_xlsx, generate_template_xlsx
from tests.conftest import make_concept, make_property, make_vocabulary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_vocab_result(
    tmp_schema, write_concept, write_property, write_vocabulary
):
    """Build a vocabulary result with a concept that has vocabulary properties."""
    write_vocabulary("enrollment-status.yaml", make_vocabulary(
        id="enrollment-status",
        values=[
            {
                "code": "active",
                "label": {"en": "Active", "fr": "Actif", "es": "Activo"},
                "definition": {"en": "Currently active.", "fr": "Actif.", "es": "Activo."},
            },
            {
                "code": "suspended",
                "label": {"en": "Suspended", "fr": "Suspendu", "es": "Suspendido"},
                "definition": {"en": "Temporarily paused.", "fr": "Suspendu.", "es": "Suspendido."},
            },
        ],
    ))
    write_property("beneficiary.yaml", make_property(
        id="beneficiary", type="concept:Person",
        data_classification="personal",
    ))
    write_property("enrollment_status.yaml", make_property(
        id="enrollment_status", vocabulary="enrollment-status",
        data_classification="non_personal",
    ))
    write_property("enrollment_date.yaml", make_property(
        id="enrollment_date", type="date",
        data_classification="non_personal",
    ))
    write_concept("enrollment.yaml", make_concept(
        id="Enrollment",
        domain="sp",
        properties=["beneficiary", "enrollment_status", "enrollment_date"],
        convergence={"system_count": 6, "total_systems": 6, "notes": "Universal."},
    ))
    return build_vocabulary(tmp_schema)


# ---------------------------------------------------------------------------
# CSV tests
# ---------------------------------------------------------------------------

class TestConceptCSV:
    def test_csv_has_header_row(self, sample_vocab_result, tmp_path):
        generate_concept_csv("Enrollment", sample_vocab_result, tmp_path)
        csv_path = tmp_path / "sp" / "Enrollment.csv"
        reader = csv.DictReader(csv_path.open())
        assert set(reader.fieldnames) == {
            "property", "type", "cardinality",
            "definition", "vocabulary", "data_classification",
        }

    def test_csv_has_one_row_per_property(self, sample_vocab_result, tmp_path):
        generate_concept_csv("Enrollment", sample_vocab_result, tmp_path)
        csv_path = tmp_path / "sp" / "Enrollment.csv"
        reader = csv.DictReader(csv_path.open())
        rows = list(reader)
        assert len(rows) == 3

    def test_csv_property_values(self, sample_vocab_result, tmp_path):
        generate_concept_csv("Enrollment", sample_vocab_result, tmp_path)
        csv_path = tmp_path / "sp" / "Enrollment.csv"
        reader = csv.DictReader(csv_path.open())
        rows = {r["property"]: r for r in reader}

        assert rows["enrollment_status"]["vocabulary"] == "enrollment-status"
        assert rows["enrollment_date"]["type"] == "date"
        assert rows["beneficiary"]["data_classification"] == "personal"

    def test_csv_universal_concept_no_domain_dir(
        self, tmp_schema, write_concept, write_property, tmp_path
    ):
        """Universal concepts (no domain) write CSV directly in root."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        generate_concept_csv("Person", result, tmp_path)
        assert (tmp_path / "Person.csv").exists()


# ---------------------------------------------------------------------------
# Definition workbook tests
# ---------------------------------------------------------------------------

class TestDefinitionXLSX:
    def test_has_concept_sheet(self, sample_vocab_result, tmp_path):
        generate_definition_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-definition.xlsx")
        assert "Concept" in wb.sheetnames

    def test_concept_sheet_has_metadata(self, sample_vocab_result, tmp_path):
        generate_definition_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-definition.xlsx")
        ws = wb["Concept"]
        # Collect all cell values from column A and B
        all_values = []
        for r in range(1, ws.max_row + 1):
            a = ws.cell(row=r, column=1).value
            b = ws.cell(row=r, column=2).value
            if a:
                all_values.append((a, b))
        # Title row contains concept name
        assert any("Enrollment" in str(a) for a, _ in all_values)
        # Domain is shown as readable label
        data = {a: b for a, b in all_values if b is not None}
        assert any("Social Protection" in str(v) for v in data.values())

    def test_has_properties_sheet(self, sample_vocab_result, tmp_path):
        generate_definition_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-definition.xlsx")
        assert "Properties" in wb.sheetnames

    def test_properties_sheet_has_header_and_rows(self, sample_vocab_result, tmp_path):
        generate_definition_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-definition.xlsx")
        ws = wb["Properties"]
        headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
        assert "Property" in headers
        assert "Type" in headers
        assert "Definition (EN)" in headers
        # One header row + 3 property rows
        assert ws.max_row == 4

    def test_has_vocabulary_sheets(self, sample_vocab_result, tmp_path):
        generate_definition_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-definition.xlsx")
        assert "enrollment-status" in wb.sheetnames

    def test_vocabulary_sheet_has_values(self, sample_vocab_result, tmp_path):
        generate_definition_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-definition.xlsx")
        ws = wb["enrollment-status"]
        headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
        assert "Code" in headers
        assert "Label (EN)" in headers
        # Header + 2 values
        assert ws.max_row == 3

    def test_no_vocabulary_sheet_for_non_vocab_properties(
        self, tmp_schema, write_concept, write_property, tmp_path
    ):
        """Concepts with no vocabulary properties get no vocab sheets."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        generate_definition_xlsx("Person", result, tmp_path)
        wb = load_workbook(tmp_path / "Person-definition.xlsx")
        assert wb.sheetnames == ["Concept", "Properties"]


# ---------------------------------------------------------------------------
# Template workbook tests
# ---------------------------------------------------------------------------

class TestTemplateXLSX:
    def test_has_data_sheet(self, sample_vocab_result, tmp_path):
        generate_template_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-template.xlsx")
        assert "Data" in wb.sheetnames

    def test_row1_has_human_labels(self, sample_vocab_result, tmp_path):
        generate_template_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-template.xlsx")
        ws = wb["Data"]
        labels = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
        # Human-readable: underscores replaced, title case
        assert "Beneficiary" in labels
        assert "Enrollment status" in labels
        assert "Enrollment date" in labels

    def test_row2_has_property_ids(self, sample_vocab_result, tmp_path):
        generate_template_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-template.xlsx")
        ws = wb["Data"]
        ids = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
        assert "beneficiary" in ids
        assert "enrollment_status" in ids
        assert "enrollment_date" in ids

    def test_vocabulary_columns_have_data_validation(self, sample_vocab_result, tmp_path):
        generate_template_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-template.xlsx")
        ws = wb["Data"]
        # Find the enrollment_status column
        ids = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
        status_col = ids.index("enrollment_status") + 1
        # Check that data validation exists on the column
        validations = ws.data_validations.dataValidation
        col_letter = ws.cell(row=3, column=status_col).column_letter
        has_validation = any(
            col_letter in str(dv.sqref) for dv in validations
        )
        assert has_validation, "enrollment_status column should have data validation"

    def test_header_cells_have_comments(self, sample_vocab_result, tmp_path):
        generate_template_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-template.xlsx")
        ws = wb["Data"]
        # Row 1 (label row) should have comments with definitions
        has_comment = False
        for c in range(1, ws.max_column + 1):
            if ws.cell(row=1, column=c).comment is not None:
                has_comment = True
                break
        assert has_comment, "At least one header cell should have a comment"

    def test_rows_3_onward_are_empty(self, sample_vocab_result, tmp_path):
        generate_template_xlsx("Enrollment", sample_vocab_result, tmp_path)
        wb = load_workbook(tmp_path / "sp" / "Enrollment-template.xlsx")
        ws = wb["Data"]
        for c in range(1, ws.max_column + 1):
            assert ws.cell(row=3, column=c).value is None
