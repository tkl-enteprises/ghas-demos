from __future__ import annotations

import subprocess

import yaml


def test_codeql_autofix_script_is_valid_bash(repo_root):
    script = repo_root / "scripts" / "codeql-autofix.sh"
    assert script.is_file()
    subprocess.run(["bash", "-n", str(script)], check=True)


def test_codeql_autofix_workflow_is_guarded(repo_root, workflows_dir):
    workflow_path = workflows_dir / "codeql-autofix.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    script = (repo_root / "scripts" / "codeql-autofix.sh").read_text(encoding="utf-8")

    assert workflow["permissions"] == {
        "actions": "write",
        "contents": "write",
        "pull-requests": "write",
        "security-events": "write",
    }
    assert workflow["jobs"]["create-draft-fixes"]["if"].count("workflow_run") >= 3
    assert "--draft" in script
    assert "autofix/commits" in script
    assert "gh pr merge" not in script
