"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Bandit detects every issue here.
"""

# ⚠️ B105 — hardcoded password string.
ADMIN_PASSWORD = "hunter2_FAKE_DEMO_PASSWORD"


def admin_only(role: str, password: str) -> None:
    # ⚠️ B101 — `assert` is stripped by `python -O` and is the wrong tool for auth.
    assert role == "admin", "Not authorized"
    assert password == ADMIN_PASSWORD, "Wrong password"


def login(user: str, password: str = "hunter2_FAKE_DEMO_PASSWORD") -> bool:
    # ⚠️ B107 — hardcoded password as a default argument.
    return user == "admin" and password == ADMIN_PASSWORD


def start_debug_app() -> None:
    # ⚠️ B201 — Flask debug=True enables the Werkzeug debugger (RCE in prod).
    try:
        from flask import Flask
    except ImportError:
        return
    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return "hello"

    app.run(debug=True)
