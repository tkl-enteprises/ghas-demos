"""
Markdown link + screenshot integrity.

  - Every `docs/screenshots/*.{png,txt}` file is referenced from at least one
    markdown file in the repo (no orphan screenshots).
  - Every `docs/screenshots/...` reference inside any markdown file resolves
    to a file that actually exists on disk.
  - Numbered screenshots are referenced from their expected remapped lesson.
  - Relative `lessons/NN-slug/...` links inside README.md / FACILITATOR.md
    point at directories or files that exist.
"""

from __future__ import annotations

import re
from pathlib import Path


NUMBERED_SCREENSHOT_LESSONS = {
    "01-code-scanning-alerts.png": "01-code-security-codeql-scanning",
    "01-codeql-alert-detail.png": "01-code-security-codeql-scanning",
    "03-custom-codeql-alert-detail.png": "03-code-security-custom-codeql-queries",
    "03-custom-codeql-rule-list.png": "03-code-security-custom-codeql-queries",
    "04-actions-tab.png": "04-code-security-sarif-integration",
    "04-bandit-sarif-findings.png": "04-code-security-sarif-integration",
    "07-push-protection-settings.png": "07-secret-protection-secret-scanning",
    "07-secret-scanning-default-empty.png": "07-secret-protection-secret-scanning",
    "08-secret-scanning-generic-ai.png": "08-secret-protection-custom-patterns",
    "09-dependabot-alerts.png": "09-supply-chain-dependabot",
    "09-dependabot-pr-detail.png": "09-supply-chain-dependabot",
    "09-dependabot-prs-list.png": "09-supply-chain-dependabot",
    "10-org-security-overview-coverage.png": "10-governance-security-overview",
    "10-org-security-overview-risk.png": "10-governance-security-overview",
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


def test_numbered_screenshots_belong_to_remapped_lessons(repo_root, screenshots_dir):
    """Every numbered screenshot must be embedded in its mapped lesson."""
    numbered_screenshots = {
        path.name
        for path in screenshots_dir.iterdir()
        if path.is_file()
        and path.suffix == ".png"
        and NON_NUMBERED_PREFIX_RE.match(path.name)
        and not path.name.startswith("00-")
    }
    assert numbered_screenshots == set(NUMBERED_SCREENSHOT_LESSONS), (
        "Numbered screenshot mapping is incomplete or stale: "
        f"files={sorted(numbered_screenshots)}, "
        f"mapping={sorted(NUMBERED_SCREENSHOT_LESSONS)}"
    )

    violations = []
    for screenshot_name, lesson_name in NUMBERED_SCREENSHOT_LESSONS.items():
        assert screenshot_name.startswith(f"{lesson_name[:2]}-")
        lesson_dir = repo_root / "lessons" / lesson_name
        if not lesson_dir.is_dir():
            violations.append((screenshot_name, f"missing lesson {lesson_name}"))
            continue
        embedded = any(
            screenshot_name in md.read_text(encoding="utf-8")
            for md in lesson_dir.glob("*.md")
        )
        if not embedded:
            violations.append(
                (
                    screenshot_name,
                    f"not referenced from any .md in {lesson_dir.name}/",
                )
            )
    assert not violations, (
        f"Numbered-screenshot/lesson mismatches: {violations}"
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


def test_lesson_directory_refs_in_all_markdown_resolve(repo_root):
    """Every lesson directory mentioned in markdown must exist."""
    pattern = re.compile(r"\blessons/(\d{2}-[a-z0-9-]+)")
    hits = []
    for md in _all_markdown_files(repo_root):
        text = md.read_text(encoding="utf-8")
        for lesson_name in pattern.findall(text):
            if not (repo_root / "lessons" / lesson_name).is_dir():
                hits.append((str(md.relative_to(repo_root)), lesson_name))
    assert not hits, f"Markdown references missing lesson directories: {hits}"
