"""
Markdown link + screenshot integrity.

  - Every `docs/screenshots/*.{png,txt}` file is referenced from at least one
    markdown file in the repo (no orphan screenshots).
  - Every `docs/screenshots/...` reference inside any markdown file resolves
    to a file that actually exists on disk.
  - Numbered screenshots `0N-*.png` are referenced from `lessons/0N-*/`
    (with explicit skip-list for known pre-existing exceptions).
  - Relative `lessons/NN-slug/...` links inside README.md / FACILITATOR.md
    point at directories or files that exist.
"""

from __future__ import annotations

import re
from pathlib import Path


# Files where the numbered-prefix-must-equal-lesson-prefix convention is
# intentionally relaxed (pre-existing screenshot/lesson naming drift, NOT a
# Part 1 rename regression). Comments below explain each case.
NUMBERED_PREFIX_SKIPS = {
    # Used by lesson 01 by intention — pre-existing misnumber, called out in
    # FACILITATOR.md's screenshot table.
    "02-codeql-alert-detail.png",
    # Renamed from 06-secret-scanning-default-empty.png in C3 (lesson 06 -> 05);
    # the screenshot is conceptually a Secret-Scanning-pillar visual referenced
    # from lesson 04, not lesson 05. The rename followed the lesson dir number,
    # not the lesson where it's embedded.
    "05-secret-scanning-default-empty.png",
}

NON_NUMBERED_PREFIX_RE = re.compile(r"^\d{2}-")


def _all_markdown_files(repo_root: Path) -> list[Path]:
    return [
        p
        for p in repo_root.rglob("*.md")
        if ".git" not in p.parts and "node_modules" not in p.parts
    ]


def _all_markdown_text(repo_root: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in _all_markdown_files(repo_root))


def test_no_orphan_screenshots(repo_root, screenshots_dir):
    md_blob = _all_markdown_text(repo_root)
    orphans = []
    for f in screenshots_dir.iterdir():
        if not f.is_file():
            continue
        if f.name not in md_blob:
            orphans.append(f.name)
    assert not orphans, f"Orphan screenshot files (no markdown ref): {orphans}"


def test_screenshot_refs_resolve(repo_root, screenshots_dir):
    pattern = re.compile(r"docs/screenshots/([A-Za-z0-9._-]+)")
    missing = set()
    for md in _all_markdown_files(repo_root):
        for ref in pattern.findall(md.read_text(encoding="utf-8")):
            if not (screenshots_dir / ref).is_file():
                missing.add((str(md.relative_to(repo_root)), ref))
    assert not missing, f"Broken docs/screenshots refs: {sorted(missing)}"


def test_numbered_screenshot_belongs_to_matching_lesson(repo_root, screenshots_dir):
    """0N-*.png must be embedded in lessons/0N-*/ (README.md or solution.md)."""
    violations = []
    for f in sorted(screenshots_dir.iterdir()):
        if not f.is_file() or f.suffix != ".png":
            continue
        if not NON_NUMBERED_PREFIX_RE.match(f.name):
            continue
        if f.name in NUMBERED_PREFIX_SKIPS:
            continue
        prefix = f.name[:2]
        if prefix == "00":
            continue  # Root README hero, not a per-lesson screenshot.
        lesson_matches = list((repo_root / "lessons").glob(f"{prefix}-*"))
        if not lesson_matches:
            violations.append((f.name, f"no lesson dir with prefix {prefix}"))
            continue
        lesson_dir = lesson_matches[0]
        embedded = any(
            f.name in md.read_text(encoding="utf-8")
            for md in lesson_dir.glob("*.md")
        )
        if not embedded:
            violations.append(
                (f.name, f"not referenced from any .md in {lesson_dir.name}/")
            )
    assert not violations, (
        f"Numbered-screenshot/lesson mismatches: {violations}\n"
        f"Either embed the screenshot in the matching lesson, rename it, or "
        f"add it to NUMBERED_PREFIX_SKIPS with a comment."
    )


def test_lesson_dir_links_in_root_readme_resolve(repo_root):
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    for ref in re.findall(r"\(lessons/(\d{2}-[a-z0-9-]+)/?\)", text):
        target = repo_root / "lessons" / ref
        assert target.is_dir(), f"README.md links to non-existent lessons/{ref}/"


def test_lesson_dir_links_in_facilitator_resolve(repo_root):
    text = (repo_root / "FACILITATOR.md").read_text(encoding="utf-8")
    for ref in re.findall(r"\(lessons/(\d{2}-[a-z0-9-]+)/?\)", text):
        target = repo_root / "lessons" / ref
        assert target.is_dir(), f"FACILITATOR.md links to non-existent lessons/{ref}/"


def test_no_old_lesson_path_refs(repo_root):
    """No lingering refs to the pre-pillar-grouped layout.

    The old (pre-rename) layout used:
      lessons/02-secret-scanning, lessons/03-dependabot-supply-chain,
      lessons/04-copilot-autofix, lessons/05-custom-codeql-queries,
      lessons/06-custom-secret-patterns
    """
    forbidden_paths = {
        "lessons/02-secret-scanning",
        "lessons/03-dependabot-supply-chain",
        "lessons/04-copilot-autofix",
        "lessons/05-custom-codeql-queries",
        "lessons/06-custom-secret-patterns",
    }
    hits = []
    for md in _all_markdown_files(repo_root):
        text = md.read_text(encoding="utf-8")
        for old in forbidden_paths:
            if old in text:
                hits.append((str(md.relative_to(repo_root)), old))
    assert not hits, f"Stale lesson paths still referenced: {hits}"
