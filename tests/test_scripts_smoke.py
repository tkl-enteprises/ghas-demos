"""
Smoke-test the helper scripts under `scripts/`.

  - `scripts/preflight.sh`: executable bit set; `bash -n` syntax check passes.
  - `scripts/demo-health.py`: importable as a Python module without raising;
    when run with no GITHUB_TOKEN, prints a helpful message (not a stack
    trace). We accept its current exit code rather than dictating one — the
    spec is "doesn't crash with a stack trace; mentions GITHUB_TOKEN".
"""

from __future__ import annotations

import os
import py_compile
import subprocess
from pathlib import Path


def test_preflight_is_executable(repo_root: Path):
    p = repo_root / "scripts" / "preflight.sh"
    assert p.is_file(), f"{p} missing"
    assert os.access(p, os.X_OK), f"{p} is not executable (chmod +x scripts/preflight.sh)"


def test_preflight_has_bash_shebang(repo_root: Path):
    p = repo_root / "scripts" / "preflight.sh"
    first = p.read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("#!") and "bash" in first, (
        f"{p} missing bash shebang; got {first!r}"
    )


def test_preflight_bash_syntax_ok(repo_root: Path):
    p = repo_root / "scripts" / "preflight.sh"
    result = subprocess.run(
        ["bash", "-n", str(p)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"bash -n failed on {p}:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_demo_health_compiles(repo_root: Path):
    p = repo_root / "scripts" / "demo-health.py"
    assert p.is_file(), f"{p} missing"
    py_compile.compile(str(p), doraise=True)


def test_demo_health_handles_missing_token(repo_root: Path):
    """Running without GITHUB_TOKEN should produce a friendly error, not a crash."""
    p = repo_root / "scripts" / "demo-health.py"
    env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
    result = subprocess.run(
        ["python3", str(p)],
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )
    combined = (result.stdout + result.stderr).lower()
    assert "github_token" in combined, (
        f"demo-health.py should mention GITHUB_TOKEN when missing; "
        f"got stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    assert "traceback" not in combined, (
        f"demo-health.py crashed with a Python traceback when GITHUB_TOKEN missing:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
