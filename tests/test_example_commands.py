"""Smoke-test every example command the guides tell an adopter to run.

Each command runs as a subprocess from the repository root, as documented, with
the interpreter of the current environment (what ``uv run --locked python``
selects). The focused example tests cover behaviour; this only proves that the
documented entry points still start, pass and say so.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = "examples/relationship-date-migration"
# The official FHIR validator is an optional authoring check. Its guide
# downloads the pinned JAR and prepares the package cache at these paths.
FHIR_JAR = Path("/tmp/publicschema-fhir-validator-6.9.12.jar")
FHIR_CACHE = Path("/tmp/publicschema-fhir-cache")

COMMANDS = {
    "farm-operators": (["examples/farm-operators/validate_profile.py"],
                       "Farm holder and work example profile: passed"),
    "facility-roles": (["examples/facility-roles/validate_profile.py"],
                       "Facility estate example profile: passed"),
    "agriculture-biology": (["examples/agriculture-biology/validate_movement_profile.py"],
                            "Animal movement example profile: passed"),
    "government-relationships": (["examples/government-relationships/validate_profile.py", "--negative"],
                                 "Documented government relationship counterexamples: rejected as expected"),
    "government-domains": (["examples/government-domains/profile.py"],
                           "Government domain example profile: passed"),
    "public-services": (["examples/public-services/profile.py"],
                        "synthetic public service records."),
    "fhir-registry": (["examples/fhir-registry/validate.py"],
                      "PASS: official R5 JSON Schema and local reference contract"),
    "relationship-date-migration": ([f"{MIGRATION}/migrate.py", "--source-boundary", "inclusive-calendar-days",
                                     f"{MIGRATION}/legacy-records.json"],
                                    "https://example.org/date-migration/holding"),
}


def documented_scripts():
    """Example scripts named in a run command in the guides or example docs."""
    command = re.compile(r"(?:uv run(?: --locked)? python|\.venv/bin/python) (examples/[\w./-]+\.py)")
    sources = [*ROOT.glob("docs/*.md"), *ROOT.glob("examples/**/*.md"), *ROOT.glob("examples/**/*.py")]
    return {match for path in sources for match in command.findall(path.read_text(encoding="utf-8"))}


def run(args):
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True, timeout=300, check=False,
    )


def test_every_documented_example_script_is_smoke_tested():
    tested = {args[0] for args, _ in COMMANDS.values()} | {"examples/fhir-registry/official_validate.py"}
    documented = documented_scripts()
    assert "examples/fhir-registry/official_validate.py" in documented
    assert documented <= tested, sorted(documented - tested)


@pytest.mark.parametrize("name", COMMANDS)
def test_documented_example_command_passes(name):
    args, expected = COMMANDS[name]
    result = run(args)
    assert result.returncode == 0, result.stderr
    assert expected in result.stdout
    if name == "relationship-date-migration":
        expected_records = json.loads((ROOT / MIGRATION / "records.json").read_text(encoding="utf-8"))
        assert json.loads(result.stdout) == expected_records


@pytest.mark.skipif(
    shutil.which("java") is None or not FHIR_JAR.is_file() or not (FHIR_CACHE / ".fhir/packages").is_dir(),
    reason="the optional official FHIR validator needs Java, the pinned JAR and a prepared package cache",
)
def test_documented_official_fhir_validation_passes(tmp_path):
    result = run([
        "examples/fhir-registry/official_validate.py", "--jar", str(FHIR_JAR),
        "--cache-home", str(FHIR_CACHE), "--output", str(tmp_path / "outcome.json"),
    ])
    assert result.returncode == 0, result.stderr
    assert "PASS with the reported terminology limitations" in result.stdout
