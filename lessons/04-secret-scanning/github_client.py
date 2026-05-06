"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is clearly marked FAKE/DEMO so secret scanning detects the shape without exposing a real credential.
Do not reuse in production.
"""

# ⚠️ FAKE GitHub PAT — the partner pattern is `ghp_[A-Za-z0-9]{36}`
# (exactly 36 alphanumeric chars, no underscores). The body below is
# 36 chars: `FAKE` × 9 = 36, so the full string is `ghp_` + 36 = 40 chars,
# matches the pattern, and is obviously non-real. Validity checks will
# mark it inactive.
GITHUB_TOKEN = "ghp_FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE"


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
