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
