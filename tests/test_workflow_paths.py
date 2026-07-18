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


EXPECTED_BANDIT_TARGET = "lessons/04-code-security-sarif-integration"
EXPECTED_TRIVY_TARGET = "lessons/06-code-security-ai-detections"
EXPECTED_DEPENDABOT_LESSON_DIRECTORIES = {
    "/lessons/04-code-security-sarif-integration",
    "/lessons/09-supply-chain-dependabot",
}
EXPECTED_CODEQL_PATHS_IGNORE = ["lessons/04-code-security-sarif-integration/**"]
EXPECTED_DEPENDABOT_LESSON_METADATA = {
    "/lessons/04-code-security-sarif-integration": {
        "groups": set(),
        "labels": {"dependencies", "lesson-04"},
    },
    "/lessons/09-supply-chain-dependabot": {
        "groups": {"lesson-nine-security-updates"},
        "labels": {"dependencies", "lesson-09"},
    },
}


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
    assert m.group(1) == EXPECTED_BANDIT_TARGET
    target = repo_root / m.group(1)
    assert target.is_dir(), (
        f"sarif-bandit.yml runs `bandit -r {m.group(1)}` but {target} is not a directory"
    )


def test_trivy_target_path_exists(repo_root, workflows_dir):
    text = (workflows_dir / "lesson-06-trivy.yml").read_text(encoding="utf-8")
    m = re.search(r"scan-ref:\s*(\S+)", text)
    assert m, "Expected `scan-ref: <path>` in lesson-06-trivy.yml"
    assert m.group(1) == EXPECTED_TRIVY_TARGET
    assert (repo_root / m.group(1)).is_dir()
    assert re.search(r"^\s+scanners:\s*misconfig\s*$", text, re.MULTILINE)
    assert re.search(r"^\s+format:\s*sarif\s*$", text, re.MULTILINE)
    assert "github/codeql-action/upload-sarif@" in text


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
    lesson_directories = {
        entry.get("directory")
        for entry in updates
        if str(entry.get("directory", "")).startswith("/lessons/")
    }
    assert lesson_directories == EXPECTED_DEPENDABOT_LESSON_DIRECTORIES
    for entry in updates:
        directory = entry.get("directory")
        assert directory, f"dependabot.yml entry missing `directory`: {entry}"
        rel = directory.lstrip("/")
        target = repo_root / rel if rel else repo_root
        assert target.is_dir(), (
            f"dependabot.yml `directory: {directory}` does not resolve "
            f"(expected {target})"
        )
        if directory in EXPECTED_DEPENDABOT_LESSON_METADATA:
            expected = EXPECTED_DEPENDABOT_LESSON_METADATA[directory]
            assert set((entry.get("groups") or {}).keys()) == expected["groups"]
            assert set(entry.get("labels") or []) == expected["labels"]


def test_codeql_config_paths_ignore_resolve(repo_root):
    cfg = yaml.safe_load(
        (repo_root / ".github" / "codeql" / "codeql-config.yml").read_text(encoding="utf-8")
    )
    paths_ignore = cfg.get("paths-ignore") or []
    assert paths_ignore == EXPECTED_CODEQL_PATHS_IGNORE
    for glob_pat in paths_ignore:
        base = glob_pat.rstrip("/*")
        target = repo_root / base
        assert target.exists(), (
            f"codeql-config.yml paths-ignore `{glob_pat}` does not match anything "
            f"(looked for {target})"
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
