#!/usr/bin/env python3
"""
Workshop demo health check — runs daily via demo-health.yml or on demand.

Validates the live state of tkl-enteprises/ghas-demos:
  - Every intentional lesson finding in scripts/expected-alerts.json is still
    open on the default branch (catches a demo fix PR that was merged by mistake)
  - Open alert counts haven't drifted below expected thresholds
  - Latest CodeQL run on main was successful
  - main-branch ruleset is active
  - Secret Protection and Dependabot toggles are still enabled

Reads GITHUB_TOKEN from the environment. Prints a Markdown report to stdout
(the workflow appends it to the job summary) and exits 1 if any check fails.
Checks the token cannot read are reported as skipped, not failed.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

OWNER = "tkl-enteprises"
REPO = "ghas-demos"
API = "https://api.github.com"
INVENTORY = Path(__file__).resolve().parent / "expected-alerts.json"

# (row label, alerts endpoint, minimum open alerts before the demo looks empty)
ALERT_COUNT_CHECKS = (
    ("Code scanning alerts", "code-scanning/alerts", 25),
    ("Dependabot alerts", "dependabot/alerts", 50),
    ("Secret scanning alerts", "secret-scanning/alerts", 1),
)
EXPECTED_RULESET_NAME = "main-branch-protection"


def _request(path: str, token: str) -> tuple[int, Any, dict[str, str]]:
    """Make an authenticated GET against the GitHub REST API.

    Returns (status_code, parsed_json_or_none, headers).
    Never raises for HTTP errors — the caller decides what to do with non-200.
    """
    url = path if path.startswith("http") else f"{API}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "ghas-demos-health-check",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body) if body else None
            return resp.status, data, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(body) if body else None
        except json.JSONDecodeError:
            data = body
        return e.code, data, dict(e.headers or {})
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}, {}


def _next_link(headers: dict[str, str]) -> str | None:
    link = headers.get("Link") or headers.get("link") or ""
    for part in link.split(","):
        part = part.strip()
        if part.endswith('rel="next"'):
            start, end = part.find("<"), part.find(">")
            if start != -1 and end != -1:
                return part[start + 1 : end]
    return None


def _list_paginated(path: str, token: str, cap: int = 2000) -> tuple[list | None, str | None]:
    """Fetch every item of a list endpoint. On 403/404 returns (None, reason)."""
    sep = "&" if "?" in path else "?"
    page: str | None = f"{path}{sep}per_page=100"
    items: list = []
    while page and len(items) < cap:
        status, data, headers = _request(page, token)
        if status == 403:
            return None, "403 forbidden (token lacks permission)"
        if status == 404:
            return None, "404 not found (feature disabled?)"
        if status != 200:
            return None, f"http {status}"
        if not isinstance(data, list):
            return None, "unexpected response shape"
        items.extend(data)
        page = _next_link(headers)
    return items, None


def _row(name: str, expected: str, actual: str, ok: bool | None) -> dict:
    return {"name": name, "expected": expected, "actual": actual, "ok": ok}


def check_alert_count(label: str, endpoint: str, minimum: int, token: str) -> dict:
    items, err = _list_paginated(f"/repos/{OWNER}/{REPO}/{endpoint}?state=open", token)
    if err:
        return _row(label, f"≥ {minimum}", f"skipped — {err}", None)
    count = len(items or [])
    return _row(label, f"≥ {minimum}", str(count), count >= minimum)


def load_inventory(path: Path = INVENTORY) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)["code_scanning"]


def missing_expected_alerts(open_alerts: list[dict], expected: list[dict]) -> list[dict]:
    """Return the inventory entries that have no matching open alert."""
    present = {
        (
            (alert.get("tool") or {}).get("name"),
            (alert.get("rule") or {}).get("id"),
            ((alert.get("most_recent_instance") or {}).get("location") or {}).get("path"),
        )
        for alert in open_alerts
    }
    return [e for e in expected if (e["tool"], e["rule"], e["path"]) not in present]


def check_expected_findings(token: str) -> dict:
    name = "Intentional lesson findings open on main"
    expected = load_inventory()
    want = f"{len(expected)}/{len(expected)}"
    alerts, err = _list_paginated(
        f"/repos/{OWNER}/{REPO}/code-scanning/alerts?state=open", token
    )
    if err:
        return _row(name, want, f"skipped — {err}", None)
    missing = missing_expected_alerts(alerts or [], expected)
    actual = f"{len(expected) - len(missing)}/{len(expected)}"
    if missing:
        listed = "; ".join(
            f"lesson {e['lesson']} {e['rule']} in {e['path'].rsplit('/', 1)[-1]}"
            for e in missing[:6]
        )
        more = f" (+{len(missing) - 6} more)" if len(missing) > 6 else ""
        actual += f" — missing: {listed}{more}"
    return _row(name, want, actual, not missing)


def check_codeql_run(token: str) -> dict:
    name = "Latest CodeQL run on main"
    status, data, _ = _request(
        f"/repos/{OWNER}/{REPO}/actions/workflows/codeql.yml/runs?branch=main&per_page=1",
        token,
    )
    if status == 403:
        return _row(name, "success", "skipped — 403 forbidden", None)
    if status != 200 or not isinstance(data, dict):
        return _row(name, "success", f"http {status}", False)
    runs = data.get("workflow_runs") or []
    if not runs:
        return _row(name, "success", "no runs found", False)
    conclusion = runs[0].get("conclusion") or runs[0].get("status") or "unknown"
    return _row(name, "success", str(conclusion), conclusion == "success")


def check_ruleset(token: str) -> dict:
    name = "main-branch ruleset"
    status, data, _ = _request(f"/repos/{OWNER}/{REPO}/rulesets", token)
    if status == 403:
        return _row(name, "active", "skipped — 403 forbidden", None)
    if status != 200 or not isinstance(data, list):
        return _row(name, "active", f"http {status}", False)
    match = next((r for r in data if r.get("name") == EXPECTED_RULESET_NAME), None)
    if not match:
        return _row(name, "active", "missing", False)
    enforcement = match.get("enforcement") or "unknown"
    return _row(name, "active", str(enforcement), enforcement == "active")


def check_security_settings(token: str) -> list[dict]:
    """Inspect the repo's security_and_analysis block (visible to admins only)."""
    status, data, _ = _request(f"/repos/{OWNER}/{REPO}", token)
    if status != 200 or not isinstance(data, dict):
        return [_row("Security settings", "enabled", f"skipped — http {status}", None)]
    settings = data.get("security_and_analysis")
    if not isinstance(settings, dict):
        return [_row("Security settings", "enabled", "skipped — needs admin token", None)]
    rows: list[dict] = []
    for label, key in (
        ("Secret scanning", "secret_scanning"),
        ("Push protection", "secret_scanning_push_protection"),
        ("Dependabot security updates", "dependabot_security_updates"),
    ):
        block = settings.get(key)
        if not isinstance(block, dict):
            rows.append(_row(label, "enabled", "skipped — needs admin token", None))
            continue
        state = block.get("status") or "unknown"
        rows.append(_row(label, "enabled", str(state), state == "enabled"))
    return rows


def render_table(rows: list[dict]) -> str:
    lines = [
        "| Check | Expected | Actual | Status |",
        "|---|---|---|---|",
    ]
    for r in rows:
        badge = {True: "✅", False: "❌"}.get(r["ok"], "⚠️")
        lines.append(f"| {r['name']} | {r['expected']} | {r['actual']} | {badge} |")
    return "\n".join(lines)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("error: GITHUB_TOKEN is not set", file=sys.stderr)
        return 2

    rows: list[dict] = [
        check_expected_findings(token),
        *(
            check_alert_count(label, endpoint, minimum, token)
            for label, endpoint, minimum in ALERT_COUNT_CHECKS
        ),
        check_codeql_run(token),
        check_ruleset(token),
        *check_security_settings(token),
    ]

    print(f"## Workshop demo health — {OWNER}/{REPO}\n")
    print(render_table(rows))

    failures = sum(1 for r in rows if r["ok"] is False)
    skipped = sum(1 for r in rows if r["ok"] is None)
    passed = sum(1 for r in rows if r["ok"] is True)
    print(f"summary: {passed} passed, {failures} failed, {skipped} skipped", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
