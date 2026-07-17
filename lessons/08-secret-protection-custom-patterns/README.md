# Lesson 08 — Custom Secret Scanning Patterns

Detect *org-specific* secret formats that no partner pattern covers, by defining your own regex.

## Goal

Most teams have at least one home-grown credential format — an internal service token, a workshop key, a build-system bearer. Partner patterns don't know about these. Custom secret scanning patterns let you teach GHAS what *your* secrets look like.

## Learning objectives

After this lesson you can:

- Define a repo-level custom secret pattern with regex, name, and test string.
- Generate multiple regex candidates with AI, review the candidates, and select rather than blindly trust one.
- Use **Save and dry run** to measure matches without creating alerts before publishing.
- Verify a custom pattern fires only on its intended shape (precision check).
- Decide when to scope a pattern at repo / org / enterprise level.
- Apply the "specific + anchored" design rules to a pattern of your own.

## Estimated time

**~10 min demo + 5 min discussion**

## Prerequisites

- An organization-owned repository on **GitHub Team or GitHub Enterprise Cloud** with **GitHub Secret Protection** (or a legacy GitHub Advanced Security entitlement) enabled. Custom patterns and the AI generator are Secret Protection features; they are not accurately described as “Enterprise tier only.”
- Repo-admin permission on `tkl-enteprises/ghas-demos` (custom patterns are configured in repo Settings).
- Facilitator preflight has both `Contoso API Token` and `Contoso Workshop Demo Key` patterns published — see *Configure the patterns* below.

> **Status/licensing:** AI-generated custom-pattern regexes are **generally available**, not preview. Despite using GitHub AI, the generator does **not** require a GitHub Copilot subscription. It requires GitHub Secret Protection on an organization- or enterprise-owned repository. GitHub's documented `GHE.com` data-residency exclusion applies to public monitoring (Lesson 07), not to this generator; do not invent an exclusion where the product documentation does not state one.

## Where the patterns live

> 🛠️ **Custom patterns are not configuration files in source control.** A common misconception is that `.github/secret_scanning.yml` defines custom patterns — it does not. That file supports scanner path exclusions. This lesson uses repo / org / enterprise *Settings* because the AI candidate and dry-run workflow is presented in the GitHub UI.

This lesson exercises two custom patterns. The facilitator (or a workshop preflight script) configures them once via the UI:

| Pattern name | Regex | Test string |
| --- | --- | --- |
| Contoso API Token | `CONTOSO-API-[A-Z0-9]{16,}` | `CONTOSO-API-FAKEDEMO0123456789ABCDEF` |
| Contoso Workshop Demo Key | `contoso_demo_[a-z0-9]{32}` | `contoso_demo_abcdef0123456789abcdef0123456789` |

Each Python file in this lesson hard-codes one fake match. Once the patterns are saved in repo settings, GHAS scans the repo and surfaces both as alerts.

> 🎯 **Why `Contoso`?** [Contoso](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/maui/converters/empty-string-converter) is Microsoft's canonical fictitious-customer name (alongside Fabrikam, Adventure Works, etc.). Combined with explicit `FAKE` / `DEMO` markers, it makes these fixtures visibly nonfunctional and unlikely to be mistaken for a provider credential. Custom patterns are vendor-neutral—pick a distinctive prefix reserved for testing in *your* org.

### Configure the patterns with AI candidates and a dry run (facilitator preflight)

1. Open `https://github.com/tkl-enteprises/ghas-demos/settings/security_analysis` (or *Settings → Code security*).
2. Scroll to *Secret scanning → Custom patterns* and click **New pattern**.
3. Enter **Pattern name:** `Contoso API Token`, then click **Generate with AI**.
4. In the generator, provide only fake examples:
   - **I want a regular expression that:** `Matches a literal CONTOSO-API- prefix followed by at least 16 uppercase ASCII letters or digits.`
   - **Examples of what I'm looking for:** `CONTOSO-API-FAKEDEMO0123456789ABCDEF`
5. Click **Generate suggestions**. The model can return up to three candidates with descriptions. Compare them for an escaped literal prefix, the exact `[A-Z0-9]` class, and a lower bound of 16. Select a safe candidate with **Use results**. A suitable result is `CONTOSO-API-[A-Z0-9]{16,}`, but generated output can vary.
6. Add the fake example to **Test string**, then click **Save and dry run**. A dry run finds matches **without creating alerts** and returns a sample of up to 1,000 results. Confirm it finds `internal.py`; inspect every result for false positives.
7. Tighten the candidate and repeat the dry run if needed. Only then click **Publish pattern**. Publishing triggers scanning across the repository's Git history and branches.
8. Repeat the candidate-review/dry-run flow for:
   - **Pattern name:** `Contoso Workshop Demo Key`
   - **Description:** `Matches a literal contoso_demo_ prefix followed by exactly 32 lowercase ASCII letters or digits.`
   - **Fake example:** `contoso_demo_abcdef0123456789abcdef0123456789`
   - **Expected shape:** `contoso_demo_[a-z0-9]{32}`
9. After each pattern is published, optionally click **Enable** for push protection. The option is available only after a successful dry run and publication, and repository push protection must also be enabled.

> At organization scope, a dry run can target all repositories or up to 10 selected repositories. At enterprise scope, select up to 10 repositories and remember that only the pattern creator can edit/dry-run it, using repositories where they have admin access.

Once both patterns are published, GHAS rescans automatically and the two demo files in this lesson will show up under **Security → Secret scanning**.

![Historical Generic AI tab of Security → Secret scanning showing AI-detected password alerts.](../../docs/screenshots/08-secret-scanning-generic-ai.png)

*Preserved historical UI: the current documentation calls this separate list **AI-detected secrets**. It currently detects unstructured passwords; it is not a fallback detector for arbitrary Contoso token shapes. The Contoso fixtures alert only after their custom patterns are published._

## Org-level vs repo-level

Custom patterns can be defined at three scopes — pick the one that matches who needs to maintain the pattern:

- **Repo level** (this lesson): repo *Settings → Code security → Secret scanning → Custom patterns*. Quick to iterate, but only protects the one repo. Useful when prototyping a pattern.
- **Org level**: org *Settings → Code security → Secret scanning → Custom patterns*. Apply to all repos in the org with one click. Recommended for any pattern that's broadly useful.
- **Enterprise level**: enterprise admin console → *Code security → Secret scanning → Custom patterns*. Apply across every org in the enterprise. Use for company-wide token formats.

Reference: <https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-your-secrets/customize-leak-detection/define-custom-patterns>

In a real workshop, you'd typically promote a working repo-level pattern to org-level once it's proven not to false-positive. None of these scopes are version-controlled in source — pattern lifecycle (draft → review → publish → tune) lives entirely in the GitHub UI.

## Hands-on steps

1. Confirm the facilitator preflight above is done — both custom patterns are *Published* in repo settings.
2. Open `internal.py` and `demo_key.py` in this lesson — both contain a fake string that matches one of the custom patterns.
3. Visit **Security → Secret scanning** for the repo: <https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning>
4. Filter by *Secret type* → look for "Contoso API Token" and "Contoso Workshop Demo Key".
5. Confirm both alerts are open, with the file path and line number pointing at this lesson.
6. Review the facilitator's dry-run result (or rerun a draft pattern) and explain why dry run comes before publishing.
7. Optionally: clone the repo, edit `internal.py` to add another fake `CONTOSO-API-…` value, and watch push protection block your push (works only if you enabled push protection on the published custom pattern and on the repository).

## Designing custom patterns — checklist

A good custom pattern is **specific** (low false-positive rate) and **anchored** (only matches in the right context). Use this checklist when adding a new one:

- ✅ **Stable, distinctive prefix.** `CONTOSO-API-`, `contoso_demo_`, `acme_pat_`, etc. The prefix is what saves you from matching every random base64 string.
- ✅ **Length bounds.** `[A-Z0-9]{12,16}` is much better than `[A-Z0-9]+`. A bound makes accidental matches on log lines and short hashes less likely.
- ✅ **Character-class precision.** If the body is base32, write `[A-Z2-7]`, not `[A-Za-z0-9]`. The narrower the class, the higher the precision.
- ✅ **Test string in the UI.** Every pattern should have a fake string that the regex must match. Treat it like a unit test, then use the dry-run results as the precision test before publishing.
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
- Attendees can compare AI-generated candidates, reject an overbroad regex, and explain that dry runs create no alerts.
- Attendees can describe the difference between repo / org / enterprise pattern scope.
- (Optional) A push of a new `CONTOSO-API-…` value is blocked by push protection.

## Key takeaways

- Custom patterns live in **GitHub Settings, not source control** — `.github/secret_scanning.yml` only supports `paths:` exclusions, not pattern definitions.
- The AI regex generator is **GA**, requires GitHub Secret Protection, and requires **no Copilot license**; generated candidates still need human review.
- **Save and dry run** samples up to 1,000 matches without creating alerts. Publish only after tuning.
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
