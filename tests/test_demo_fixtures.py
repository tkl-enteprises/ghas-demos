"""Regression guards for intentionally vulnerable and quality demo fixtures."""

from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest


DEPENDABOT_PINS = (
    "Flask==0.12.0",
    "Jinja2==2.10",
    "Werkzeug==0.14",
    "urllib3==1.24.1",
    "requests==2.19.1",
    "PyYAML==5.1",
    "cryptography==2.3",
)

QUALITY_RULE_IDS = {
    "js/template-syntax-in-string-literal",
    "js/useless-assignment-to-local",
}


def _lesson(repo_root: Path, name: str) -> Path:
    return repo_root / "lessons" / name


def _requirements_pins(path: Path) -> tuple[str, ...]:
    return tuple(
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def _section(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        markdown,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, f"Missing {heading!r} section"
    return match.group(1)


def _markdown_table(markdown: str, header: str) -> dict[str, list[str]]:
    lines = markdown.splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.startswith(f"| {header} ")),
        None,
    )
    assert header_index is not None, f"Missing markdown table headed by {header!r}"

    rows: dict[str, list[str]] = {}
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        rows[cells[0]] = cells[1:]
    return rows


def _module_boolean_assignments(path: Path) -> dict[str, bool]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assignments = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, bool)
        ):
            assignments[node.targets[0].id] = node.value.value
    return assignments


def test_lesson03_custom_query_and_controls_stay_aligned(repo_root: Path):
    lesson = _lesson(repo_root, "03-code-security-custom-codeql-queries")
    query_path = (
        repo_root / ".github" / "codeql" / "custom-queries" / "PutinKhuyloFalse.ql"
    )
    query = query_path.read_text(encoding="utf-8")

    assert "@id py/tkl/putin-khuylo-false" in query
    assert 'n.getId() = "putin_khuylo"' in query
    assert 'v.toString() = "False"' in query
    assert _module_boolean_assignments(lesson / "noncompliant.py")[
        "putin_khuylo"
    ] is False
    assert _module_boolean_assignments(lesson / "compliant.py")[
        "putin_khuylo"
    ] is True


def test_lesson09_manifests_match_all_intentional_pins(repo_root: Path):
    lesson = _lesson(repo_root, "09-supply-chain-dependabot")
    requirements = _requirements_pins(lesson / "requirements.txt")
    pyproject = tomllib.loads((lesson / "pyproject.toml").read_text(encoding="utf-8"))
    project_dependencies = tuple(pyproject["project"]["dependencies"])

    assert requirements == DEPENDABOT_PINS
    assert project_dependencies == DEPENDABOT_PINS
    assert requirements == project_dependencies


def test_lesson09_vulnerable_baseline_is_documented(repo_root: Path):
    lesson = _lesson(repo_root, "09-supply-chain-dependabot")
    readme = (lesson / "README.md").read_text(encoding="utf-8")
    solution = (lesson / "solution.md").read_text(encoding="utf-8")
    rows = _markdown_table(readme, "Package")

    assert rows["Werkzeug"][:4] == [
        "0.14",
        "GHSA-2g68-c3qc-8985",
        "High",
        "3.0.3",
    ]
    assert rows["cryptography"][:4] == [
        "2.3",
        "GHSA-hggm-jpg3-v476",
        "High",
        "3.2",
    ]

    documented_pins = set(
        re.findall(
            r"`([A-Za-z0-9_.-]+==[A-Za-z0-9_.+-]+)`",
            _section(solution, "Fixture integrity"),
        )
    )
    assert documented_pins == set(DEPENDABOT_PINS)


def test_lesson09_safety_warnings_remain(repo_root: Path):
    lesson = _lesson(repo_root, "09-supply-chain-dependabot")
    readme = (lesson / "README.md").read_text(encoding="utf-8")
    requirements_intro = "\n".join(
        (lesson / "requirements.txt").read_text(encoding="utf-8").splitlines()[:2]
    )
    pyproject_intro = "\n".join(
        (lesson / "pyproject.toml").read_text(encoding="utf-8").splitlines()[:3]
    )
    app_intro = "\n".join(
        (lesson / "app.py").read_text(encoding="utf-8").splitlines()[:5]
    )
    readme_intro = readme.partition("## Goal")[0]
    fixture_guidance = _section(
        (lesson / "solution.md").read_text(encoding="utf-8"), "Fixture integrity"
    )

    for manifest_intro in (requirements_intro, pyproject_intro):
        assert "INTENTIONALLY VULNERABLE" in manifest_intro.upper()
    assert "INTENTIONALLY VULNERABLE" in app_intro.upper()
    assert re.search(r"\bdo not deploy\b", app_intro, flags=re.IGNORECASE)
    assert "intentionally vulnerable" in readme_intro.lower()
    assert re.search(r"\bdo not install\b", readme_intro, flags=re.IGNORECASE)
    assert re.search(r"\bnever install\b", fixture_guidance, flags=re.IGNORECASE)
    assert re.search(r"\bexecute `app\.py`", fixture_guidance, flags=re.IGNORECASE)


def test_lesson11_retains_quality_defects_and_solution(repo_root: Path):
    lesson = _lesson(repo_root, "11-code-quality-analysis")
    fixture = (lesson / "quality-fixtures.js").read_text(encoding="utf-8")
    readme = (lesson / "README.md").read_text(encoding="utf-8")
    solution = (lesson / "solution.md").read_text(encoding="utf-8")

    documented_rules = set(re.findall(r"\bjs/[a-z0-9-]+\b", readme))
    solution_rules = set(re.findall(r"\bjs/[a-z0-9-]+\b", solution))
    assert documented_rules == QUALITY_RULE_IDS
    assert solution_rules == QUALITY_RULE_IDS
    assert re.search(
        r"\[`js/template-syntax-in-string-literal`\]\([^)]+\)"
        r"\s*\|\s*Reliability\s*\|\s*Warning\s*\|\s*High\s*\|",
        readme,
    )
    assert re.search(
        r"\[`js/useless-assignment-to-local`\]\([^)]+\)"
        r"\s*\|\s*Maintainability\s*\|\s*Warning\s*\|\s*Very high\s*\|",
        readme,
    )

    assert re.search(r"`[^`]*\$\{userName\}[^`]*`", fixture)
    assert re.search(r'["\'][^"\']*\$\{userName\}[^"\']*["\']', fixture)
    assert re.search(
        r"let\s+completed\s*=\s*tasks\.length\s*;"
        r"\s*completed\s*=\s*tasks\.filter\(",
        fixture,
    )

    assert re.search(r"message:\s*`[^`]*\$\{userName\}[^`]*`", solution)
    assert re.search(r"const\s+completed\s*=\s*tasks\.filter\(", solution)
    assert re.search(r"\bdo\s+not\s+merge\b", solution, flags=re.IGNORECASE)


def test_lesson11_fixture_is_runnable_and_inert(repo_root: Path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is optional; static fixture checks still ran")

    fixture = _lesson(repo_root, "11-code-quality-analysis") / "quality-fixtures.js"
    harness = r"""
const assert = require("node:assert/strict");
const Module = require("node:module");

const fixturePath = process.argv[1];
const originalLoad = Module._load;
Module._load = function (request, parent, isMain) {
  if (request === fixturePath) {
    return originalLoad.call(this, request, parent, isMain);
  }
  throw new Error(`Fixture imported unexpected module: ${request}`);
};

for (const name of ["fetch", "setInterval", "setTimeout"]) {
  globalThis[name] = () => {
    throw new Error(`Fixture invoked ${name}`);
  };
}
for (const name of ["debug", "error", "info", "log", "warn"]) {
  console[name] = () => {
    throw new Error(`Fixture wrote to console.${name}`);
  };
}

const fixtures = require(fixturePath);
assert.deepEqual(Object.keys(fixtures).sort(), ["buildGreeting", "countCompleted"]);
assert.deepEqual(fixtures.buildGreeting("Ada"), {
  preview: "Preview for Ada",
  message: "Welcome, ${userName}!",
});
assert.equal(
  fixtures.countCompleted([{ complete: true }, { complete: false }]),
  1,
);
"""
    result = subprocess.run(
        [node, "--check", str(fixture)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr

    result = subprocess.run(
        [node, "-e", harness, str(fixture.resolve())],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_security_fixtures_cannot_activate_accidentally(repo_root: Path):
    actions_fixtures = _lesson(repo_root, "05-code-security-actions") / "fixtures"
    fixture_files = sorted(path.name for path in actions_fixtures.iterdir() if path.is_file())
    assert fixture_files == [
        "remediated-workflow.yml.txt",
        "vulnerable-workflow.yml.txt",
    ]

    ai_samples = _lesson(repo_root, "06-code-security-ai-detections") / "samples"
    sample_files = {path.name: path for path in ai_samples.iterdir() if path.is_file()}
    assert set(sample_files) == {"Dockerfile", "main.tf", "preview_path.bash", "query.php"}
    assert all(not os.access(path, os.X_OK) for path in sample_files.values())

    workflow_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (repo_root / ".github" / "workflows").glob("*.yml")
    )
    assert "05-code-security-actions/fixtures" not in workflow_text
    assert "06-code-security-ai-detections/samples" not in workflow_text

    assert re.search(r"^\s*count\s*=\s*0\s*$", sample_files["main.tf"].read_text(), re.MULTILINE)
    dockerfile = sample_files["Dockerfile"].read_text(encoding="utf-8")
    assert not re.search(r"^\s*(RUN|CMD|ENTRYPOINT)\b", dockerfile, re.MULTILINE)
    assert sample_files["preview_path.bash"].read_text().count("preview_path") == 1
    assert sample_files["query.php"].read_text().count("findUser") == 1


def test_lesson05_secret_exposure_demo_stays_disabled(repo_root: Path):
    workflow = (
        repo_root / ".github" / "workflows" / "lesson-05-vulnerable.yml"
    ).read_text(encoding="utf-8")

    assert re.search(r"^\s{4}if:\s*\$\{\{\s*false\s*\}\}\s*$", workflow, re.MULTILINE)
    assert "fromJSON(secrets.LESSON_05_CREDENTIALS).password" in workflow
    assert 'run: echo "${{ fromJSON(secrets.LESSON_05_CREDENTIALS).password }}"' in workflow
