"""
Consistency checks for scripts/expected-alerts.json — the inventory of
intentional code scanning findings that every lesson relies on.

  - The inventory is well formed and every path exists.
  - Every inventory rule is documented by its lesson (or FACILITATOR.md).
  - Lesson 04's documented Bandit rules match the inventory exactly.
  - scripts/demo-health.py reports missing findings correctly.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest


def _inventory(repo_root: Path) -> list[dict]:
    data = json.loads((repo_root / "scripts" / "expected-alerts.json").read_text(encoding="utf-8"))
    return data["code_scanning"]


def _lesson_dir(repo_root: Path, number: str) -> Path:
    matches = sorted((repo_root / "lessons").glob(f"{number}-*"))
    assert len(matches) == 1, f"expected one lesson directory for {number}, got {matches}"
    return matches[0]


def _load_demo_health(repo_root: Path):
    spec = importlib.util.spec_from_file_location(
        "demo_health", repo_root / "scripts" / "demo-health.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inventory_is_well_formed(repo_root: Path):
    entries = _inventory(repo_root)
    assert entries, "expected-alerts.json lists no findings"
    keys = [(e["tool"], e["rule"], e["path"]) for e in entries]
    assert len(keys) == len(set(keys)), "duplicate (tool, rule, path) entries"
    for e in entries:
        assert set(e) == {"lesson", "tool", "rule", "path"}, e
        assert e["tool"] in {"CodeQL", "Bandit"}, e
        assert re.fullmatch(r"\d{2}", e["lesson"]), e
        assert (repo_root / e["path"]).is_file(), f"inventory path does not exist: {e['path']}"
        if e["path"].startswith("lessons/"):
            assert e["path"].startswith(f"lessons/{e['lesson']}-"), e
        else:
            assert e["path"].startswith(".github/workflows/"), e


def test_every_inventory_rule_is_documented(repo_root: Path):
    facilitator = (repo_root / "FACILITATOR.md").read_text(encoding="utf-8")
    undocumented = []
    for e in _inventory(repo_root):
        lesson = _lesson_dir(repo_root, e["lesson"])
        docs = "\n".join(p.read_text(encoding="utf-8") for p in lesson.glob("*.md"))
        if e["rule"] not in docs and e["rule"] not in facilitator:
            undocumented.append((e["lesson"], e["rule"]))
    assert not undocumented, f"Inventory rules missing from lesson docs: {undocumented}"


def test_lesson01_documented_rules_are_in_inventory(repo_root: Path):
    readme = (_lesson_dir(repo_root, "01") / "README.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"`(py/[a-z0-9/-]+)`", readme))
    inventory = {e["rule"] for e in _inventory(repo_root) if e["lesson"] == "01"}
    assert documented == inventory, (
        f"Lesson 01 README and inventory disagree: only in README {documented - inventory}, "
        f"only in inventory {inventory - documented}"
    )


def test_lesson04_bandit_rules_match_inventory(repo_root: Path):
    readme = (_lesson_dir(repo_root, "04") / "README.md").read_text(encoding="utf-8")
    files_table = readme.split("## Files", 1)[1].split("\n## ", 1)[0]
    documented = set(re.findall(r"\bB\d{3}\b", files_table))
    inventory = {e["rule"] for e in _inventory(repo_root) if e["tool"] == "Bandit"}
    assert documented == inventory, (
        f"Lesson 04 Files table and inventory disagree: only in README {documented - inventory}, "
        f"only in inventory {inventory - documented}"
    )


def test_demo_health_reports_missing_findings(repo_root: Path):
    module = _load_demo_health(repo_root)
    expected = module.load_inventory(repo_root / "scripts" / "expected-alerts.json")
    open_alerts = [
        {
            "tool": {"name": e["tool"]},
            "rule": {"id": e["rule"]},
            "most_recent_instance": {"location": {"path": e["path"]}},
        }
        for e in expected
    ]
    assert module.missing_expected_alerts(open_alerts, expected) == []

    dropped = expected[0]
    remaining = [
        a
        for a in open_alerts
        if (a["tool"]["name"], a["rule"]["id"], a["most_recent_instance"]["location"]["path"])
        != (dropped["tool"], dropped["rule"], dropped["path"])
    ]
    assert module.missing_expected_alerts(remaining, expected) == [dropped]


@pytest.mark.parametrize("ok,badge", [(True, "✅"), (False, "❌"), (None, "⚠️")])
def test_demo_health_table_badges(repo_root: Path, ok, badge):
    module = _load_demo_health(repo_root)
    table = module.render_table([{"name": "n", "expected": "e", "actual": "a", "ok": ok}])
    assert table.splitlines()[-1] == f"| n | e | a | {badge} |"
