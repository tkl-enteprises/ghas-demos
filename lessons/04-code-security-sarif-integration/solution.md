# Solution — SARIF / Bandit lesson

## How to fix each Bandit finding

| Rule | Vuln file | Fix |
|------|-----------|-----|
| **B101** — `assert` for auth | `assert_check.py` | `assert` is stripped under `python -O`. Use `if not condition: raise PermissionError(...)`. |
| **B105** — hardcoded password string | `assert_check.py` | Read from environment (`os.environ["ADMIN_PASSWORD"]`) or a secrets manager (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault). Never commit credentials — and rotate any value that ever touched git history. |
| **B107** — hardcoded password default arg | `assert_check.py` | Default to `None` and require the caller to supply a value: `def login(user, password=None): if password is None: raise ValueError(...)`. |
| **B201** — Flask `debug=True` | `assert_check.py` | Drive from env: `app.run(debug=os.environ.get("FLASK_DEBUG") == "1")`. Never `True` in production — the Werkzeug debugger is RCE-by-design. |
| **B301** — `pickle.loads` on untrusted data | `unsafe_deserialize.py` | Switch to `json.loads` for data, or `msgpack` / `cbor2` for binary. If you absolutely need pickle, sign the payload (HMAC) and verify before unpickling. |
| **B303** — `hashlib.md5` | `weak_crypto.py` | For passwords use `bcrypt`, `argon2-cffi`, or `passlib`. For integrity checksums use `hashlib.sha256`. (`hashlib.md5(..., usedforsecurity=False)` is acceptable for non-security uses on Python 3.9+.) |
| **B307** — `eval` / `exec` | `eval_use.py` | If you only need to parse a literal, use `ast.literal_eval`. Otherwise build a real parser or restrict to a whitelist. Never `eval` user input. |
| **B311** — `random` for security | `weak_crypto.py` | Use the `secrets` module: `secrets.token_hex(16)`, `secrets.token_urlsafe(32)`, `secrets.choice(...)`. |
| **B404 / B603 / B602** — `subprocess` | `subprocess_use.py` | Use `subprocess.run([...], shell=False, check=True)` with an argv **list**. Never interpolate user input into a shell string. Validate / allow-list the binary path. |
| **B608** — SQL string formatting | `sql_format.py` | Use parameterised queries: `cur.execute("SELECT * FROM users WHERE username = ?", (username,))` for SQLite, `%s` for psycopg, named params for SQLAlchemy. The driver does the escaping. |

## Multi-tool SAST strategy

CodeQL is excellent at deep dataflow analysis (taint tracking, cross-function reachability) but ships with a curated, conservative rule set focused on real exploits. Layer additional tools when their strengths complement it:

- **Add Bandit** for Python projects — catches the long tail of "obviously bad" idioms (MD5, pickle, asserts-as-auth) that CodeQL deprioritises to keep its SNR high.
- **Add Semgrep** when you want **custom org-specific rules** without learning QL. Great for "no one in this org is allowed to import `requests` without `verify=`" style policies.
- **Add Trivy / Grype** for **container images and dependencies** — neither CodeQL nor Bandit covers your `Dockerfile` or `requirements.txt` CVEs.
- **Add Checkov / KICS / tfsec** if you have **Terraform or Kubernetes manifests** — IaC misconfiguration is its own category.
- **Add gitleaks** as a belt-and-braces secret scanner alongside GHAS Secret Scanning, especially for commit history pre-dating GHAS adoption.

Rule of thumb: **one tool per coverage gap**, not three tools doing the same job. Stack vertically (depth: CodeQL + Bandit on Python source) and horizontally (breadth: + Trivy on containers + Checkov on IaC).

## De-duping findings

GHAS Code Scanning groups alerts by `(tool name, rule ID, location, partialFingerprint)` — **not** by source line alone. So a Bandit finding and a CodeQL finding on the same line of `eval_use.py` will appear as **two separate alerts**, even though they describe the same bug. Strategies:

1. **Pick one tool per rule family.** If CodeQL already covers `py/code-injection`, suppress Bandit's B307 in that path (e.g. `bandit -s B307` or a `# nosec` comment) — or vice versa. The lesson here uses `paths-ignore` in the CodeQL config to give Bandit exclusive ownership of `lessons/04-code-security-sarif-integration/`.
2. **Use distinct `category:` values** when uploading SARIF (this lesson's workflow uses `category: bandit`). That keeps the two tools' results in separate result sets so re-uploading one doesn't wipe the other.
3. **Triage in bulk** by tool: filter Code Scanning to `tool:bandit`, dismiss anything covered by another scanner with reason "won't fix → covered by CodeQL". Document the policy in `SECURITY.md` so future maintainers don't re-enable both.
4. **Stable `partialFingerprints`** matter: if the tool emits unstable fingerprints, every push creates a new alert and dismissals don't stick. Bandit ≥ 1.7.5 emits good fingerprints out of the box.

The goal is **one alert per real bug**, not one alert per tool that noticed it.
