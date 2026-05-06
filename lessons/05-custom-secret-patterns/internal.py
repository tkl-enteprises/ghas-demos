"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is documented as fake by AWS/Stripe/GitHub or is clearly marked FAKE/EXAMPLE/DEMO.
Do not reuse in production.
"""

# Fake match for the custom pattern "TKL Internal Token".
# Format: TKL-INTERNAL-[A-Z0-9]{12,16}
# The pattern is published in repo Settings → Code security → Secret scanning →
# Custom patterns. See lesson README for the facilitator preflight that
# configures it. This value is workshop-only and matches no real service.
INTERNAL_API_TOKEN = "TKL-INTERNAL-DEMO123ABC456"


def call_internal_service(payload: dict) -> dict:
    """Pretend to call an internal API.

    ⚠️ Hard-coding the bearer token in source is the alert pattern this
    lesson exists to demonstrate. The right answer is to read it from a
    runtime secrets store and rotate it on a schedule.
    """
    return {
        "ok": False,
        "error": "demo only — TKL-INTERNAL token is fake",
        "token_prefix": INTERNAL_API_TOKEN[:13],
        "payload_keys": sorted(payload.keys()),
    }
