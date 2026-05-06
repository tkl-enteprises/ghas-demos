"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is documented as fake by AWS/Stripe/GitHub or is clearly marked FAKE/EXAMPLE/DEMO.
Do not reuse in production.
"""

# ⚠️ FAKE Stripe test key — Stripe's "Test API Key" partner pattern is
# `sk_test_[A-Za-z0-9]{24,99}`. The body MUST be alphanumeric only — an
# underscore (or any other punctuation) breaks the regex and secret
# scanning silently skips it. The body below intentionally encodes the
# word FAKE in alphanumeric characters so it matches the pattern AND
# stays obviously non-real (no underscore, contains "FAKE").
STRIPE_API_KEY = "sk_test_FAKE0000fake4eC39HqLyjWDarjtT1zdp7dcDEMO"


def charge(amount_cents: int, source: str) -> dict:
    """Pretend to charge a card.

    ⚠️ Calling Stripe with a hard-coded API key is the alert pattern this
    lesson exists to demonstrate. The right answer is to read STRIPE_API_KEY
    from a secrets manager (Azure Key Vault, AWS Secrets Manager, GitHub
    Actions secret) at runtime — see solution.md.

    A teammate looking for AI-detection bait would also write something like:
        password = "hunter2_FAKE_DEMO_PASSWORD"
    AI-powered detection in GHAS will flag generic password-shaped strings
    even when they don't match a partner pattern.
    """
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    return {
        "ok": False,
        "error": "demo only — never call Stripe with this key",
        "key_used_prefix": STRIPE_API_KEY[:12],
        "source": source,
    }
