"""Guard that docs/consent-lifecycle.md keeps the three legal-basis test questions.

The questions are the decision tree for "should a program claim legal_basis = consent?"
and must be discoverable in prose (not buried in schema). Prevents doc rot.
"""

from pathlib import Path


DOCS_DIR = Path(__file__).parent.parent / "docs"
CONSENT_LIFECYCLE = DOCS_DIR / "consent-lifecycle.md"


LEGAL_BASIS_TEST_QUESTIONS = [
    "Can the beneficiary realistically refuse without losing access to the service?",
    "Does the notice explicitly state that participation is voluntary?",
    "Does withdrawal terminate the service?",
]


def test_consent_lifecycle_exists():
    assert CONSENT_LIFECYCLE.is_file()


def test_three_legal_basis_questions_present_verbatim():
    text = CONSENT_LIFECYCLE.read_text()
    for q in LEGAL_BASIS_TEST_QUESTIONS:
        assert q in text, f"consent-lifecycle.md missing legal-basis test question: {q!r}"


def test_biometric_cross_reference_documented():
    """Biometric-as-capture-method vs biometric-as-data-category must be distinguished in prose."""
    text = CONSENT_LIFECYCLE.read_text().lower()
    assert "opt-in-biometric" in text or "consent_expression" in text
    assert "personal_data_categories" in text
    # The two axes section should articulate the distinction
    assert "capture method" in text or "capture" in text


def test_age_of_majority_workaround_documented():
    """The v1 workaround (expiry_date = date of majority on parental consent) must be stated."""
    text = CONSENT_LIFECYCLE.read_text().lower()
    assert "expiry_date" in text
    assert "majority" in text
