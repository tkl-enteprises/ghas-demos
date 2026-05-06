# Lesson 05 — Custom Secret Scanning Patterns

Detect *org-specific* secret formats that no partner pattern covers, by defining your own regex.

## Goal

Most teams have at least one home-grown credential format — an internal service token, a workshop key, a build-system bearer. Partner patterns don't know about these. Custom secret scanning patterns let you teach GHAS what *your* secrets look like.

## Learning objectives

After this lesson you can:

- Define a repo-level custom secret pattern with regex, name, and test string.
- Verify a custom pattern fires only on its intended shape (precision check).
- Decide when to scope a pattern at repo / org / enterprise level.
- Apply the "specific + anchored" design rules to a pattern of your own.

## Estimated time

**~10 min demo + 5 min discussion**

## Prerequisites

- GHAS + secret scanning enabled, with **custom patterns** available (Enterprise license tier).
- Repo-admin permission on `tkl-enteprises/ghas-demos` (custom patterns are configured in repo Settings).
- Facilitator preflight has both `Contoso API Token` and `Contoso Workshop Demo Key` patterns published — see *Configure the patterns* below.

## Where the patterns live

> 🛠️ **Custom patterns are configured in the GitHub UI, not in source control.** A common misconception is that `.github/secret_scanning.yml` defines custom patterns — it does not. That file only supports `paths:` exclusions for the scanner. Custom patterns must be added through repo / org / enterprise *Settings* and are not yet exposed via a public REST API at the repo level.

This lesson exercises two custom patterns. The facilitator (or a workshop preflight script) configures them once via the UI:

| Pattern name | Regex | Test string |
| --- | --- | --- |
| Contoso API Token | `CONTOSO-API-[A-Z0-9]{16,}` | `CONTOSO-API-FAKEDEMO0123456789ABCDEF` |
| Contoso Workshop Demo Key | `contoso_demo_[a-z0-9]{32}` | `contoso_demo_abcdef0123456789abcdef0123456789` |

Each Python file in this lesson hard-codes one fake match. Once the patterns are saved in repo settings, GHAS scans the repo and surfaces both as alerts.

> 🎯 **Why `Contoso`?** [Contoso](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/maui/converters/empty-string-converter) is Microsoft's canonical fictitious-customer name (alongside Fabrikam, Adventure Works, etc.). The prefix is **guaranteed not to collide with any real provider**, which makes it the safest choice for demo fixtures: a workshop screenshot ending up on Slack or in a deck can't be mistaken for a real credential. Custom patterns are vendor-neutral — pick any prefix that's distinctive in *your* org.

### Configure the patterns (facilitator preflight)

1. Open `https://github.com/tkl-enteprises/ghas-demos/settings/security_analysis` (or *Settings → Code security*).
2. Scroll to *Secret scanning → Custom patterns* and click **New pattern**.
3. For pattern #1, paste:
   - **Pattern name:** `Contoso API Token`
   - **Secret format:** `CONTOSO-API-[A-Z0-9]{16,}`
   - **Test string:** `CONTOSO-API-FAKEDEMO0123456789ABCDEF` (verify the dry-run preview turns green).
4. Click *Publish pattern* → confirm it scans across the repo.
5. Repeat for pattern #2 with name `Contoso Workshop Demo Key`, format `contoso_demo_[a-z0-9]{32}`, test string `contoso_demo_abcdef0123456789abcdef0123456789`.
6. Optional: tick *Push protection* on each pattern so workshop attendees can demo push-protection on custom patterns too.

Once both patterns are published, GHAS rescans automatically and the two demo files in this lesson will show up under **Security → Secret scanning**.

![Generic AI tab of Security → Secret scanning showing alerts firing on `hunter2_FAKE_*`-style password assignments — the same generic classifier that surfaces custom-token-shaped strings before a partner pattern exists.](../../docs/screenshots/05-secret-scanning-generic-ai.png)

*The **Generic** AI tab of the secret-scanning UI. Custom partner patterns land in their own filterable rows on the **Default** tab once published; until then, the generic AI classifier is what catches the demo strings._

## Org-level vs repo-level

Custom patterns can be defined at three scopes — pick the one that matches who needs to maintain the pattern:

- **Repo level** (this lesson): repo *Settings → Code security → Secret scanning → Custom patterns*. Quick to iterate, but only protects the one repo. Useful when prototyping a pattern.
- **Org level**: org *Settings → Code security → Secret scanning → Custom patterns*. Apply to all repos in the org with one click. Recommended for any pattern that's broadly useful.
- **Enterprise level**: enterprise admin console → *Code security → Secret scanning → Custom patterns*. Apply across every org in the enterprise. Use for company-wide token formats.

Reference: <https://docs.github.com/en/code-security/secret-scanning/defining-custom-patterns-for-secret-scanning>

In a real workshop, you'd typically promote a working repo-level pattern to org-level once it's proven not to false-positive. None of these scopes are version-controlled in source — pattern lifecycle (draft → review → publish → tune) lives entirely in the GitHub UI.

## Hands-on steps

1. Confirm the facilitator preflight above is done — both custom patterns are *Published* in repo settings.
2. Open `internal.py` and `demo_key.py` in this lesson — both contain a fake string that matches one of the custom patterns.
3. Visit **Security → Secret scanning** for the repo: <https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning>
4. Filter by *Secret type* → look for "Contoso API Token" and "Contoso Workshop Demo Key".
5. Confirm both alerts are open, with the file path and line number pointing at this lesson.
6. Optionally: clone the repo, edit `internal.py` to add another `CONTOSO-API-…` value, and watch push protection block your push (works only if you ticked *Push protection* on the pattern in step 6 of the preflight).

## Designing custom patterns — checklist

A good custom pattern is **specific** (low false-positive rate) and **anchored** (only matches in the right context). Use this checklist when adding a new one:

- ✅ **Stable, distinctive prefix.** `CONTOSO-API-`, `contoso_demo_`, `acme_pat_`, etc. The prefix is what saves you from matching every random base64 string.
- ✅ **Length bounds.** `[A-Z0-9]{12,16}` is much better than `[A-Z0-9]+`. A bound makes accidental matches on log lines and short hashes less likely.
- ✅ **Character-class precision.** If the body is base32, write `[A-Z2-7]`, not `[A-Za-z0-9]`. The narrower the class, the higher the precision.
- ✅ **`regex_pattern_test_string`** in the YAML — every pattern should ship with a test string that the regex must match (and ideally a counter-example that it must *not* match). Treat it like a unit test.
- ✅ **`before_secret` / `after_secret` anchors** when the surrounding context is predictable. E.g. a token that always appears in `Authorization: Bearer <token>` headers can anchor on `Bearer ` before and `\s|$` after.
- ❌ **Don't try to match passphrases.** Anything that looks like English words has too high a base rate in source code (variable names, comments, fixtures). Use AI-powered detection for that — it's purpose-built.
- ❌ **Don't match secrets shorter than ~12 characters** unless the prefix is highly distinctive. Short secrets collide with everything.

## Where to look

- Repo alerts: <https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning>
- Filter the alert list by *Secret type* → "Contoso API Token" / "Contoso Workshop Demo Key".

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This lesson guide |
| `internal.py` | Fake `CONTOSO-API-…` token, matches custom pattern #1 |
| `demo_key.py` | Fake `contoso_demo_…` key, matches custom pattern #2 |
| `solution.md` | How to revoke + how to design robust patterns |

## Exit criteria

The demo has landed when:

- **Security → Secret scanning** shows two custom-pattern alerts (`Contoso API Token`, `Contoso Workshop Demo Key`).
- Attendees can describe the difference between repo / org / enterprise pattern scope.
- (Optional) A push of a new `CONTOSO-API-…` value is blocked by push protection.

## Key takeaways

- Custom patterns live in **GitHub Settings, not source control** — `.github/secret_scanning.yml` only supports `paths:` exclusions, not pattern definitions.
- A good custom pattern is **specific** (distinctive prefix + bounded length) and **anchored** (predictable surrounding context).
- Promote a pattern from **repo → org → enterprise** once it's proven not to false-positive — the GitHub UI is the lifecycle tool, not git.

## Discussion questions

1. Who in your org owns the custom-pattern lifecycle — security team, platform team, or each repo's maintainers? What's the review process before publishing at the org level?
2. Would you accept a 5% false-positive rate on a custom pattern to catch 95% of real leaks, or do you require near-zero false-positives before rolling out at org scope?

## Reset state

This lesson DOES mutate org/repo state because patterns live in Settings:

1. Go to *Settings → Code security → Secret scanning → Custom patterns*.
2. **Delete** `Contoso API Token` and `Contoso Workshop Demo Key` if the next cohort should configure them from scratch.
3. Otherwise leave them in place — the lesson is idempotent and the patterns can stay published between runs.

```bash
git checkout main && git pull
```

If push protection was demoed on a custom pattern, delete any `test-contoso-pattern-*` branches that got pushed.
