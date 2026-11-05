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
EXPECTED_DEPENDABOT_LESSON_DIRECTORIES = {
    "/lessons/04-code-security-sarif-integration",
    "/lessons/10-supply-chain-dependabot",
}
EXPECTED_CODEQL_PATHS_IGNORE = ["lessons/04-code-security-sarif-integration/**"]
EXPECTED_DEPENDABOT_LESSON_METADATA = {
    "/lessons/04-code-security-sarif-integration": {
        "groups": set(),
        "labels": {"dependencies", "lesson-04"},
    },
    "/lessons/10-supply-chain-dependabot": {
        "groups": {"lesson-ten-security-updates", "lesson-ten-version-updates"},
        "labels": {"dependencies", "lesson-10"},
    },
}
USES_RE = re.compile(r"^\s*(?:-\s+)?uses:\s*(?P<ref>\S+)(?P<comment>.*)$", re.MULTILINE)


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


def test_codeql_analyzes_github_actions(workflows_dir):
    cfg = yaml.safe_load((workflows_dir / "codeql.yml").read_text(encoding="utf-8"))
    job = cfg["jobs"]["analyze-actions"]
    init_step = next(
        step
        for step in job["steps"]
        if str(step.get("uses", "")).startswith("github/codeql-action/init@")
    )
    analyze_step = next(
        step
        for step in job["steps"]
        if str(step.get("uses", "")).startswith("github/codeql-action/analyze@")
    )

    assert init_step["with"] == {
        "languages": "actions",
        "build-mode": "none",
        "queries": "security-extended",
    }
    assert analyze_step["with"]["category"] == "/language:actions"


def _workflow_action_refs(workflows_dir) -> list[tuple[str, str, str]]:
    """(file, action@ref, trailing comment) for every remote `uses:` step."""
    refs = []
    for f in sorted(workflows_dir.glob("*.yml")):
        for m in USES_RE.finditer(f.read_text(encoding="utf-8")):
            ref = m.group("ref")
            if ref.startswith(("./", "docker://")):
                continue
            refs.append((f.name, ref, m.group("comment").strip()))
    return refs


def test_workflow_actions_are_pinned_to_full_commit_shas(workflows_dir):
    """Practice what lesson 05 teaches: every action is pinned to a full SHA
    with a matching `# vX.Y.Z` comment so Dependabot can keep it current."""
    refs = _workflow_action_refs(workflows_dir)
    assert refs, "Expected at least one `uses:` step in .github/workflows/"
    unpinned = [
        (f, ref, comment)
        for f, ref, comment in refs
        if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", ref)
        or not re.fullmatch(r"#\s*v\d+(\.\d+){0,2}", comment)
    ]
    assert not unpinned, f"Actions must be pinned to a full SHA with a version comment: {unpinned}"


def test_codeql_action_steps_share_one_version(workflows_dir):
    """init/analyze/upload-sarif must run the same codeql-action release, otherwise
    the job fails with "Loaded a configuration file for version X, but running Y"."""
    versions = {
        ref.split("@", 1)[1]
        for _, ref, _ in _workflow_action_refs(workflows_dir)
        if ref.startswith("github/codeql-action/")
    }
    assert len(versions) == 1, f"github/codeql-action steps use different versions: {versions}"


def test_dependabot_groups_github_actions_updates(repo_root):
    cfg = yaml.safe_load(
        (repo_root / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    )
    entry = next(
        (u for u in cfg["updates"] if u.get("package-ecosystem") == "github-actions"),
        None,
    )
    assert entry is not None, "dependabot.yml should keep GitHub Actions updated"
    patterns = [
        pattern
        for group in (entry.get("groups") or {}).values()
        for pattern in group.get("patterns") or []
    ]
    assert "*" in patterns or any(p.startswith("github/codeql-action") for p in patterns), (
        "Group the github/codeql-action updates so init/analyze/upload-sarif bump together"
    )


def test_dependabot_lesson_directories_have_a_manifest(repo_root):
    """A pip entry without a manifest makes every Dependabot run fail."""
    cfg = yaml.safe_load(
        (repo_root / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    )
    for entry in cfg["updates"]:
        if entry.get("package-ecosystem") != "pip":
            continue
        directory = repo_root / entry["directory"].lstrip("/")
        manifests = [
            name
            for name in ("requirements.txt", "pyproject.toml", "setup.py", "Pipfile")
            if (directory / name).is_file()
        ]
        assert manifests, f"{entry['directory']} has no pip manifest for Dependabot"
