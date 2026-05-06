# Lesson 06 — Custom Secret Scanning Patterns

Detect *org-specific* secret formats that no partner pattern covers, by defining your own regex in `.github/secret_scanning.yml`.

## Goal

Most teams have at least one home-grown credential format — an internal service token, a workshop key, a build-system bearer. Partner patterns don't know about these. Custom secret scanning patterns let you teach GHAS what *your* secrets look like.

## Where the patterns live

This lesson uses two custom patterns defined at the repo level in [`.github/secret_scanning.yml`](../../.github/secret_scanning.yml):

| Pattern name | Regex | Example match |
| --- | --- | --- |
| TKL Internal Token | `TKL-INTERNAL-[A-Z0-9]{12,16}` | `TKL-INTERNAL-DEMO123ABC456` |
| TKL Workshop Demo Key | `tkl_demo_[a-z0-9]{32}` | `tkl_demo_abcdef0123456789abcdef0123456789` |

Each Python file in this lesson hard-codes a fake match for one of those patterns so GHAS has something to detect.

## Org-level vs repo-level

Custom patterns can be defined at three scopes — pick the one that matches who needs to maintain the pattern:

- **Repo level** (this lesson): `.github/secret_scanning.yml`. Quick to iterate, version-controlled with the code, but only protects the one repo. Useful when prototyping a pattern.
- **Org level**: Org → Settings → Code security → Secret scanning → Custom patterns. Apply to all repos in the org with one click. Recommended for any pattern that's broadly useful.
- **Enterprise level**: Enterprise admin console → Code security → Secret scanning → Custom patterns. Apply across every org in the enterprise. Use for company-wide token formats.

Reference: <https://docs.github.com/en/code-security/secret-scanning/defining-custom-patterns-for-secret-scanning>

In a real workshop, you'd typically promote a working repo-level pattern to org-level once it's proven not to false-positive. The repo-level YAML in this lesson is also a great pattern-as-code artefact that you can review in PR.

## Hands-on steps

1. Open [`.github/secret_scanning.yml`](../../.github/secret_scanning.yml) and read the two pattern definitions.
2. Open `internal.py` and `demo_key.py` in this lesson — both contain a fake string that matches one of the custom patterns.
3. Visit **Security → Secret scanning** for the repo: <https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning>
4. Filter by *Secret type* → look for "TKL Internal Token" and "TKL Workshop Demo Key".
5. Confirm both alerts are open, with the file path and line number pointing at this lesson.
6. Optionally: clone the repo, edit `internal.py` to add another `TKL-INTERNAL-…` value, and watch push protection block your push (custom patterns are pushable too if marked `push_protection: true` in the YAML).

## Designing custom patterns — checklist

A good custom pattern is **specific** (low false-positive rate) and **anchored** (only matches in the right context). Use this checklist when adding a new one:

- ✅ **Stable, distinctive prefix.** `TKL-INTERNAL-`, `tkl_demo_`, `acme_pat_`, etc. The prefix is what saves you from matching every random base64 string.
- ✅ **Length bounds.** `[A-Z0-9]{12,16}` is much better than `[A-Z0-9]+`. A bound makes accidental matches on log lines and short hashes less likely.
- ✅ **Character-class precision.** If the body is base32, write `[A-Z2-7]`, not `[A-Za-z0-9]`. The narrower the class, the higher the precision.
- ✅ **`regex_pattern_test_string`** in the YAML — every pattern should ship with a test string that the regex must match (and ideally a counter-example that it must *not* match). Treat it like a unit test.
- ✅ **`before_secret` / `after_secret` anchors** when the surrounding context is predictable. E.g. a token that always appears in `Authorization: Bearer <token>` headers can anchor on `Bearer ` before and `\s|$` after.
- ❌ **Don't try to match passphrases.** Anything that looks like English words has too high a base rate in source code (variable names, comments, fixtures). Use AI-powered detection for that — it's purpose-built.
- ❌ **Don't match secrets shorter than ~12 characters** unless the prefix is highly distinctive. Short secrets collide with everything.

## Where to look

- Repo alerts: <https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning>
- Filter the alert list by *Secret type* → "TKL Internal Token" / "TKL Workshop Demo Key".

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This lesson guide |
| `internal.py` | Fake `TKL-INTERNAL-…` token, matches custom pattern #1 |
| `demo_key.py` | Fake `tkl_demo_…` key, matches custom pattern #2 |
| `solution.md` | How to revoke + how to design robust patterns |
