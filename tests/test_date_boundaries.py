"""The published end_date states its boundary, so merged datasets agree on the last effective day."""
import pytest
from rdflib import URIRef
from rdflib.namespace import SKOS

END_DATE = URIRef("https://publicschema.org/end_date")
SCHEMA_END_DATE = URIRef("http://schema.org/endDate")


@pytest.mark.parametrize("language,last_day", [
    ("en", "last day on which this is effective"),
    ("es", "último día en que esto es efectivo"),
    ("fr", "dernier jour où ceci est effectif"),
])
def test_end_date_is_the_last_day_it_applies(built_vocabulary, language, last_day):
    definition = built_vocabulary["properties"]["end_date"]["definition"][language]
    assert last_day in definition
    # A one-day period shows that the end date is included.
    assert definition.count("2026-06-30") == 2
    assert "2026-07-01" not in definition


def test_schema_org_end_date_stays_an_exact_match_with_its_context_alias(built_vocabulary, owl_graph):
    # schema.org and FHIR also read an end date as the last day of a period.
    end_date = built_vocabulary["properties"]["end_date"]
    assert end_date["schema_org_equivalent"] == "schema:endDate"
    assert (END_DATE, SKOS.exactMatch, SCHEMA_END_DATE) in owl_graph
    assert (END_DATE, SKOS.closeMatch, SCHEMA_END_DATE) not in owl_graph

    context = built_vocabulary["context"]["@context"]
    assert context["endDate"] == context["end_date"]
    assert context["startDate"] == context["start_date"]


@pytest.mark.parametrize("language,calendar_year", [
    ("en", "2024-01-01 to 2024-12-31"),
    ("es", "2024-01-01 a 2024-12-31"),
    ("fr", "2024-01-01 au 2024-12-31"),
])
def test_a_metric_period_ends_on_its_last_covered_day(built_vocabulary, language, calendar_year):
    definition = built_vocabulary["concepts"]["metrics/Period"]["definition"][language]
    assert calendar_year in definition
    assert "2025-01-01" not in definition
