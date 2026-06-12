"""
Validate that paths referenced in CI/automation YAML actually exist.

  - Every `.github/workflows/*.yml` parses as YAML.
  - Path arguments to `bandit -r ...`, `python3 scripts/...`, etc. resolve.
  - `dependabot.yml` `directory:` paths resolve to existing directories.
  - `codeql-config.yml` `paths-ignore:` globs resolve to ≥1 existing path.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


def test_each_workflow_parses_as_yaml(workflows_dir):
    files = sorted(workflows_dir.glob("*.yml"))
    assert files, "No workflow YAML files found"
    for f in files:
        try:
            yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            pytest.fail(f"{f} failed to parse: {e}")


def test_bandit_target_path_exists(repo_root, workflows_dir):
    text = (workflows_dir / "sarif-bandit.yml").read_text(encoding="utf-8")
    m = re.search(r"bandit\s+-r\s+(\S+)", text)
    assert m, "Expected `bandit -r <path>` in sarif-bandit.yml"
    target = repo_root / m.group(1)
    assert target.is_dir(), (
        f"sarif-bandit.yml runs `bandit -r {m.group(1)}` but {target} is not a directory"
    )


def test_demo_health_script_path_exists(repo_root, workflows_dir):
    text = (workflows_dir / "demo-health.yml").read_text(encoding="utf-8")
    m = re.search(r"python3?\s+(scripts/\S+)", text)
    assert m, "Expected `python3 scripts/...` in demo-health.yml"
    target = repo_root / m.group(1)
    assert target.is_file(), f"demo-health.yml runs {m.group(1)} but {target} is missing"


def test_dependabot_directories_resolve(repo_root):
    cfg = yaml.safe_load(
        (repo_root / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    )
    updates = cfg.get("updates") or []
    assert updates, "dependabot.yml has no updates entries"
    for entry in updates:
        directory = entry.get("directory")
        assert directory, f"dependabot.yml entry missing `directory`: {entry}"
        rel = directory.lstrip("/")
        target = repo_root / rel if rel else repo_root
        assert target.is_dir(), (
            f"dependabot.yml `directory: {directory}` does not resolve "
            f"(expected {target})"
        )


def test_codeql_config_paths_ignore_resolve(repo_root):
    cfg = yaml.safe_load(
        (repo_root / ".github" / "codeql" / "codeql-config.yml").read_text(encoding="utf-8")
    )
    for glob_pat in cfg.get("paths-ignore") or []:
        rel_pat = glob_pat.lstrip("/")
        matches = list(repo_root.glob(rel_pat))
        assert matches, (
            f"codeql-config.yml paths-ignore `{glob_pat}` does not match anything "
            f"(looked for glob `{rel_pat}` under {repo_root})"
        )


def test_codeql_config_queries_pack_exists(repo_root):
    cfg = yaml.safe_load(
        (repo_root / ".github" / "codeql" / "codeql-config.yml").read_text(encoding="utf-8")
    )
    for entry in cfg.get("queries") or []:
        uses = entry.get("uses") if isinstance(entry, dict) else None
        if not uses or not uses.startswith("./"):
            continue
        target = repo_root / uses[2:]
        assert target.exists(), f"codeql-config.yml `uses: {uses}` does not resolve"
