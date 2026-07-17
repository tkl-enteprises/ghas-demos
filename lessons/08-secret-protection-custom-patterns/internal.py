"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is clearly marked FAKE/DEMO so secret scanning detects the shape without exposing a real credential.
Do not reuse in production.
"""

# Fake match for the custom pattern "Contoso API Token".
# Format: CONTOSO-API-[A-Z0-9]{16,}
# The pattern is published in repo Settings → Code security → Secret scanning →
# Custom patterns. See lesson README for the facilitator preflight that
# configures it. This value is workshop-only and matches no real service —
# `Contoso` is Microsoft's canonical fictitious-customer name, so the prefix
# is guaranteed not to collide with any real provider.
INTERNAL_API_TOKEN = "CONTOSO-API-FAKEDEMO0123456789ABCDEF"


def call_internal_service(payload: dict) -> dict:
    """Pretend to call an internal API.

    ⚠️ Hard-coding the bearer token in source is the alert pattern this
    lesson exists to demonstrate. The right answer is to read it from a
    runtime secrets store and rotate it on a schedule.
    """
    return {
        "ok": False,
        "error": "demo only — CONTOSO-API token is fake",
        "token_prefix": INTERNAL_API_TOKEN[:12],
        "payload_keys": sorted(payload.keys()),
    }
