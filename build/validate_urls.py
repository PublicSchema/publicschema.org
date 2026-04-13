"""Checks that bibliography entry URIs are reachable.

Reads every YAML file in ``schema/bibliography/`` and probes each entry's
``uri`` via HTTP HEAD (falling back to GET if HEAD is not allowed). Reports
results grouped by outcome category. Exits 0 unconditionally: this is an
advisory tool meant to be run manually or on a schedule, not a build gate.

Usage:
    uv run python -m build.validate_urls [schema_dir]
"""

import socket
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import yaml


DEFAULT_TIMEOUT = 15  # seconds; some standards bodies' sites are slow
USER_AGENT = "PublicSchema-LinkCheck/1.0 (+https://publicschema.org)"
MAX_WORKERS = 8


@dataclass
class ProbeResult:
    bib_id: str
    uri: str
    status: int | None
    final_uri: str | None
    error: str | None


def _load_bibliography(directory: Path) -> list[tuple[str, str]]:
    """Return [(bib_id, uri)] for every bibliography entry that has a URI."""
    results: list[tuple[str, str]] = []
    for path in sorted(directory.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        bib_id = data.get("id")
        uri = data.get("uri")
        if bib_id and uri:
            results.append((bib_id, uri))
    return results


def _probe(bib_id: str, uri: str, timeout: int = DEFAULT_TIMEOUT) -> ProbeResult:
    """HEAD the URL; fall back to GET if HEAD is rejected.

    Captures HTTP status, the final (post-redirect) URL, and any transport
    error. All exceptions are caught so a single bad URL does not abort the
    run; the failure is recorded on the result instead.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}

    def _open(method: str):
        req = urllib.request.Request(uri, headers=headers, method=method)
        return urllib.request.urlopen(req, timeout=timeout)

    try:
        try:
            resp = _open("HEAD")
        except urllib.error.HTTPError as e:
            # 405/501 mean HEAD is unsupported; many SDOs only allow GET.
            if e.code in (403, 405, 501):
                resp = _open("GET")
            else:
                return ProbeResult(bib_id, uri, e.code, None, None)
        return ProbeResult(bib_id, uri, resp.status, resp.geturl(), None)
    except urllib.error.HTTPError as e:
        return ProbeResult(bib_id, uri, e.code, None, None)
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", e)
        return ProbeResult(bib_id, uri, None, None, f"{type(reason).__name__}: {reason}")
    except (socket.timeout, ssl.SSLError, ConnectionError, OSError) as e:
        return ProbeResult(bib_id, uri, None, None, f"{type(e).__name__}: {e}")


def _categorise(result: ProbeResult) -> str:
    if result.error is not None:
        return "transport_error"
    if result.status is None:
        return "unknown"
    if 200 <= result.status < 300:
        return "ok"
    if 300 <= result.status < 400:
        return "redirect_unfollowed"
    if 400 <= result.status < 500:
        return "client_error"
    if 500 <= result.status < 600:
        return "server_error"
    return "unknown"


def _redirected_to_different_host(uri: str, final_uri: str | None) -> bool:
    if not final_uri or final_uri == uri:
        return False
    try:
        from urllib.parse import urlparse
        return urlparse(uri).netloc != urlparse(final_uri).netloc
    except Exception:
        return False


def main():
    schema_dir = Path("schema")
    if len(sys.argv) > 1:
        schema_dir = Path(sys.argv[1])
    bib_dir = schema_dir / "bibliography"

    if not bib_dir.exists():
        print(f"No bibliography directory at {bib_dir}", file=sys.stderr)
        sys.exit(0)

    entries = _load_bibliography(bib_dir)
    print(f"Probing {len(entries)} bibliography URIs...\n", flush=True)

    results: list[ProbeResult] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_probe, bib_id, uri): (bib_id, uri) for bib_id, uri in entries}
        for fut in as_completed(futures):
            results.append(fut.result())

    by_category: dict[str, list[ProbeResult]] = {}
    for r in results:
        by_category.setdefault(_categorise(r), []).append(r)

    order = ["ok", "redirect_unfollowed", "client_error", "server_error", "transport_error", "unknown"]
    headings = {
        "ok": "OK (2xx)",
        "redirect_unfollowed": "Redirect not followed (3xx)",
        "client_error": "Client error (4xx)",
        "server_error": "Server error (5xx)",
        "transport_error": "Transport error",
        "unknown": "Unknown",
    }

    for cat in order:
        items = sorted(by_category.get(cat, []), key=lambda r: r.bib_id)
        if not items:
            continue
        print(f"== {headings[cat]} ({len(items)}) ==")
        for r in items:
            line = f"  - {r.bib_id}  {r.status if r.status is not None else '-'}  {r.uri}"
            if r.error:
                line += f"  [{r.error}]"
            elif _redirected_to_different_host(r.uri, r.final_uri):
                line += f"  -> {r.final_uri}"
            print(line)
        print()

    total = len(results)
    ok = len(by_category.get("ok", []))
    print(f"Summary: {ok}/{total} OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
