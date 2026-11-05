"""Regression guards for intentionally vulnerable and quality demo fixtures."""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest


DEPENDABOT_PINS = (
    "Flask==0.12.0",
    "Jinja2==2.10",
    "Werkzeug==0.14",
    "urllib3==1.24.1",
    "requests==2.19.1",
    "PyYAML==5.1",
    "cryptography==2.3",
)

# Known-malicious pin (GHSA-3pmj-h39m-cfpm) behind lesson 10's malware alert.
# PyPI no longer serves the project; the test below keeps the fixture inert.
MALWARE_PIN = "requestsa==2.28.1"

QUALITY_RULE_IDS = {
    "js/template-syntax-in-string-literal",
    "js/useless-assignment-to-local",
}


def _lesson(repo_root: Path, name: str) -> Path:
    return repo_root / "lessons" / name


def _requirements_pins(path: Path) -> tuple[str, ...]:
    return tuple(
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def _section(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        markdown,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, f"Missing {heading!r} section"
    return match.group(1)


def _markdown_table(markdown: str, header: str) -> dict[str, list[str]]:
    lines = markdown.splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.startswith(f"| {header} ")),
        None,
    )
    assert header_index is not None, f"Missing markdown table headed by {header!r}"

    rows: dict[str, list[str]] = {}
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        rows[cells[0]] = cells[1:]
    return rows


def _route_protection(path: Path) -> dict[str, bool]:
    """Map each `@app.route` URL in a fixture to whether `@admin_required` guards it."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    routes = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        decorator_names = {d.id for d in node.decorator_list if isinstance(d, ast.Name)}
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "route"
            ):
                routes[decorator.args[0].value] = "admin_required" in decorator_names
    return routes


def test_lesson03_custom_query_and_controls_stay_aligned(repo_root: Path):
    lesson = _lesson(repo_root, "03-code-security-custom-codeql-queries")
    queries = repo_root / ".github" / "codeql" / "custom-queries"
    query = (queries / "UnprotectedAdminRoute.ql").read_text(encoding="utf-8")

    assert "@id py/tkl/unprotected-admin-route" in query
    assert '.getId() = "admin_required"' in query
    assert 'regexpMatch("/admin(/.*)?")' in query
    assert (queries / "UnprotectedAdminRoute.md").is_file(), "rule help for the alert page"

    assert _route_protection(lesson / "noncompliant.py") == {
        "/health": False,
        "/admin/audit-log": True,
        "/admin/users/export": False,
    }, (
        "noncompliant.py must keep exactly one unprotected /admin route for the custom "
        "query to report. If a demo PR added @admin_required there, close it unmerged "
        "or revert it."
    )
    assert _route_protection(lesson / "compliant.py") == {
        "/health": False,
        "/admin/audit-log": True,
        "/admin/users/export": True,
    }


def test_lesson10_manifests_match_all_intentional_pins(repo_root: Path):
    lesson = _lesson(repo_root, "10-supply-chain-dependabot")
    requirements = _requirements_pins(lesson / "requirements.txt")
    pyproject = tomllib.loads((lesson / "pyproject.toml").read_text(encoding="utf-8"))
    project_dependencies = tuple(pyproject["project"]["dependencies"])

    assert requirements == DEPENDABOT_PINS
    assert project_dependencies == DEPENDABOT_PINS
    assert requirements == project_dependencies


def test_lesson10_vulnerable_baseline_is_documented(repo_root: Path):
    lesson = _lesson(repo_root, "10-supply-chain-dependabot")
    readme = (lesson / "README.md").read_text(encoding="utf-8")
    solution = (lesson / "solution.md").read_text(encoding="utf-8")
    rows = _markdown_table(readme, "Package")

    assert rows["Werkzeug"][:4] == [
        "0.14",
        "GHSA-2g68-c3qc-8985",
        "High",
        "3.0.3",
    ]
    assert rows["cryptography"][:4] == [
        "2.3",
        "GHSA-hggm-jpg3-v476",
        "High",
        "3.2",
    ]

    documented_pins = set(
        re.findall(
            r"`([A-Za-z0-9_.-]+==[A-Za-z0-9_.+-]+)`",
            _section(solution, "Fixture integrity"),
        )
    )
    assert documented_pins == set(DEPENDABOT_PINS) | {MALWARE_PIN}


def test_lesson10_malware_fixture_stays_inert(repo_root: Path):
    malware_demo = _lesson(repo_root, "10-supply-chain-dependabot") / "malware-demo"
    files = sorted(path.name for path in malware_demo.iterdir() if not path.name.startswith("."))
    assert files == ["requirements.txt"], "malware-demo/ holds only the manifest: no lockfile or code"

    manifest = malware_demo / "requirements.txt"
    assert _requirements_pins(manifest) == (MALWARE_PIN,)
    assert re.search(r"\bnever install\b", manifest.read_text(encoding="utf-8"), re.IGNORECASE)

    automation = [
        *(repo_root / ".github" / "workflows").glob("*.yml"),
        repo_root / ".github" / "dependabot.yml",
        *(path for path in (repo_root / "scripts").iterdir() if path.is_file()),
    ]
    referencing = [
        str(path.relative_to(repo_root))
        for path in automation
        if "malware-demo" in path.read_text(encoding="utf-8")
    ]
    assert not referencing, (
        f"{referencing} reference the malware fixture. Nothing may install, lock, or "
        "update malware-demo/requirements.txt."
    )


def test_lesson10_safety_warnings_remain(repo_root: Path):
    lesson = _lesson(repo_root, "10-supply-chain-dependabot")
    readme = (lesson / "README.md").read_text(encoding="utf-8")
    requirements_intro = "\n".join(
        (lesson / "requirements.txt").read_text(encoding="utf-8").splitlines()[:2]
    )
    pyproject_intro = "\n".join(
        (lesson / "pyproject.toml").read_text(encoding="utf-8").splitlines()[:3]
    )
    app_intro = "\n".join(
        (lesson / "app.py").read_text(encoding="utf-8").splitlines()[:5]
    )
    readme_intro = readme.partition("## Goal")[0]
    fixture_guidance = _section(
        (lesson / "solution.md").read_text(encoding="utf-8"), "Fixture integrity"
    )

    for manifest_intro in (requirements_intro, pyproject_intro):
        assert "INTENTIONALLY VULNERABLE" in manifest_intro.upper()
    assert "INTENTIONALLY VULNERABLE" in app_intro.upper()
    assert re.search(r"\bdo not deploy\b", app_intro, flags=re.IGNORECASE)
    assert "intentionally vulnerable" in readme_intro.lower()
    assert re.search(r"\bdo not install\b", readme_intro, flags=re.IGNORECASE)
    assert re.search(r"\bnever install\b", fixture_guidance, flags=re.IGNORECASE)
    assert re.search(r"\bexecute `app\.py`", fixture_guidance, flags=re.IGNORECASE)


def test_lesson06_retains_quality_defects_and_solution(repo_root: Path):
    lesson = _lesson(repo_root, "06-code-quality-standard-findings")
    fixture = (lesson / "quality-fixtures.js").read_text(encoding="utf-8")
    readme = (lesson / "README.md").read_text(encoding="utf-8")
    solution = (lesson / "solution.md").read_text(encoding="utf-8")

    documented_rules = set(re.findall(r"\bjs/[a-z0-9-]+\b", readme))
    solution_rules = set(re.findall(r"\bjs/[a-z0-9-]+\b", solution))
    assert documented_rules == QUALITY_RULE_IDS
    assert solution_rules == QUALITY_RULE_IDS
    assert re.search(
        r"\[`js/template-syntax-in-string-literal`\]\([^)]+\)"
        r"\s*\|\s*Reliability\s*\|\s*Warning\s*\|\s*High\s*\|",
        readme,
    )
    assert re.search(
        r"\[`js/useless-assignment-to-local`\]\([^)]+\)"
        r"\s*\|\s*Maintainability\s*\|\s*Warning\s*\|\s*Very high\s*\|",
        readme,
    )

    assert re.search(r"`[^`]*\$\{userName\}[^`]*`", fixture)
    assert re.search(r'["\'][^"\']*\$\{userName\}[^"\']*["\']', fixture)
    assert re.search(
        r"let\s+completed\s*=\s*tasks\.length\s*;"
        r"\s*completed\s*=\s*tasks\.filter\(",
        fixture,
    )

    assert re.search(r"message:\s*`[^`]*\$\{userName\}[^`]*`", solution)
    assert re.search(r"const\s+completed\s*=\s*tasks\.filter\(", solution)
    assert re.search(r"\bdo\s+not\s+merge\b", solution, flags=re.IGNORECASE)


def test_lesson06_fixture_is_runnable_and_inert(repo_root: Path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is optional; static fixture checks still ran")

    fixture = _lesson(repo_root, "06-code-quality-standard-findings") / "quality-fixtures.js"
    harness = r"""
const assert = require("node:assert/strict");
const Module = require("node:module");

const fixturePath = process.argv[1];
const originalLoad = Module._load;
Module._load = function (request, parent, isMain) {
  if (request === fixturePath) {
    return originalLoad.call(this, request, parent, isMain);
  }
  throw new Error(`Fixture imported unexpected module: ${request}`);
};

for (const name of ["fetch", "setInterval", "setTimeout"]) {
  globalThis[name] = () => {
    throw new Error(`Fixture invoked ${name}`);
  };
}
for (const name of ["debug", "error", "info", "log", "warn"]) {
  console[name] = () => {
    throw new Error(`Fixture wrote to console.${name}`);
  };
}

const fixtures = require(fixturePath);
assert.deepEqual(Object.keys(fixtures).sort(), ["buildGreeting", "countCompleted"]);
assert.deepEqual(fixtures.buildGreeting("Ada"), {
  preview: "Preview for Ada",
  message: "Welcome, ${userName}!",
});
assert.equal(
  fixtures.countCompleted([{ complete: true }, { complete: false }]),
  1,
);
"""
    result = subprocess.run(
        [node, "--check", str(fixture)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr

    result = subprocess.run(
        [node, "-e", harness, str(fixture.resolve())],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_lesson07_ai_findings_fixture_is_contextual_and_inert(repo_root: Path):
    lesson = _lesson(repo_root, "07-code-quality-ai-findings")
    fixture = lesson / "ai-findings-fixtures.js"
    text = fixture.read_text(encoding="utf-8")
    readme = (lesson / "README.md").read_text(encoding="utf-8")

    assert re.search(r"let\s+selectedWorkshop\s*=\s*workshops\[0\]", text)
    assert "registration were succesfully saved" in text
    assert re.search(r"attendees\.sort\(", text)
    assert re.search(r"attendee\.name\s*=", text)
    assert re.search(r"for\s*\([^)]*workshopId[^)]*\)\s*\{[^}]*await", text, re.DOTALL)
    assert "At least one pull request is merged after Code Quality was enabled" in readme

    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is optional; static AI fixture checks still ran")

    harness = r"""
const assert = require("node:assert/strict");
const Module = require("node:module");

const fixturePath = process.argv[1];
const originalLoad = Module._load;
Module._load = function (request, parent, isMain) {
  if (request === fixturePath) {
    return originalLoad.call(this, request, parent, isMain);
  }
  throw new Error(`Fixture imported unexpected module: ${request}`);
};

for (const name of ["fetch", "setInterval", "setTimeout"]) {
  globalThis[name] = () => {
    throw new Error(`Fixture invoked ${name}`);
  };
}
for (const name of ["debug", "error", "info", "log", "warn"]) {
  console[name] = () => {
    throw new Error(`Fixture wrote to console.${name}`);
  };
}

const fixtures = require(fixturePath);
    assert.deepEqual(Object.keys(fixtures).sort(), [
      "buildRegistrationMessage",
      "findWorkshopById",
      "loadWorkshopDetails",
      "normalizeAttendees",
    ]);
    assert.equal(
      fixtures.buildRegistrationMessage("Ada"),
      "Ada, your registration were succesfully saved.",
    );

const workshops = [{ id: "first" }, { id: "second" }];
assert.equal(fixtures.findWorkshopById(workshops, "missing"), workshops[0]);

const attendees = [
  { name: "  Zoe", email: "ZOE@EXAMPLE.COM " },
  { name: " Ada ", email: " ADA@EXAMPLE.COM" },
];
    assert.equal(fixtures.normalizeAttendees(attendees), attendees);
    assert.deepEqual(attendees, [
      { name: "Zoe", email: "zoe@example.com" },
      { name: "Ada", email: "ada@example.com" },
    ]);

let active = 0;
let maximumActive = 0;
async function fetchWorkshop(id) {
  active += 1;
  maximumActive = Math.max(maximumActive, active);
  await Promise.resolve();
  active -= 1;
  return { id };
}

(async () => {
  assert.deepEqual(
    await fixtures.loadWorkshopDetails(["first", "second"], fetchWorkshop),
    [{ id: "first" }, { id: "second" }],
  );
  assert.equal(maximumActive, 1);
})().catch((error) => {
  process.stderr.write(`${error.stack}\n`);
  process.exitCode = 1;
});
"""
    result = subprocess.run(
        [node, "--check", str(fixture)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr

    result = subprocess.run(
        [node, "-e", harness, str(fixture.resolve())],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_security_fixtures_cannot_activate_accidentally(repo_root: Path):
    actions_fixtures = _lesson(repo_root, "05-code-security-actions") / "fixtures"
    fixture_files = sorted(path.name for path in actions_fixtures.iterdir() if path.is_file())
    assert fixture_files == [
        "remediated-workflow.yml.txt",
        "vulnerable-workflow.yml.txt",
    ]

    workflow_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (repo_root / ".github" / "workflows").glob("*.yml")
    )
    assert "05-code-security-actions/fixtures" not in workflow_text


def test_lesson05_secret_exposure_demo_stays_disabled(repo_root: Path):
    workflow = (
        repo_root / ".github" / "workflows" / "lesson-05-vulnerable.yml"
    ).read_text(encoding="utf-8")

    assert re.search(r"^\s{4}if:\s*\$\{\{\s*false\s*\}\}\s*$", workflow, re.MULTILINE)
    assert "fromJSON(secrets.LESSON_05_CREDENTIALS).password" in workflow
    assert 'run: echo "${{ fromJSON(secrets.LESSON_05_CREDENTIALS).password }}"' in workflow


# ---------------------------------------------------------------------------
# Intentional vulnerabilities must survive live demos.
#
# Lessons 01, 02 and 04 end with "Generate fix" / "Assign to Copilot" PRs. If
# one of those PRs is merged, the next cohort silently loses an alert (this
# happened to lesson 01's `lookup_user` SQL injection in July 2026). These
# guards turn such a PR red with an explanation instead.
# ---------------------------------------------------------------------------

INTENTIONAL_SINKS = {
    "01-code-security-codeql-scanning/vulnerable_app.py": (
        "\"SELECT id, email FROM users WHERE username = '\" + username + \"'\"",
        "cursor.execute(query)",
        '"ping -c 1 " + host',
        "shell=True",
        'os.path.join("reports", report_name)',
        "return eval(expr)",
        'log.info("Login attempt: user=%s password=%s", username, password)',
        "hashlib.md5(",
        'ADMIN_PASSWORD = "',  # hard-coded literal; value deliberately not repeated here
    ),
    "01-code-security-codeql-scanning/user_routes.py": (
        "\"SELECT id, username, email FROM users WHERE username LIKE '%\" + q + \"%'\"",
        '"SELECT id, total FROM orders WHERE user_id = " + user_id',
    ),
    "02-code-security-copilot-autofix/insecure_login.py": (
        "\"WHERE username = '\" + username + \"' \"",
        "\"AND password = '\" + password + \"'\"",
        "cursor.execute(query)",
    ),
    "04-code-security-sarif-integration/subprocess_use.py": (
        'subprocess.check_output(f"ls -la {path}", shell=True)',
        'f"cat /etc/passwd | grep {user_filter}",\n        shell=True,',
        'subprocess.check_output(["ping", "-c", "1", target])',
    ),
    "04-code-security-sarif-integration/sql_format.py": (
        "\"SELECT * FROM users WHERE username = '%s'\" % username",
        "f\"SELECT id, total FROM orders WHERE status = '{status}'\"",
    ),
    "04-code-security-sarif-integration/eval_use.py": ("eval(expression)", "exec(code)"),
    "04-code-security-sarif-integration/unsafe_deserialize.py": (
        "pickle.loads(blob)",
        "pickle.load(fh)",
    ),
    "04-code-security-sarif-integration/weak_crypto.py": (
        "hashlib.md5(",
        "random.randint(0, 9)",
        "random.seed(seed)",
    ),
    "04-code-security-sarif-integration/assert_check.py": (
        'assert role == "admin"',
        'ADMIN_PASSWORD = "',  # literal values not repeated: avoid new AI-detected alerts
        'password: str = "',
        "app.run(debug=True)",
    ),
}


@pytest.mark.parametrize("relative_path", sorted(INTENTIONAL_SINKS))
def test_intentional_vulnerabilities_are_still_present(repo_root: Path, relative_path: str):
    text = (repo_root / "lessons" / relative_path).read_text(encoding="utf-8")
    missing = [snippet for snippet in INTENTIONAL_SINKS[relative_path] if snippet not in text]
    assert not missing, (
        f"lessons/{relative_path} no longer contains the intentional vulnerability "
        f"{missing}. A workshop fix (Copilot Autofix, Copilot cloud agent, or a manual "
        "solution.md change) appears to have been merged. That is expected inside a "
        "demo PR, but do not merge it: close the PR, or revert it so the next cohort "
        "still sees the alert."
    )


def test_lesson09_fixtures_match_their_custom_patterns(repo_root: Path):
    lesson = _lesson(repo_root, "09-secret-protection-custom-patterns")
    readme = (lesson / "README.md").read_text(encoding="utf-8")
    patterns = {
        "internal.py": r"CONTOSO-API-[A-Z0-9]{16,}",
        "demo_key.py": r"contoso_demo_[a-z0-9]{32}",
    }
    for filename, pattern in patterns.items():
        assert f"`{pattern}`" in readme, f"lesson 09 README should document `{pattern}`"
        text = (lesson / filename).read_text(encoding="utf-8")
        assert re.search(rf'"{pattern}"', text), (
            f"{filename} must keep a quoted value matching the custom pattern {pattern}"
        )


# ---------------------------------------------------------------------------
# Live push-protection demos must not leave real credentials behind.
# ---------------------------------------------------------------------------

SENSITIVE_ENV_KEY_RE = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PAT|CONNECTION_STRING)", re.I)
GITHUB_FINE_GRAINED_PAT_RE = re.compile(r"github_pat_[A-Za-z0-9_]{22,}")
GITHUB_CLASSIC_TOKEN_RE = re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")


def _tracked_text_files(repo_root: Path) -> list[Path]:
    git = shutil.which("git")
    if git is None or not (repo_root / ".git").exists():
        pytest.skip("git checkout required to enumerate tracked files")
    result = subprocess.run(
        [git, "ls-files", "-z"], cwd=repo_root, capture_output=True, check=True
    )
    paths = [repo_root / p for p in result.stdout.decode().split("\0") if p]
    return [p for p in paths if p.suffix not in {".png", ".jpg", ".gif"} and p.is_file()]


def test_env_example_keeps_placeholders_only(repo_root: Path):
    env_example = _lesson(repo_root, "08-secret-protection-secret-scanning") / ".env.example"
    filled = [
        line.split("=", 1)[0]
        for line in env_example.read_text(encoding="utf-8").splitlines()
        if "=" in line
        and not line.lstrip().startswith("#")
        and SENSITIVE_ENV_KEY_RE.search(line.split("=", 1)[0])
        and line.split("=", 1)[1].strip()
    ]
    assert not filled, (
        f".env.example must teach the placeholder pattern, but {filled} have values. "
        "A live push-protection demo probably committed a real token: revoke it, then "
        "blank the value."
    )


def test_no_env_files_are_tracked(repo_root: Path):
    tracked = [
        str(p.relative_to(repo_root))
        for p in _tracked_text_files(repo_root)
        if p.name == ".env" or (p.name.startswith(".env.") and p.name != ".env.example")
    ]
    assert not tracked, (
        f"{tracked} are tracked although .gitignore excludes them. They are usually "
        "left behind by a live push-protection bypass demo: revoke the token and "
        "delete the file."
    )


def test_no_real_github_tokens_are_committed(repo_root: Path):
    offenders = []
    for path in _tracked_text_files(repo_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if GITHUB_FINE_GRAINED_PAT_RE.search(text):
            offenders.append(f"{path.relative_to(repo_root)} (github_pat_…)")
        for token in GITHUB_CLASSIC_TOKEN_RE.findall(text):
            if "FAKE" not in token:
                offenders.append(f"{path.relative_to(repo_root)} ({token[:4]}…)")
    assert not offenders, (
        f"Real-looking GitHub tokens are committed: {offenders}. Workshop fixtures "
        "must contain FAKE markers; revoke any real token immediately."
    )
