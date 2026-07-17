"""
Repo-level metadata + invariants the workshop relies on.

  - README.md, LICENSE, SECURITY.md, CONTRIBUTING.md, FACILITATOR.md exist.
  - Root README has the pillar mermaid block (one ```mermaid fenced block,
    contains the `flowchart` keyword, has a matching closing fence).
  - Root README's lessons table has 11 lesson rows (one per lesson 01..11).
  - FACILITATOR's 60-minute agenda heading references lessons 1, 4, 6, 8
    (not the stale 1, 2, 3, 8 from the pre-rename layout).
  - FACILITATOR's 2-hour agenda heading references the post-rename lesson
    set (1, 2, 4, 5, 6, 7, 8 — note: NOT 3).
"""

from __future__ import annotations

import re
from pathlib import Path


def test_top_level_docs_exist(repo_root: Path):
    for name in ("README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "FACILITATOR.md"):
        assert (repo_root / name).is_file(), f"{name} missing at repo root"


def test_root_readme_has_one_mermaid_block(repo_root: Path):
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    opens = re.findall(r"^```mermaid\s*$", text, flags=re.MULTILINE)
    assert len(opens) == 1, f"Expected exactly 1 ```mermaid fence in README.md, got {len(opens)}"
    m = re.search(r"```mermaid\s*\n(.*?)\n```", text, flags=re.DOTALL)
    assert m, "README.md mermaid block not properly closed"
    assert "flowchart" in m.group(1), "README.md mermaid block missing `flowchart` directive"


def test_root_readme_fences_balanced(repo_root: Path):
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    fence_count = len(re.findall(r"^```", text, flags=re.MULTILINE))
    assert fence_count % 2 == 0, f"README.md has unbalanced ``` fences ({fence_count})"


def test_root_readme_lessons_table_has_eleven_rows(repo_root: Path):
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    refs = sorted(set(re.findall(r"`lessons/(\d{2})-[a-z0-9-]+/`", text)))
    assert refs == [f"{n:02d}" for n in range(1, 12)], (
        f"Root README lessons table should have rows for lessons 01..11; got {refs}"
    )


def test_facilitator_60min_agenda_lessons(repo_root: Path):
    text = (repo_root / "FACILITATOR.md").read_text(encoding="utf-8")
    m = re.search(
        r"###\s+60-minute\s+executive\s+overview\s+\(lessons\s+([^)]+)\)",
        text,
        flags=re.IGNORECASE,
    )
    assert m, "FACILITATOR.md missing '60-minute executive overview (lessons …)' heading"
    lessons = [int(n) for n in re.findall(r"\d+", m.group(1))]
    assert lessons == [1, 4, 6, 8], (
        f"60-minute agenda heading should list lessons 1, 4, 6, 8 (post-rename); got {lessons}"
    )


def test_facilitator_2hr_agenda_lessons(repo_root: Path):
    text = (repo_root / "FACILITATOR.md").read_text(encoding="utf-8")
    m = re.search(
        r"###\s+2-hour\s+developer\s+enablement\s+\(lessons\s+([^)]+)\)",
        text,
        flags=re.IGNORECASE,
    )
    assert m, "FACILITATOR.md missing '2-hour developer enablement (lessons …)' heading"
    lessons = [int(n) for n in re.findall(r"\d+", m.group(1))]
    assert lessons == [1, 2, 4, 5, 6, 7, 8], (
        f"2-hour agenda heading should list lessons 1, 2, 4, 5, 6, 7, 8 (post-rename, skips L3); got {lessons}"
    )


def test_facilitator_halfday_agenda_includes_all_eleven(repo_root: Path):
    text = (repo_root / "FACILITATOR.md").read_text(encoding="utf-8")
    m = re.search(r"###\s+Half-day\s+deep\s+dive\s+\(([^)]+)\)", text, flags=re.IGNORECASE)
    assert m, "FACILITATOR.md missing 'Half-day deep dive (...)' heading"
    label = m.group(1).lower()
    assert "all 11 lessons" in label or "all eleven" in label, (
        f"Half-day agenda label should advertise all 11 lessons; got: {label!r}"
    )


def test_root_readme_has_pillar_grouped_intro(repo_root: Path):
    """Sanity check the lessons-section intro text reflects the post-rename layout."""
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "Code Scanning" in text and "Secret Scanning" in text and "Supply Chain" in text, (
        "README.md should mention the GHAS pillars (Code Scanning / Secret Scanning / Supply Chain)"
    )


def test_no_aws_first_fixtures_in_lessons_04_05(repo_root: Path):
    """Lessons 04 + 05 must lead with Azure-first / Contoso fixtures, not AWS.

    Microsoft FTEs deliver this workshop to customers; AWS-shaped values
    (`AKIA…`) in source files or screenshots are off-brand. Vendor-neutrality
    may appear in *prose* (incident-response runbooks reference Azure / AWS /
    GCP side-by-side), but:

      - Lesson 05 README must not reference the legacy AKIA pattern at all
        — its custom-pattern fixtures are Contoso-prefixed.
      - Lesson 04 README may discuss AWS as a secondary vendor in prose, but
        the FIRST mention of a cloud provider in the file must be Azure.
        (Anchors the Azure-first framing for the live demo.)
    """
    l5_readme = (
        repo_root / "lessons" / "05-custom-secret-patterns" / "README.md"
    ).read_text(encoding="utf-8")
    assert "AKIA" not in l5_readme, (
        "lesson 05 README must not reference the legacy AWS AKIA pattern; "
        "lesson 05 custom-pattern fixtures are Contoso-prefixed"
    )

    l4_readme = (
        repo_root / "lessons" / "04-secret-scanning" / "README.md"
    ).read_text(encoding="utf-8")
    aws_positions = [p for p in (l4_readme.find("AWS"), l4_readme.find("AKIA")) if p != -1]
    if aws_positions:
        first_aws = min(aws_positions)
        first_azure = l4_readme.find("Azure")
        assert first_azure != -1 and first_azure < first_aws, (
            "lesson 04 README must mention Azure before any AWS/AKIA reference "
            "(Azure-first optics for Microsoft-FTE delivery)"
        )
