"""
This file is the negative control: DEBUG is set from the environment, so the
custom CodeQL query should NOT flag it. Useful to verify query precision.
"""
import os

DEBUG = bool(os.environ.get("DEBUG"))

def render_error(exc: Exception) -> str:
    if DEBUG:
        return f"<pre>{exc!r}</pre>"
    return "An error occurred."
