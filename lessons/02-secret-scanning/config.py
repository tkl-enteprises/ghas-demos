"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is documented as fake by AWS/Stripe/GitHub or is clearly marked FAKE/EXAMPLE/DEMO.
Do not reuse in production.
"""

# ⚠️ AWS DOCS CANARY — these are documented fake credentials from AWS docs.
# Secret scanning will detect them but they cannot be used.
# Reference: https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

REGION = "eu-west-1"


def get_credentials() -> tuple[str, str]:
    """Return the hard-coded credentials.

    ⚠️ This is exactly the anti-pattern secret scanning is designed to catch.
    The right answer is to read from the environment, an instance role, or
    GitHub Actions OIDC federation — see solution.md.
    """
    return AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
