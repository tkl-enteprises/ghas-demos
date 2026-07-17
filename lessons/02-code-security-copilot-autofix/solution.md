# Lesson 02 — Reference Solution

The manual fix you'd expect a careful reviewer to write — and the rough shape of what Copilot Autofix should suggest.

## What Autofix should produce

Autofix sees a `py/sql-injection` alert with a taint path from `username`/`password` (function parameters → tainted strings) into `cursor.execute(query)`. It should rewrite `authenticate` to use parameter binding:

```python
def authenticate(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE username = ? AND password = ?",
            (username, password),
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()
```

Key properties of the patch:

1. The two `+` concatenations are gone — every user-supplied value is now a bound parameter.
2. The SQL string is a constant — easy to grep, easy to audit.
3. The function signature and return type are unchanged — callers don't break.
4. The SQLite driver does the quoting, so the alert auto-closes on the next CodeQL run.

## How to evaluate Autofix's actual suggestion

When the workshop run produces a real Autofix patch, walk through this checklist:

- [ ] Did it convert **both** `username` and `password` to bound parameters? (A patch that fixes only one is half a fix.)
- [ ] Did it preserve `fetchone() is not None` semantics, or did it accidentally switch to `fetchall()`?
- [ ] Is `conn.close()` (or the `try/finally`) still present?
- [ ] Did it touch only `authenticate`, or did it modify the `__main__` block too?
- [ ] Does the rationale text mention CWE-89 / SQL injection / parameterised queries — i.e. is it reasoning about the *security* property, not just style?

## Review the draft PR

| Situation | Action |
| --- | --- |
| Patch matches the reference above (modulo whitespace). | Run the checks, request review, and move the draft PR through the normal approval process. |
| Patch is correct but uses different identifiers / formatting than the rest of the file. | Edit the draft PR, or ask Copilot to iterate if it came from an agentic session. |
| Patch does something surprising — e.g. introduces an ORM, changes the schema, or only fixes one of the two parameters. | Close or replace the draft PR and apply the manual fix. Do not dismiss the valid alert. |

## What to *not* do

- ❌ Hash the password client-side and concatenate the hash into the query — still vulnerable, just slightly weirder.
- ❌ Reach for `.format()` / f-strings instead of `+` — both are still concatenation as far as CodeQL is concerned, and both are still exploitable.
- ❌ Wrap user input in `repr(...)` or strip quotes — DIY escaping is how this class of bug stays alive for decades. Always let the driver bind.

## Going deeper

Production-grade login flows do more than parameterise SQL — they store **bcrypt/argon2** hashes (never plaintext passwords), rate-limit attempts, and use `secrets.compare_digest` for the final check. Lesson 01's `solution.md` walks through the password-hashing fix in detail.
