#!/usr/bin/env bash
# Post-create setup for the GHAS Demos workshop dev container.
# Idempotent: safe to re-run. Lesson dep installs are best-effort —
# some lessons intentionally pin known-vulnerable old versions that
# will not install on Python 3.11, and that's the point of the lesson.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "▶ Installing workshop dev tools (bandit, pip-tools, pytest)…"
pip install --user --upgrade bandit pip-tools pytest || \
  echo "⚠ Dev tool install reported errors — continuing."

shopt -s nullglob
for req in lessons/*/requirements.txt; do
  lesson_dir="$(dirname "$req")"
  lesson_name="$(basename "$lesson_dir")"
  echo "▶ Installing deps for ${lesson_name}…"
  if pip install --user -r "$req"; then
    echo "✓ ${lesson_name} deps installed."
  else
    echo "ℹ ${lesson_name} deps did not install — that's expected if this lesson"
    echo "  pins intentionally-vulnerable old versions (e.g. Flask 0.12 on"
    echo "  Python 3.11). Lesson 09 demonstrates them via Dependabot, not"
    echo "  local execution."
  fi
done
shopt -u nullglob

cat <<'BANNER'

╔══════════════════════════════════════════════════════════════════╗
║  ✅ GHAS Demos workshop ready.                                   ║
║     Open README.md and start at lesson 01.                       ║
╚══════════════════════════════════════════════════════════════════╝

BANNER
