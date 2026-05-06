"""
Demo-code syntax/manifest sanity.

The lessons ship intentionally vulnerable Python — we do NOT assert security
properties here. We only confirm:

  - Every `lessons/**/*.py` byte-compiles cleanly (no syntax errors).
  - Every `lessons/**/requirements.txt` line is either blank, a comment,
    or `package(==|>=|<=|~=|>|<)version`-shaped.
"""

from __future__ import annotations

import py_compile
import re
from pathlib import Path

import pytest


REQUIREMENT_LINE_RE = re.compile(
    r"^[A-Za-z0-9_.\-]+(\[[A-Za-z0-9_.,\-]+\])?\s*(==|>=|<=|~=|>|<)\s*[A-Za-z0-9_.\-+]+\s*$"
)

# Regression guard for Part 6 (Microsoft-FTE optics). Catches AWS-shaped
# access keys committed in any `lessons/**/*.py` fixture. Keep the regex
# narrow to AKIA + 16+ alphanumerics so it doesn't match unrelated prose.
AKIA_PATTERN = re.compile(r"AKIA[A-Z0-9]{16,}")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_LESSONS = _REPO_ROOT / "lessons"


def _all_lesson_python_files() -> list[Path]:
    return sorted(_LESSONS.rglob("*.py"))


def _all_requirements_files() -> list[Path]:
    return sorted(_LESSONS.rglob("requirements.txt"))


def test_lesson_python_files_exist(lessons_dir):
    files = sorted(lessons_dir.rglob("*.py"))
    assert files, "Expected at least one lesson Python file"


@pytest.mark.parametrize(
    "py_file",
    _all_lesson_python_files(),
    ids=lambda p: str(p.relative_to(_REPO_ROOT)),
)
def test_lesson_python_compiles(py_file: Path):
    """Every demo Python file must be syntactically valid Python 3."""
    py_compile.compile(str(py_file), doraise=True)


@pytest.mark.parametrize(
    "req_file",
    _all_requirements_files(),
    ids=lambda p: str(p.relative_to(_REPO_ROOT)),
)
def test_requirements_lines_well_formed(req_file: Path):
    """Each non-blank, non-comment line must be `package<op>version`-shaped."""
    bad = []
    for lineno, raw in enumerate(req_file.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not REQUIREMENT_LINE_RE.match(line):
            bad.append((lineno, raw))
    assert not bad, f"Malformed requirements.txt lines in {req_file}: {bad}"


def test_no_aws_access_key_shapes_in_lesson_python(lessons_dir):
    """No `lessons/**/*.py` fixture may contain an AWS-shaped access-key string.

    Microsoft FTEs deliver this workshop to customers; AWS-shaped fixtures
    (`AKIA[A-Z0-9]{16,}`) are off-brand. Use Azure storage connection strings
    or Contoso-prefixed custom-pattern fixtures instead. Vendor-neutrality
    lives in *prose* (e.g. solution.md's Azure / AWS / GCP runbook table),
    not in the demo source files.

    The regex literal `AKIA[A-Z0-9]{16,}` lives in the test file itself —
    that's the regression guard, not a violation. The check scans only
    `lessons/**/*.py`, so the test file is intentionally out of scope.
    """
    offenders = []
    for py_file in sorted(lessons_dir.rglob("*.py")):
        text = py_file.read_text(encoding="utf-8")
        if AKIA_PATTERN.search(text):
            offenders.append(str(py_file.relative_to(lessons_dir)))
    assert not offenders, (
        f"AWS-shaped fixtures (AKIA…) found in lesson Python files: {offenders} "
        "— use Azure / Contoso fixtures instead (Microsoft-FTE optics)"
    )
