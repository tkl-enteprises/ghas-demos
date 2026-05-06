"""
Per-lesson README sanity:

  - 9 lessons exist (01..09), no gaps.
  - Each lesson dir name matches `NN-slug` and has a README.md.
  - README starts with `# Lesson NN` (number matches dir prefix).
  - Each README contains the standardized H2 sections.
  - Older lessons use `## Hands-on steps`; lesson 09 uses `## Walkthrough` —
    the test accepts either spelling for the "steps" heading.
  - Same for `## Discussion questions` vs `## Discussion prompts`.
  - README is non-empty (>500 chars) so we don't ship blank scaffolds.
  - Root README's lessons table contains exactly 9 rows referring to all 9
    lesson folders.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


EXPECTED_LESSON_PREFIXES = [f"{n:02d}" for n in range(1, 10)]

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


def test_nine_lessons_exist(lesson_dirs):
    prefixes = [d.name[:2] for d in lesson_dirs]
    assert prefixes == EXPECTED_LESSON_PREFIXES, (
        f"Expected lessons 01..09 with no gaps; got {prefixes}"
    )


@pytest.mark.parametrize("prefix", EXPECTED_LESSON_PREFIXES)
def test_lesson_has_readme(lessons_dir, prefix):
    matches = list(lessons_dir.glob(f"{prefix}-*"))
    assert len(matches) == 1, f"Expected exactly one lesson dir for prefix {prefix}"
    readme = matches[0] / "README.md"
    assert readme.is_file(), f"{readme} missing"


@pytest.mark.parametrize("prefix", EXPECTED_LESSON_PREFIXES)
def test_lesson_readme_title_matches_prefix(lessons_dir, prefix):
    readme = next(lessons_dir.glob(f"{prefix}-*")) / "README.md"
    first_line = readme.read_text(encoding="utf-8").splitlines()[0].strip()
    m = re.match(r"^#\s+Lesson\s+(\d{1,2})\b", first_line)
    assert m, f"{readme}: first line should be '# Lesson NN ...', got: {first_line!r}"
    assert int(m.group(1)) == int(prefix), (
        f"{readme}: lesson number in title ({m.group(1)}) does not match dir prefix ({prefix})"
    )


@pytest.mark.parametrize("prefix", EXPECTED_LESSON_PREFIXES)
def test_lesson_readme_has_required_sections(lessons_dir, prefix):
    readme = next(lessons_dir.glob(f"{prefix}-*")) / "README.md"
    headings = set(_h2_headings(readme))
    missing = [
        " or ".join(group)
        for group in REQUIRED_SECTIONS
        if not any(h in headings for h in group)
    ]
    assert not missing, f"{readme} missing required H2 section(s): {missing}"


@pytest.mark.parametrize("prefix", EXPECTED_LESSON_PREFIXES)
def test_lesson_readme_non_empty(lessons_dir, prefix):
    readme = next(lessons_dir.glob(f"{prefix}-*")) / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert len(text) > 500, f"{readme} suspiciously short ({len(text)} chars)"


def test_root_readme_lessons_table_lists_all_nine(repo_root):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    refs = re.findall(r"`lessons/(\d{2})-[a-z0-9-]+/`", readme)
    unique = sorted(set(refs))
    assert unique == EXPECTED_LESSON_PREFIXES, (
        f"Root README lessons table should reference lessons 01..09 exactly once each; got {unique}"
    )
