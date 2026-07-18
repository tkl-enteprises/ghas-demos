"""
Per-lesson README sanity:

  - 11 lessons exist (01..11), no gaps.
  - Each lesson dir name matches the ordered `NN-pillar-lesson` map and has a
    README.md.
  - README starts with `# Lesson NN` (number matches dir prefix).
  - Each README contains the standardized H2 sections.
  - Most lessons use `## Hands-on steps`; some use `## Walkthrough` or
    `## Step-by-step navigation` —
    the test accepts either spelling for the "steps" heading.
  - Same for `## Discussion questions` vs `## Discussion prompts`.
  - README is non-empty (>500 chars) so we don't ship blank scaffolds.
  - Root README's lessons table contains exactly 11 rows referring to all 11
    lesson folders.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


EXPECTED_LESSON_NAMES = (
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
)
EXPECTED_LESSON_PREFIXES = tuple(f"{n:02d}" for n in range(1, 12))
RECOGNIZED_PILLARS = (
    "code-security",
    "secret-protection",
    "supply-chain",
    "governance",
    "code-quality",
)
EXPECTED_PILLAR_ORDER = (
    *(["code-security"] * 5),
    *(["code-quality"] * 2),
    *(["secret-protection"] * 2),
    "supply-chain",
    "governance",
)
LESSON_DIR_RE = re.compile(
    rf"^(?P<number>\d{{2}})-"
    rf"(?P<pillar>{'|'.join(map(re.escape, RECOGNIZED_PILLARS))})-"
    r"(?P<lesson>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)

REQUIRED_SECTIONS: list[tuple[str, ...]] = [
    ("Goal",),
    ("Learning objectives",),
    ("Estimated time",),
    ("Prerequisites",),
    ("Hands-on steps", "Walkthrough", "Step-by-step navigation"),
    ("Exit criteria",),
    ("Key takeaways",),
    ("Discussion questions", "Discussion prompts"),
]


def _h2_headings(readme: Path) -> list[str]:
    return [
        line[3:].strip()
        for line in readme.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ")
    ]


def test_lesson_directories_match_ordered_pillar_map(lesson_dirs):
    names = [directory.name for directory in lesson_dirs]
    assert names == list(EXPECTED_LESSON_NAMES), (
        "Lesson directories must exactly match the ordered NN-pillar-lesson map; "
        f"got {names}"
    )

    parsed = []
    for expected_number, name in enumerate(names, start=1):
        match = LESSON_DIR_RE.fullmatch(name)
        assert match, f"{name!r} does not match NN-recognized-pillar-non-empty-lesson"
        parsed.append(match.groupdict())
        assert int(match["number"]) == expected_number, (
            f"{name!r} has number {match['number']}, expected {expected_number:02d}"
        )

    assert tuple(item["pillar"] for item in parsed) == EXPECTED_PILLAR_ORDER
    assert all(item["lesson"] for item in parsed)


@pytest.mark.parametrize("lesson_name", EXPECTED_LESSON_NAMES)
def test_lesson_has_readme(lessons_dir, lesson_name):
    readme = lessons_dir / lesson_name / "README.md"
    assert readme.is_file(), f"{readme} missing"


@pytest.mark.parametrize("lesson_name", EXPECTED_LESSON_NAMES)
def test_lesson_readme_title_matches_prefix(lessons_dir, lesson_name):
    prefix = lesson_name[:2]
    readme = lessons_dir / lesson_name / "README.md"
    first_line = readme.read_text(encoding="utf-8").splitlines()[0].strip()
    m = re.match(r"^#\s+Lesson\s+(\d{1,2})\b", first_line)
    assert m, f"{readme}: first line should be '# Lesson NN ...', got: {first_line!r}"
    assert int(m.group(1)) == int(prefix), (
        f"{readme}: lesson number in title ({m.group(1)}) does not match dir prefix ({prefix})"
    )


@pytest.mark.parametrize("lesson_name", EXPECTED_LESSON_NAMES)
def test_lesson_readme_has_required_sections(lessons_dir, lesson_name):
    readme = lessons_dir / lesson_name / "README.md"
    headings = set(_h2_headings(readme))
    missing = [
        " or ".join(group)
        for group in REQUIRED_SECTIONS
        if not any(h in headings for h in group)
    ]
    assert not missing, f"{readme} missing required H2 section(s): {missing}"


@pytest.mark.parametrize("lesson_name", EXPECTED_LESSON_NAMES)
def test_lesson_readme_non_empty(lessons_dir, lesson_name):
    readme = lessons_dir / lesson_name / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert len(text) > 500, f"{readme} suspiciously short ({len(text)} chars)"


def test_root_readme_lessons_table_lists_all_eleven(repo_root):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    refs = re.findall(r"`lessons/(\d{2}-[a-z0-9-]+)/`", readme)
    assert refs == list(EXPECTED_LESSON_NAMES), (
        "Root README lessons table should reference the exact ordered pillar map "
        f"once each; got {refs}"
    )
