# Lesson 01 — Manual Remediation

Each section below maps to one vulnerability in `vulnerable_app.py` / `user_routes.py`. The Python snippets show the canonical fix that silences the corresponding CodeQL rule **and** is correct in production code.

## 1. `py/sql-injection` — parameterised queries

**Bad** (`vulnerable_app.py::lookup_user`, `user_routes.py::search_users`, `list_user_orders`):

```python
query = "SELECT id, email FROM users WHERE username = '" + username + "'"
cursor.execute(query)
```

**Good** — let the driver bind the parameter; never interpolate user input into SQL:

```python
cursor.execute(
    "SELECT id, email FROM users WHERE username = ?",
    (username,),
)
```

For the `LIKE` case, escape `%`/`_` if you accept them from users, then bind:

```python
cursor.execute(
    "SELECT id, username, email FROM users WHERE username LIKE ?",
    (f"%{q}%",),
)
```

For `user_id` (numeric) cast first, then bind:

```python
cursor.execute(
    "SELECT id, total FROM orders WHERE user_id = ?",
    (int(user_id),),
)
```

## 2. `py/command-line-injection` — argv list + `shlex.quote`

**Bad** (`ping_host`):

```python
subprocess.run("ping -c 1 " + host, shell=True, ...)
```

**Good** — pass the args as a list (no shell), and validate the host:

```python
import ipaddress
import shlex
import subprocess

def ping_host(host: str) -> str:
    # If you must accept hostnames, validate aggressively.
    ipaddress.ip_address(host)  # raises ValueError on garbage
    result = subprocess.run(
        ["ping", "-c", "1", host],   # no shell=True
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout
```

If you genuinely need a shell, `shlex.quote(host)` makes the argument single-token safe — but the list form above is preferred.

## 3. `py/path-injection` — `pathlib` resolve + `is_relative_to`

**Bad** (`read_report`):

```python
path = os.path.join("reports", report_name)
with open(path) as f:
    ...
```

**Good** — resolve symlinks then assert containment:

```python
from pathlib import Path

REPORTS_DIR = Path("reports").resolve()

def read_report(report_name: str) -> str:
    candidate = (REPORTS_DIR / report_name).resolve()
    if not candidate.is_relative_to(REPORTS_DIR):
        raise PermissionError("path escapes the reports directory")
    return candidate.read_text(encoding="utf-8")
```

## 4. `py/code-injection` — `ast.literal_eval`

**Bad** (`evaluate_expression`):

```python
return eval(expr)
```

**Good** — for arithmetic-only input use `ast.literal_eval`, which only parses Python literals; or use a real expression evaluator like `simpleeval`:

```python
import ast

def evaluate_expression(expr: str) -> object:
    return ast.literal_eval(expr)
```

`ast.literal_eval` raises on anything fancier than numbers, strings, tuples, lists, dicts, sets, booleans and `None` — exactly what you want.

## 5. `py/clear-text-logging-sensitive-data` — redact at the call site

**Bad** (`log_login_attempt`):

```python
log.info("Login attempt: user=%s password=%s", username, password)
```

**Good** — never log the password; log the outcome plus a non-sensitive identifier:

```python
def log_login_attempt(username: str, password: str, *, success: bool) -> None:
    log.info("Login attempt user=%s success=%s", username, success)
```

If you absolutely must log the secret for forensic reasons, hash it with a peppered KDF and store *that* — but in 99% of cases, just don't.

## 6. `py/weak-sensitive-data-hashing` — strong KDF, never raw MD5/SHA1

**Bad** (`hash_password`):

```python
return hashlib.md5(password.encode()).hexdigest()
```

**Good** — use a slow, salted password-hash KDF such as Argon2 or bcrypt:

```python
import bcrypt

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
```

If you only need a *content hash* (not a password hash), use SHA-256:

```python
hashlib.sha256(payload).hexdigest()
```

## 7. `py/hardcoded-credentials` — config / secrets store

**Bad**:

```python
ADMIN_PASSWORD = "insecure_pwd"
```

**Good** — load from environment / secret manager and compare with `secrets.compare_digest` to avoid timing attacks:

```python
import os
import secrets

ADMIN_PASSWORD_HASH = os.environ["ADMIN_PASSWORD_HASH"]  # bcrypt hash, not plaintext

def is_admin(submitted_password: str) -> bool:
    import bcrypt
    return bcrypt.checkpw(
        submitted_password.encode("utf-8"),
        ADMIN_PASSWORD_HASH.encode("utf-8"),
    )
```

For non-password constant-time comparisons (API keys, HMACs):

```python
secrets.compare_digest(submitted, expected)
```

## After you fix it

Re-push the branch. CodeQL re-runs and the alerts auto-close as **Fixed in branch**. That close event is the signal you want feeding into your team's metrics dashboard.
