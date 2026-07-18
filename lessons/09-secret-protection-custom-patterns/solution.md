# Solution — Lesson 09

How to respond when a custom-pattern alert fires, and how to design new patterns that earn their keep.

## How to revoke

In this workshop the "tokens" are fake — there's nothing to revoke. In a real org, a custom-pattern alert kicks off the same incident response as any other secret leak (see `lessons/08-secret-protection-secret-scanning/solution.md` for the general runbook), with one extra step at the front:

0. **Verify it's actually one of your tokens.** Custom patterns can false-positive on test fixtures, log samples, sample data, or third-party code that uses the same prefix. Triage before you wake anyone up at 02:00.
1. **Rotate** via your internal token-issuing service (or whatever owns the format).
2. **Audit** access logs at the receiving service.
3. **Purge from history** with `git filter-repo` / BFG.
4. **Replace** with a runtime secrets manager + short-lived tokens.

Most importantly, file a follow-up: *why did the developer hard-code it?* Often the answer is "because there was no good alternative" — and the fix is to make the secrets manager easier to use, not to lecture the developer.

## How to design a robust pattern

A pattern is good if it (a) catches every real leak and (b) doesn't drown the security team in false positives. Use this recipe:

### 1. Anchor with a unique prefix

Most home-grown tokens already do this; if yours doesn't, add one. `CONTOSO-API-`, `contoso_demo_`, `acme_pat_v2_`, `_NSPK_` — all good. The prefix should be unlikely to appear in normal code or English text.

### 2. Use a character class that matches the issuing format exactly

If your token-issuing service emits base32, the body is `[A-Z2-7]` — not `[A-Za-z0-9]`. Tightening the character class meaningfully reduces false positives.

### 3. Bound the length

A bound (`{32}`, `{16,}`, `{12,16}`, …) prevents the regex from matching short prefixes-as-strings ("CONTOSO-API-USER" in a comment) and from catastrophic-backtracking on huge log lines.

### 4. Always supply a test string in the UI

GitHub's "New pattern" dialog has a *Test string* field. Paste a fake example match, then **Save and dry run** before publishing. The dry run samples up to 1,000 matches without creating alerts; inspect those results for false positives, edit, and rerun. A green test-string match proves only recall for that example, not precision across the repository.

### 5. Treat AI output as candidates, not policy

**Generate with AI** can turn an English description and fake examples into up to three regex suggestions. It is GA for organization/enterprise repositories with GitHub Secret Protection and does not require a GitHub Copilot subscription. Compare candidate character classes, lengths, grouping, and anchors; select one with **Use results**, then validate it with the same dry-run gate as a hand-written regex. Never paste real tokens into the examples.

### 6. Use before/after anchors when context is reliable

If the token always appears in `Authorization: Bearer <token>`, anchor `before_secret: "Bearer "` so a stray `Bearer ` in unrelated code doesn't trip you up. If it always appears in JSON as `"api_key": "<token>"`, anchor accordingly.

### 7. Pilot before going wide

Roll a new pattern out at the **repo level** first (like this lesson does). Watch the alert volume for a week. Tune. Then promote to org level. A noisy pattern that fires 100 times a day on test fixtures will get muted by your team and stop catching real leaks.

### 8. Pair custom patterns with push protection

After a dry run succeeds and the pattern is published, click **Enable** for push protection on patterns that should never appear in source. Repository push protection must also be enabled. That way the *next* leak gets blocked at push time, not after it lands in `main`.

## Reference

- Define and dry-run custom patterns: <https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-your-secrets/customize-leak-detection/define-custom-patterns>
- Generate custom-pattern regexes with AI: <https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-your-secrets/customize-leak-detection/generating-regular-expressions-for-custom-patterns-with-ai>
- GitHub Secret Protection plans and features: <https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/about-github-advanced-security>
