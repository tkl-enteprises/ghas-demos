"""
Repo-level metadata + invariants the workshop relies on.

  - README.md, LICENSE, SECURITY.md, CONTRIBUTING.md, FACILITATOR.md exist.
  - Root README has the pillar mermaid block (one ```mermaid fenced block,
    contains the `flowchart` keyword, has a matching closing fence).
  - Root README's lessons table matches the exact pillar-grouped lesson map.
  - FACILITATOR agendas reference lessons by their pillar-grouped numbers.
"""

from __future__ import annotations

import re
from pathlib import Path


EXPECTED_LESSON_NAMES = [
    "01-code-security-codeql-scanning",
    "02-code-security-copilot-autofix",
    "03-code-security-custom-codeql-queries",
    "04-code-security-sarif-integration",
    "05-code-security-actions",
    "06-code-quality-standard-findings",
    "07-code-quality-ai-findings",
    "08-secret-protection-secret-scanning",
    "09-secret-protection-custom-patterns",
    "10-supply-chain-dependabot",
    "11-governance-security-overview",
]


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


def test_root_readme_lessons_table_matches_pillar_order(repo_root: Path):
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    refs = re.findall(r"`lessons/(\d{2}-[a-z0-9-]+)/`", text)
    assert refs == EXPECTED_LESSON_NAMES, (
        f"Root README lessons table should match the ordered pillar map; got {refs}"
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
    assert lessons == [1, 8, 10, 11], (
        f"60-minute agenda should list remapped lessons 1, 8, 10, 11; got {lessons}"
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
    assert lessons == [1, 2, 4, 8, 9, 10, 11], (
        "2-hour agenda should list remapped lessons in pillar order "
        f"(1, 2, 4, 8, 9, 10, 11); got {lessons}"
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
    """Sanity check the lessons section names every recognized pillar."""
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    expected_pillars = (
        "Code Security",
        "Secret Protection",
        "Supply Chain",
        "Governance",
        "Code Quality",
    )
    missing = [pillar for pillar in expected_pillars if pillar not in text]
    assert not missing, f"README.md should mention every lesson pillar; missing {missing}"


def test_no_aws_first_fixtures_in_secret_protection_lessons(repo_root: Path):
    """Secret Protection lessons must lead with Azure-first / Contoso fixtures.

    Microsoft FTEs deliver this workshop to customers; AWS-shaped values
    (`AKIA…`) in source files or screenshots are off-brand. Vendor-neutrality
    may appear in *prose* (incident-response runbooks reference Azure / AWS /
    GCP side-by-side), but:

      - Custom Patterns README must not reference the legacy AKIA pattern at all
        — its custom-pattern fixtures are Contoso-prefixed.
      - Secret Scanning README may discuss AWS as a secondary vendor in prose, but
        the FIRST mention of a cloud provider in the file must be Azure.
        (Anchors the Azure-first framing for the live demo.)
    """
    custom_patterns_readme = (
        repo_root
        / "lessons"
        / "09-secret-protection-custom-patterns"
        / "README.md"
    ).read_text(encoding="utf-8")
    assert "AKIA" not in custom_patterns_readme, (
        "custom-pattern README must not reference the legacy AWS AKIA pattern; "
        "its fixtures are Contoso-prefixed"
    )

    secret_scanning_readme = (
        repo_root
        / "lessons"
        / "08-secret-protection-secret-scanning"
        / "README.md"
    ).read_text(encoding="utf-8")
    aws_positions = [
        position
        for position in (
            secret_scanning_readme.find("AWS"),
            secret_scanning_readme.find("AKIA"),
        )
        if position != -1
    ]
    if aws_positions:
        first_aws = min(aws_positions)
        first_azure = secret_scanning_readme.find("Azure")
        assert first_azure != -1 and first_azure < first_aws, (
            "secret-scanning README must mention Azure before any AWS/AKIA reference "
            "(Azure-first optics for Microsoft-FTE delivery)"
        )
