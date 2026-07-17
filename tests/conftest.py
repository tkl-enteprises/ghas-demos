"""
Shared pytest fixtures for the workshop-infrastructure test suite.

These tests validate static repo invariants — lesson structure, link
correctness, workflow paths, script smoke, demo-code syntax — NOT security
properties of the intentionally-vulnerable demo code.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Absolute path to the repo root (directory containing this tests/ folder's parent)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def lessons_dir(repo_root: Path) -> Path:
    return repo_root / "lessons"


@pytest.fixture(scope="session")
def lesson_dirs(lessons_dir: Path) -> list[Path]:
    """All lesson directories in their numeric/lexical order."""
    return sorted(d for d in lessons_dir.iterdir() if d.is_dir())


@pytest.fixture(scope="session")
def screenshots_dir(repo_root: Path) -> Path:
    return repo_root / "docs" / "screenshots"


@pytest.fixture(scope="session")
def workflows_dir(repo_root: Path) -> Path:
    return repo_root / ".github" / "workflows"
