"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is clearly marked FAKE/DEMO so secret scanning detects the shape without exposing a real credential.
Do not reuse in production.
"""

# Fake match for the custom pattern "Contoso Workshop Demo Key".
# Format: contoso_demo_[a-z0-9]{32}
# The pattern is published in repo Settings → Code security → Secret scanning →
# Custom patterns. See lesson README for the facilitator preflight that
# configures it. This value is workshop-only and matches no real service.
WORKSHOP_KEY = "contoso_demo_abcdef0123456789abcdef0123456789"


def use_workshop_key() -> dict:
    """Pretend to use the workshop key.

    ⚠️ Custom patterns let GHAS detect *your* org's token formats. Even though
    no partner knows about `contoso_demo_…`, GHAS will flag it once the
    pattern is published in repo Settings → Code security → Secret scanning →
    Custom patterns. See the lesson README for the facilitator preflight.
    """
    return {
        "ok": False,
        "error": "demo only — workshop key is fake",
        "key_prefix": WORKSHOP_KEY[:13],
    }
