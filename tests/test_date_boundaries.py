"""The published end_date states its boundary, so merged datasets agree on the last effective day."""
import pytest
from rdflib import URIRef
from rdflib.namespace import SKOS

END_DATE = URIRef("https://publicschema.org/end_date")
SCHEMA_END_DATE = URIRef("http://schema.org/endDate")


@pytest.mark.parametrize("language,first_inactive_day", [
    ("en", "the first day on which it no longer applies"),
    ("es", "el primer día en que ya no se aplica"),
    ("fr", "le premier jour où il ne s'applique plus"),
])
def test_end_date_is_the_first_day_it_no_longer_applies(built_vocabulary, language, first_inactive_day):
    definition = built_vocabulary["properties"]["end_date"]["definition"][language]
    assert first_inactive_day in definition
    # A one-day period shows that the end date is excluded.
    assert "2026-06-30" in definition and "2026-07-01" in definition


def test_schema_org_end_date_is_a_close_match_without_a_context_alias(built_vocabulary, owl_graph):
    # schema.org and FHIR read an end date as the last day of a period, one day earlier.
    end_date = built_vocabulary["properties"]["end_date"]
    assert end_date["schema_org_equivalent"] is None
    assert end_date["external_equivalents"]["schema-org"]["match"] == "close"
    assert (END_DATE, SKOS.closeMatch, SCHEMA_END_DATE) in owl_graph
    assert (END_DATE, SKOS.exactMatch, SCHEMA_END_DATE) not in owl_graph

    context = built_vocabulary["context"]["@context"]
    assert "endDate" not in context
    assert context["startDate"] == context["start_date"]


@pytest.mark.parametrize("language,calendar_year", [
    ("en", "2024-01-01 to 2025-01-01"),
    ("es", "2024-01-01 a 2025-01-01"),
    ("fr", "2024-01-01 au 2025-01-01"),
])
def test_a_metric_period_ends_on_the_day_after_its_coverage(built_vocabulary, language, calendar_year):
    definition = built_vocabulary["concepts"]["metrics/Period"]["definition"][language]
    assert calendar_year in definition
    assert "FHIR" in definition
