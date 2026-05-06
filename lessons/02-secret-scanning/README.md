# Lesson 02 — Secret Scanning + Push Protection

See GitHub Advanced Security detect hard-coded credentials in source, block new ones at `git push`, and validate live tokens with partner providers.

## Goal

Experience secret scanning and push protection end-to-end: spot existing alerts in the security tab, then try to push a new "secret" and watch GitHub stop you before it ever lands on the remote.

## What's in this lesson

Four Python files plus a `.env.example`. Each Python file deliberately hard-codes a different *fake* / canary credential so that GHAS has something to flag — but every value is documented as fake by its issuer (AWS, Stripe, GitHub) or clearly marked `FAKE` / `EXAMPLE` / `DEMO`.

| File | Pattern triggered |
| --- | --- |
| `config.py` | `AWS Access Key ID` + `AWS Secret Access Key` (AWS-documented canaries) |
| `payment.py` | `Stripe API Key` (test key, marked `FAKE`) |
| `github_client.py` | `GitHub Personal Access Token` (`ghp_` prefix, FAKE body) |
| `.env.example` | **Nothing** — placeholders, no values. This teaches the right pattern. |

> ⚠️ Every file (except `.env.example`) starts with a "this is intentionally vulnerable" header. Do not copy these patterns into real code.

## Push protection demo

Push protection runs **client-side at `git push` time** — GitHub refuses the push before the secret is written to the remote. Try it:

1. Clone the repo locally.
   ```bash
   git clone https://github.com/tkl-enteprises/ghas-demos.git
   cd ghas-demos
   ```
2. Edit `lessons/02-secret-scanning/payment.py` and add a new line that *looks* like a real AWS Access Key ID — anything matching the pattern `AKIA[A-Z0-9]{16}` will do. For example:
   ```python
   NEW_AWS_KEY = "AKIA" + "EXAMPLE" + "PUSHBLOCK1"  # 20 chars total
   ```
3. Commit and try to push:
   ```bash
   git add lessons/02-secret-scanning/payment.py
   git commit -m "test push protection"
   git push
   ```
4. Observe push protection block the push with a remote rejection that links to the offending file/line and includes a bypass URL. See https://docs.github.com/en/code-security/secret-scanning/working-with-push-protection for the full workflow.
5. **Bypass workflow** (only if you genuinely need to land a documented test value, e.g. a test fixture):
   ```bash
   git push -o secret-scanning.skip-push-protection=true
   ```
   Each bypass requires a reason and is audited. In a real workflow, prefer "this is a false positive" via the UI so security can refine the pattern, or "used in tests" with a proper test fixture marker — and **never** "I'll rotate it later".

## Validity checks

For partners that support it (AWS, GitHub, Slack, …) GHAS pings the issuer's API to check whether the leaked token is currently valid. The alerts in the security tab will be tagged `Active` or `Inactive`. The canary credentials in this lesson should all show as **inactive / unknown** — they were never live, by design. In a real leak, an `Active` tag means "rotate, *now*".

## AI detection

With AI-powered detection enabled at the org level, GHAS will also surface generic-looking secrets (passwords, tokens) that don't match any partner pattern. It uses an LLM to classify suspicious string assignments. In this lesson, the `password = "hunter2_FAKE_DEMO_PASSWORD"` pattern in `payment.py`'s comments is the kind of thing AI detection would flag (we don't actually hard-code that variable to keep partner detections clean).

## Where to look in GitHub

- Repo alerts: <https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning>
- Push protection bypasses (audit log): org → Settings → Audit log → search for `secret_scanning_push_protection`.

## Hands-on steps

1. Open the repo's **Security → Secret scanning alerts** tab.
2. Confirm at least three alerts are present: AWS Access Key ID, Stripe test key (or generic API key), GitHub PAT.
3. Click into the AWS alert. Note: the file path, the line number, the validity badge, and the recommended remediation.
4. Clone the repo, follow the *Push protection demo* steps above to get a hard rejection.
5. Bypass the rejection with `-o secret-scanning.skip-push-protection=true`, then immediately revert/force-push to clean up your branch (so we don't leave canaries scattered around).
6. Open `solution.md` and walk through the remediation runbook.

## Discussion prompts

1. A teammate accidentally committed a **production** AWS access key 30 minutes ago. Walk through your incident response — what's step 1, step 2, step 3?
2. When is bypassing push protection the right call, and when is it a smell? How do you tell the two apart in PR review?
3. What's the conceptual difference between secret scanning (detection on existing code) and push protection (prevention at push time)? Why do you need both?

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This lesson guide |
| `config.py` | AWS canary access key + secret key |
| `payment.py` | Fake Stripe `sk_test_FAKE_…` token |
| `github_client.py` | Fake GitHub `ghp_FAKE…` PAT |
| `.env.example` | The right way to share config — placeholders only, no values |
| `solution.md` | Remediation runbook |
