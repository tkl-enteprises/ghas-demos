"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is documented as fake by AWS/Stripe/GitHub or is clearly marked FAKE/EXAMPLE/DEMO.
Do not reuse in production.
"""

# ⚠️ FAKE GitHub PAT — has the right ghp_ prefix and 40-char body so GHAS will
# match the "GitHub Personal Access Token" partner pattern, but the body is
# literally the word FAKE repeated. Validity check will mark it inactive.
GITHUB_TOKEN = "ghp_FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE0"


def list_my_repos() -> list[dict]:
    """Pretend to call the GitHub API.

    ⚠️ Hard-coding a PAT in source is the anti-pattern. In a real app:
      - Use a GitHub App (installation token, short-lived, scoped).
      - Or, in CI, use the auto-injected GITHUB_TOKEN (also short-lived).
      - Or, for cross-repo workflows, use a fine-grained PAT stored in a
        GitHub Actions / Codespaces secret, never in code.
    """
    return [
        {
            "ok": False,
            "error": "demo only — token is fake",
            "token_prefix": GITHUB_TOKEN[:8],
        }
    ]
