"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is documented as fake by AWS/Stripe/GitHub or is clearly marked FAKE/EXAMPLE/DEMO.
Do not reuse in production.
"""

# Fake match for the custom pattern "TKL Workshop Demo Key".
# Format: tkl_demo_[a-z0-9]{32}  — see .github/secret_scanning.yml.
# This value is workshop-only and matches no real service.
WORKSHOP_KEY = "tkl_demo_abcdef0123456789abcdef0123456789"


def use_workshop_key() -> dict:
    """Pretend to use the workshop key.

    ⚠️ Custom patterns let GHAS detect *your* org's token formats. Even though
    no partner knows about `tkl_demo_…`, GHAS will flag it because we taught
    it the format in `.github/secret_scanning.yml`.
    """
    return {
        "ok": False,
        "error": "demo only — workshop key is fake",
        "key_prefix": WORKSHOP_KEY[:9],
    }
