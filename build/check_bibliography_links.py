"""Check every `uri:` in schema/bibliography/ for reachability.

One-off diagnostic. Not part of the build or test suite: external URLs flake,
and a failing link is a triage signal for a human, not a build failure.

Run:
    uv run python build/check_bibliography_links.py

Writes a Markdown report to .work/reports/bibliography-link-check.md.
"""

from __future__ import annotations

import concurrent.futures
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BIB_DIR = REPO_ROOT / "schema" / "bibliography"
REPORT_PATH = REPO_ROOT / ".work" / "reports" / "bibliography-link-check.md"

# Mimic a real browser. Some publishers (e.g. Elsevier, Springer) 403 on
# empty or python-style User-Agents.
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT_SECONDS = 20
MAX_WORKERS = 16


def collect_entries() -> list[dict]:
    entries = []
    for path in sorted(BIB_DIR.glob("*.yaml")):
        with path.open() as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            continue
        uri = data.get("uri")
        if not uri:
            continue
        entries.append(
            {
                "id": data.get("id", path.stem),
                "title": data.get("title", ""),
                "uri": uri,
                "file": path.name,
            }
        )
    return entries


def check_one(entry: dict) -> dict:
    """Check a single URL. Try HEAD, fall back to GET on 405/403/404."""
    url = entry["uri"]
    result = dict(entry)

    def do_request(method: str) -> tuple[int | None, str | None, str | None]:
        req = urllib.request.Request(url, method=method, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                return resp.status, resp.geturl(), None
        except urllib.error.HTTPError as e:
            return e.code, None, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return None, None, f"URLError: {e.reason}"
        except TimeoutError:
            return None, None, "Timeout"
        except Exception as e:  # noqa: BLE001
            return None, None, f"{type(e).__name__}: {e}"

    # Try HEAD first (cheap), fall back to GET if the server refuses HEAD or
    # returns a code that GET might handle differently.
    status, final_url, err = do_request("HEAD")
    if status is None or status >= 400:
        status_g, final_url_g, err_g = do_request("GET")
        # Prefer GET result if it succeeded or gave a more specific error.
        if status_g is not None and (status is None or status_g < 400 or status_g != status):
            status, final_url, err = status_g, final_url_g, err_g

    result["status"] = status
    result["final_url"] = final_url
    result["error"] = err
    return result


def classify(r: dict) -> str:
    s = r["status"]
    if s is None:
        return "network_error"
    if 200 <= s < 300:
        return "ok"
    if 300 <= s < 400:
        return "redirect"
    if s == 401 or s == 403:
        return "restricted"  # likely reachable, paywalled/blocked
    if s == 404 or s == 410:
        return "missing"
    if 400 <= s < 500:
        return "client_error"
    if 500 <= s < 600:
        return "server_error"
    return "other"


def format_report(results: list[dict]) -> str:
    buckets: dict[str, list[dict]] = {}
    for r in results:
        buckets.setdefault(classify(r), []).append(r)

    total = len(results)
    lines: list[str] = []
    lines.append("# Bibliography link check")
    lines.append("")
    lines.append(f"Checked **{total}** entries from `schema/bibliography/`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    order = [
        "ok",
        "redirect",
        "restricted",
        "missing",
        "client_error",
        "server_error",
        "network_error",
        "other",
    ]
    for cat in order:
        items = buckets.get(cat, [])
        lines.append(f"- **{cat}**: {len(items)}")
    lines.append("")

    explain = {
        "ok": "Reachable (2xx).",
        "redirect": "Redirect not followed to a 2xx. Worth inspecting the final URL.",
        "restricted": "401/403: likely reachable but the server requires auth or blocks bots.",
        "missing": "404 or 410: probably actually broken. Fix priority.",
        "client_error": "Other 4xx.",
        "server_error": "5xx: may be transient, retry or inspect.",
        "network_error": "DNS failure, timeout, or connection refused.",
        "other": "Unclassified.",
    }
    priority_sections = [
        "missing",
        "network_error",
        "server_error",
        "client_error",
        "redirect",
        "restricted",
        "other",
    ]
    for cat in priority_sections:
        items = buckets.get(cat, [])
        if not items:
            continue
        lines.append(f"## {cat} ({len(items)})")
        lines.append("")
        lines.append(f"_{explain[cat]}_")
        lines.append("")
        lines.append("| id | status | uri | file |")
        lines.append("|----|--------|-----|------|")
        for r in sorted(items, key=lambda x: x["id"]):
            status = r["status"] if r["status"] is not None else (r["error"] or "err")
            uri = r["uri"].replace("|", "\\|")
            lines.append(f"| `{r['id']}` | {status} | {uri} | `{r['file']}` |")
        lines.append("")

    ok_count = len(buckets.get("ok", []))
    lines.append("## Reachable (ok)")
    lines.append("")
    lines.append(f"{ok_count} entries returned 2xx. Not listed individually.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    entries = collect_entries()
    if not entries:
        print("No bibliography entries with uri: found.", file=sys.stderr)
        return 1
    print(f"Checking {len(entries)} URLs with {MAX_WORKERS} workers...", file=sys.stderr)
    start = time.time()
    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for i, r in enumerate(pool.map(check_one, entries), 1):
            results.append(r)
            status = r["status"] if r["status"] is not None else r["error"]
            print(f"[{i}/{len(entries)}] {r['id']}: {status}", file=sys.stderr)
    elapsed = time.time() - start
    print(f"Done in {elapsed:.1f}s", file=sys.stderr)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(format_report(results))
    print(f"Report: {REPORT_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
