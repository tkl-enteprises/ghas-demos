"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production.
"""

DEBUG = True  # ⚠️ The custom query `py/tkl/hardcoded-debug-true` should flag this line.

def render_error(exc: Exception) -> str:
    if DEBUG:
        return f"<pre>{exc!r}</pre>"
    return "An error occurred."
