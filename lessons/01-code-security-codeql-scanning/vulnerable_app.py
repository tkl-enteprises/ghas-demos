"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Every issue here is detected by GHAS.
"""

import hashlib
import logging
import os
import sqlite3
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. SQL injection — CodeQL: py/sql-injection (CWE-89)
# ---------------------------------------------------------------------------
def lookup_user(username: str) -> list:
    """Look up a user by name. The query is built by string concatenation,
    so a username like `' OR 1=1 --` returns every row."""
    conn = sqlite3.connect("workshop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users WHERE username = ?", (username,))
    return cursor.fetchall()


# ---------------------------------------------------------------------------
# 2. Command injection — CodeQL: py/command-line-injection (CWE-78)
# ---------------------------------------------------------------------------
def ping_host(host: str) -> str:
    """Ping a host. `shell=True` plus user-controlled string lets an attacker
    chain commands with `; rm -rf ~`."""
    result = subprocess.run(
        "ping -c 1 " + host,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


# ---------------------------------------------------------------------------
# 3. Path traversal — CodeQL: py/path-injection (CWE-22)
# ---------------------------------------------------------------------------
def read_report(report_name: str) -> str:
    """Read a report file. A `report_name` of `../../etc/passwd` escapes the
    intended `reports/` directory."""
    path = os.path.join("reports", report_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 4. Code injection — CodeQL: py/code-injection (CWE-94)
# ---------------------------------------------------------------------------
def evaluate_expression(expr: str) -> object:
    """Evaluate an arithmetic expression for the user. `eval` will happily
    run `__import__('os').system('id')` instead."""
    return eval(expr)  # noqa: S307


# ---------------------------------------------------------------------------
# 5. Clear-text logging of sensitive data — CodeQL:
#    py/clear-text-logging-sensitive-data (CWE-312)
# ---------------------------------------------------------------------------
def log_login_attempt(username: str, password: str) -> None:
    """Logs the password in plaintext — anyone with log access wins."""
    log.info("Login attempt: user=%s password=%s", username, password)


# ---------------------------------------------------------------------------
# 6. Weak hashing of sensitive data — CodeQL:
#    py/weak-sensitive-data-hashing (CWE-327)
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """MD5 is broken for password hashing — use a slow KDF (bcrypt, argon2,
    scrypt) with a per-user salt instead."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 7. Hard-coded credentials — CodeQL: py/hardcoded-credentials (CWE-798)
# ---------------------------------------------------------------------------
ADMIN_PASSWORD = "insecure_pwd"


def is_admin(submitted_password: str) -> bool:
    return submitted_password == ADMIN_PASSWORD


# ---------------------------------------------------------------------------
# Entry point used during the workshop demo. Do NOT run against real data.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vulnerable_app.py <untrusted-input>")
        sys.exit(1)

    user_input = sys.argv[1]
    print(lookup_user(user_input))
    print(ping_host(user_input))
    print(read_report(user_input))
    print(evaluate_expression(user_input))
