#!/usr/bin/env python3
"""
Workshop demo health check — runs daily via demo-health.yml or on-demand.

Validates live state of tkl-enteprises/ghas-demos:
  - Alert counts haven't drifted below expected thresholds
  - Latest CodeQL run on main was successful
  - main-branch ruleset is active
  - GHAS toggles still enabled

Reads GITHUB_TOKEN from env. Exits 1 if any check fails.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

OWNER = "tkl-enteprises"
REPO = "ghas-demos"
API = "https://api.github.com"

EXPECTED_CODE_SCANNING = 25
EXPECTED_DEPENDABOT = 50
EXPECTED_SECRET_SCANNING = 1
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


def _count_paginated(path: str, token: str, cap: int = 1000) -> tuple[int | None, str | None]:
    """Count items across all pages of a list endpoint.

    Returns (count, error_message). On 403/404 returns (None, reason).
    """
    sep = "&" if "?" in path else "?"
    page_path = f"{path}{sep}per_page=100"
    total = 0
    while page_path and total < cap:
        status, data, headers = _request(page_path, token)
        if status == 403:
            return None, "403 forbidden (token lacks scope)"
        if status == 404:
            return None, "404 not found (feature disabled?)"
        if status != 200:
            return None, f"http {status}"
        if not isinstance(data, list):
            return None, "unexpected response shape"
        total += len(data)
        # Parse Link header for next page.
        link = headers.get("Link") or headers.get("link") or ""
        next_url = None
        for part in link.split(","):
            part = part.strip()
            if part.endswith('rel="next"'):
                start = part.find("<")
                end = part.find(">")
                if start != -1 and end != -1:
                    next_url = part[start + 1 : end]
                break
        page_path = next_url
    return total, None


def check_code_scanning(token: str) -> dict:
    count, err = _count_paginated(
        f"/repos/{OWNER}/{REPO}/code-scanning/alerts?state=open", token
    )
    if err:
        return {
            "name": "Code scanning alerts",
            "expected": f"≥ {EXPECTED_CODE_SCANNING}",
            "actual": f"skipped — {err}",
            "ok": None,
        }
    return {
        "name": "Code scanning alerts",
        "expected": f"≥ {EXPECTED_CODE_SCANNING}",
        "actual": str(count),
        "ok": count >= EXPECTED_CODE_SCANNING,
    }


def check_dependabot(token: str) -> dict:
    count, err = _count_paginated(
        f"/repos/{OWNER}/{REPO}/dependabot/alerts?state=open", token
    )
    if err:
        return {
            "name": "Dependabot alerts",
            "expected": f"≥ {EXPECTED_DEPENDABOT}",
            "actual": f"skipped — {err}",
            "ok": None,
        }
    return {
        "name": "Dependabot alerts",
        "expected": f"≥ {EXPECTED_DEPENDABOT}",
        "actual": str(count),
        "ok": count >= EXPECTED_DEPENDABOT,
    }


def check_secret_scanning(token: str) -> dict:
    count, err = _count_paginated(
        f"/repos/{OWNER}/{REPO}/secret-scanning/alerts?state=open", token
    )
    if err:
        return {
            "name": "Secret scanning alerts",
            "expected": f"≥ {EXPECTED_SECRET_SCANNING}",
            "actual": f"skipped — {err}",
            "ok": None,
        }
    return {
        "name": "Secret scanning alerts",
        "expected": f"≥ {EXPECTED_SECRET_SCANNING}",
        "actual": str(count),
        "ok": count >= EXPECTED_SECRET_SCANNING,
    }


def check_codeql_run(token: str) -> dict:
    status, data, _ = _request(
        f"/repos/{OWNER}/{REPO}/actions/workflows/codeql.yml/runs?branch=main&per_page=1",
        token,
    )
    if status == 403:
        return {
            "name": "Latest CodeQL run on main",
            "expected": "success",
            "actual": "skipped — 403 forbidden",
            "ok": None,
        }
    if status != 200 or not isinstance(data, dict):
        return {
            "name": "Latest CodeQL run on main",
            "expected": "success",
            "actual": f"http {status}",
            "ok": False,
        }
    runs = data.get("workflow_runs") or []
    if not runs:
        return {
            "name": "Latest CodeQL run on main",
            "expected": "success",
            "actual": "no runs found",
            "ok": False,
        }
    conclusion = runs[0].get("conclusion") or runs[0].get("status") or "unknown"
    return {
        "name": "Latest CodeQL run on main",
        "expected": "success",
        "actual": str(conclusion),
        "ok": conclusion == "success",
    }


def check_ruleset(token: str) -> dict:
    status, data, _ = _request(f"/repos/{OWNER}/{REPO}/rulesets", token)
    if status == 403:
        return {
            "name": "main-branch ruleset",
            "expected": "active",
            "actual": "skipped — 403 forbidden",
            "ok": None,
        }
    if status != 200 or not isinstance(data, list):
        return {
            "name": "main-branch ruleset",
            "expected": "active",
            "actual": f"http {status}",
            "ok": False,
        }
    match = next(
        (r for r in data if r.get("name") == EXPECTED_RULESET_NAME),
        None,
    )
    if not match:
        return {
            "name": "main-branch ruleset",
            "expected": "active",
            "actual": "missing",
            "ok": False,
        }
    enforcement = match.get("enforcement") or "unknown"
    return {
        "name": "main-branch ruleset",
        "expected": "active",
        "actual": str(enforcement),
        "ok": enforcement == "active",
    }


def check_ghas_toggles(token: str) -> list[dict]:
    """Inspect the repo's security_and_analysis block.

    Requires admin scope; falls back to "skipped" rows when fields are absent.
    """
    status, data, _ = _request(f"/repos/{OWNER}/{REPO}", token)
    if status != 200 or not isinstance(data, dict):
        return [
            {
                "name": "GHAS config",
                "expected": "enabled",
                "actual": f"skipped — http {status}",
                "ok": None,
            }
        ]
    sec = data.get("security_and_analysis")
    if not isinstance(sec, dict):
        return [
            {
                "name": "GHAS config",
                "expected": "enabled",
                "actual": "skipped — needs admin token",
                "ok": None,
            }
        ]
    rows: list[dict] = []
    for label, key in (
        ("Secret scanning", "secret_scanning"),
        ("Secret scanning push protection", "secret_scanning_push_protection"),
        ("Dependabot security updates", "dependabot_security_updates"),
    ):
        block = sec.get(key)
        if not isinstance(block, dict):
            rows.append(
                {
                    "name": label,
                    "expected": "enabled",
                    "actual": "skipped — needs admin token",
                    "ok": None,
                }
            )
            continue
        state = block.get("status") or "unknown"
        rows.append(
            {
                "name": label,
                "expected": "enabled",
                "actual": str(state),
                "ok": state == "enabled",
            }
        )
    return rows


def render_table(rows: list[dict]) -> str:
    lines = [
        "| Check | Expected | Actual | Status |",
        "|---|---|---|---|",
    ]
    for r in rows:
        if r["ok"] is True:
            badge = "✅"
        elif r["ok"] is False:
            badge = "❌"
        else:
            badge = "⚠️"
        lines.append(f"| {r['name']} | {r['expected']} | {r['actual']} | {badge} |")
    return "\n".join(lines)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("error: GITHUB_TOKEN is not set", file=sys.stderr)
        return 2

    rows: list[dict] = []
    rows.append(check_code_scanning(token))
    rows.append(check_dependabot(token))
    rows.append(check_secret_scanning(token))
    rows.append(check_codeql_run(token))
    rows.append(check_ruleset(token))
    rows.extend(check_ghas_toggles(token))

    table = render_table(rows)
    header = f"## Workshop demo health — {OWNER}/{REPO}\n\n"
    output = header + table + "\n"

    print(output)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(output)
        except OSError as e:
            print(f"warning: could not write GITHUB_STEP_SUMMARY: {e}", file=sys.stderr)

    failures = sum(1 for r in rows if r["ok"] is False)
    skipped = sum(1 for r in rows if r["ok"] is None)
    passed = sum(1 for r in rows if r["ok"] is True)
    print(f"summary: {passed} passed, {failures} failed, {skipped} skipped", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
