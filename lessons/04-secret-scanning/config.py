"""
⚠️ INTENTIONALLY VULNERABLE — fake/canary credentials only, for educational use.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Every "secret" in this file is clearly marked FAKE/DEMO so secret scanning
detects the *shape* without exposing a real credential.
Do not reuse in production.
"""

# ⚠️ FAKE Azure Storage connection string — the partner pattern matches
# `AccountKey=<88-char base64>` inside a connection string. The body below
# is exactly the Azure shape (DefaultEndpointsProtocol / AccountName /
# AccountKey / EndpointSuffix) but every visible character spells `FAKEDEMO`,
# so secret scanning fires on the pattern while a human reader can see at
# a glance that no real key is committed. Validity probing will mark it
# inactive — by design.
AZURE_STORAGE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;"
    "AccountName=fakedemoaccount;"
    "AccountKey=FAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDE==;"
    "AccountKey2=FAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDEMOFAKEDE==;"
    "EndpointSuffix=core.windows.net"
)

REGION = "westeurope"


def get_credentials() -> tuple[str, str]:
    """Return the hard-coded credentials.

    ⚠️ This is exactly the anti-pattern secret scanning is designed to catch.
    The right answer is to read from the environment, a managed identity, or
    GitHub Actions OIDC federation to Azure — see solution.md.
    """
    return AZURE_STORAGE_CONNECTION_STRING, REGION
