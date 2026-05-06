# Lesson 02 — Secret Scanning + Push Protection

See GitHub Advanced Security detect hard-coded credentials in source, block new ones at `git push`, and validate live tokens with partner providers.

## Goal

Experience secret scanning and push protection end-to-end. The **live demo** is push protection — push a fresh canary in a workshop branch and watch GitHub stop the push before it ever lands on the remote. The static files below document the credential **formats** GHAS recognizes.

## What's in this lesson

Four Python files plus a `.env.example`. Each Python file hard-codes a *fake* credential that matches a partner pattern — `AKIA…`, `sk_test_…`, `ghp_…` — but every value is either documented as fake by its issuer or clearly marked `FAKE` / `EXAMPLE` / `DEMO`.

| File | Format demonstrated |
| --- | --- |
| `config.py` | `AWS Access Key ID` + `AWS Secret Access Key` (AWS-documented canaries) |
| `payment.py` | `Stripe API Key` (test key with `sk_test_` prefix) |
| `github_client.py` | `GitHub Personal Access Token` (`ghp_` prefix) |
| `.env.example` | **Nothing** — placeholders only. This teaches the right pattern. |

> ⚠️ Every file (except `.env.example`) starts with a "this is intentionally vulnerable" header. Do not copy these patterns into real code.

## Why the alert tab might look empty before you start

Modern secret scanning combines regex match with **AI-powered suppression** of obvious test/example values, **provider denylists** (AWS publishes its own list of well-known canary keys like `AKIAIOSFODNN7EXAMPLE`), and **validity probing**. When the static files in this lesson contain words like `FAKE`, `DEMO`, or AWS's canary value, GHAS may correctly suppress them as "obviously not a real leak" — that's the feature working as designed for the production case, not a bug.

This is exactly why the **live push-protection moment** is the heart of this lesson. When an attendee pushes a *new* line that looks like a credential, GHAS evaluates it without the benefit of seeing it's already-known-fake — and push protection fires.

![Default tab of Security → Secret scanning showing "No secrets found" — partner-pattern detections suppressed by AI heuristics on the committed FAKE / DEMO / EXAMPLE-marked canaries.](../../docs/screenshots/06-secret-scanning-default-empty.png)

*The **Default** tab is empty by design — the committed canaries are flagged-and-suppressed by AI heuristics. This is the suppression behaviour described above; it is not a misconfiguration._

![Generic AI tab of Security → Secret scanning showing alerts firing on `hunter2_FAKE_*`-style password assignments — caught by the AI-powered generic-secret classifier rather than a partner pattern.](../../docs/screenshots/06-secret-scanning-generic-ai.png)

*The **Generic** tab (AI-powered detection) is where committed-but-unrecognized credential shapes do surface. Useful to show alongside the Default tab to explain why one looks empty and the other doesn't._

## Push protection demo

Push protection runs **client-side at `git push` time** — GitHub refuses the push before the secret is written to the remote. Try it:

![Repo Settings → Code security → Secret scanning showing Push protection toggled on, with the bypass-prompt copy displayed for contributors.](../../docs/screenshots/02-push-protection-settings.png)

*Repo settings page showing push protection enabled. Confirm this checkbox is green before running the live demo — without it the push below will succeed silently._

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

   > 📋 **Live verification capture (2026-05-06).** During preflight a fresh `AKIA…` access key + 40-char secret pair was pushed to an ephemeral branch on this repo. **The push was *not* blocked** (`EXIT_CODE: 0`) — this is captured verbatim below. Re-confirm push protection is actually enforcing in *Settings → Code security → Secret scanning* before running this demo for an audience; if you see the same behaviour, lean on the partner-pattern alert in *Security → Secret scanning* (the *Generic* AI tab) instead of the push-block moment for this run, and treat the lack of a block as a teaching point about feature-prerequisite verification rather than a script failure.

   ```text
   # Push-protection live test — captured 2026-05-06 (UTC)
   #
   # OBSERVED BEHAVIOR: push protection did NOT block this push.
   # The fresh canary committed was:
   #   TEST_AWS_KEY    = "AKIAQ7HYG3LZDFNV4P9X"   (20 chars, AKIA prefix)
   #   TEST_AWS_SECRET = "kMxR8JqLPmZbV5tNcW2yFhDgX7sQpA1RyZ4ePaT3"  (40 chars)
   #
   # These were placed adjacent in lessons/02-secret-scanning/canary-test.py
   # on branch test-push-protection-ephemeral and pushed. The push SUCCEEDED
   # (exit 0) — no GH013 secret-scanning rule violation was emitted from the
   # remote. The remote branch (and its canary) were deleted immediately
   # after capture.
   #
   # Verbatim push output follows (all stderr+stdout, no redaction):
   # ----------------------------------------------------------------
   remote:
   remote: Create a pull request for 'test-push-protection-ephemeral' on GitHub by visiting:
   remote:      https://github.com/tkl-enteprises/ghas-demos/pull/new/test-push-protection-ephemeral
   remote:
   remote: GitHub found 98 vulnerabilities on tkl-enteprises/ghas-demos's default branch (6 critical, 36 high, 46 moderate, 10 low). To find out more, visit:
   remote:      https://github.com/tkl-enteprises/ghas-demos/security/dependabot
   remote:
   To https://github.com/tkl-enteprises/ghas-demos.git
    * [new branch]      test-push-protection-ephemeral -> test-push-protection-ephemeral
   branch 'test-push-protection-ephemeral' set up to track 'origin/test-push-protection-ephemeral'.
   EXIT_CODE: 0
   ```

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
