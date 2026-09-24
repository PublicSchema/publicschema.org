"""Optional authoring check using the pinned HL7 validator and a prepared cache.

Java and downloaded FHIR packages are not application or pytest dependencies.
See docs/fhir-registry-integration.md for one-time cache preparation.
"""

import argparse
import hashlib
import json
import subprocess
import tarfile
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR_VERSION = "6.9.12"
VALIDATOR_URL = "https://github.com/hapifhir/org.hl7.fhir.core/releases/download/6.9.12/validator_cli.jar"
VALIDATOR_SHA256 = "0e53ab1d1a6f1e35f505255c0b8ce10a35fcf27e6e96b503640f784cd07e5ad6"
PACKAGES = {
    "hl7.fhir.r5.core#5.0.0",
    "hl7.fhir.xver-extensions#0.1.0",
    "hl7.terminology.r5#6.2.0",
    "hl7.fhir.uv.extensions.r5#5.2.0",
    "hl7.terminology.r5#7.1.0",
    "hl7.fhir.uv.extensions.r5#5.3.0",
    "hl7.terminology#7.3.0",
}


def outcome_counts(outcome):
    """Do not trust the Java CLI's successful exit when -output is supplied."""
    if outcome.get("resourceType") != "OperationOutcome" or not isinstance(outcome.get("issue"), list):
        raise ValueError("expected an OperationOutcome with an issue array")
    allowed = {"fatal", "error", "warning", "information", "success"}
    counts = Counter()
    for issue in outcome["issue"]:
        severity = issue.get("severity")
        if severity not in allowed:
            raise ValueError("invalid OperationOutcome severity")
        counts[severity] += 1
    return dict(counts)


def verify_inputs(jar, cache_home):
    with jar.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != VALIDATOR_SHA256:
            raise ValueError(f"expected the published HL7 validator {VALIDATOR_VERSION} SHA-256")
    cache = cache_home / ".fhir/packages"
    installed = {path.name for path in cache.iterdir() if path.is_dir() and "#" in path.name}
    if installed != PACKAGES:
        raise ValueError("use an isolated prepared cache with exactly the package versions listed in the guide")
    for package in PACKAGES:
        name, version = package.split("#")
        metadata = json.loads((cache / package / "package/package.json").read_text())
        if metadata.get("name") != name or metadata.get("version") != version:
            raise ValueError(f"cached package metadata disagrees with {package}")


def prepare_cache(cache_home):
    """Explicit setup only: fetch fixed official package releases, never input URLs."""
    cache = cache_home / ".fhir/packages"
    cache.mkdir(parents=True, exist_ok=True)
    for package in sorted(PACKAGES):
        destination = cache / package
        if destination.exists():
            continue
        name, version = package.split("#")
        url = f"https://packages2.fhir.org/packages/{name}/{version}"
        print(f"Preparing {package}", flush=True)
        with tempfile.TemporaryDirectory(prefix="publicschema-fhir-package-", dir=cache) as directory:
            temporary = Path(directory)
            archive_path = temporary / "package.tgz"
            with urllib.request.urlopen(url, timeout=60) as response, archive_path.open("wb") as output:
                while block := response.read(1024 * 1024):
                    output.write(block)
            expanded = temporary / "expanded"
            with tarfile.open(archive_path) as archive:
                archive.extractall(expanded, filter="data")
            metadata = json.loads((expanded / "package/package.json").read_text())
            if metadata.get("name") != name or metadata.get("version") != version:
                raise ValueError(f"downloaded package metadata disagrees with {package}")
            expanded.rename(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jar", type=Path)
    parser.add_argument("--cache-home", type=Path, required=True)
    parser.add_argument("--prepare-cache", action="store_true", help="download the fixed package releases, then exit")
    parser.add_argument("--bundle", type=Path, default=HERE / "bundle.fhir.json")
    parser.add_argument("--output", type=Path, help="write the checked OperationOutcome here")
    args = parser.parse_args()
    try:
        if args.prepare_cache:
            prepare_cache(args.cache_home)
            print("Pinned package cache prepared. Validation itself runs with network access disabled.")
            return
        if args.jar is None or args.output is None:
            parser.error("validation requires --jar and --output")
        verify_inputs(args.jar, args.cache_home)
        with tempfile.TemporaryDirectory(prefix="publicschema-fhir-validation-") as directory:
            temporary = Path(directory)
            settings = temporary / "fhir-settings.json"
            # FhirSettingsPOJO in the pinned official tool supports this setting.
            settings.write_text(json.dumps({"prohibitNetworkAccess": True}))
            outcome_path = temporary / "outcome.json"
            result = subprocess.run([
                "java", "-Xmx2g", "-Duser.home=" + str(args.cache_home.resolve()),
                "-jar", str(args.jar.resolve()), str(args.bundle.resolve()),
                "-version", "5.0.0", "-fhir-settings", str(settings),
                "-tx", "n/a", "-txCache", str(temporary / "tx-cache"),
                "-disable-default-resource-fetcher", "-check-references",
                "-allow-example-urls", "true", "-locale", "en", "-jurisdiction", "uv",
                "-output", str(outcome_path),
            ], check=False)
            if not outcome_path.is_file():
                raise ValueError("HL7 validator did not produce an OperationOutcome")
            outcome = json.loads(outcome_path.read_text())
            counts = outcome_counts(outcome)
            args.output.write_text(json.dumps(outcome, indent=2) + "\n")
            if result.returncode != 0 and not (counts.get("error", 0) or counts.get("fatal", 0)):
                raise ValueError("HL7 validator failed independently of its reported resource issues")
        print(json.dumps({"validator": VALIDATOR_VERSION, "fhir_release": "5.0.0", "issues": counts}, indent=2))
        if counts.get("error", 0) or counts.get("fatal", 0):
            parser.exit(1, "FHIR errors found; inspect the OperationOutcome.\n")
        print("PASS with the reported terminology limitations; no jurisdictional-profile or clinical-conformance claim.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Official validation failed: {error}\n")


if __name__ == "__main__":
    main()
