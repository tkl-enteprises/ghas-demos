# Facilitator notes

Instructor-side companion to [`README.md`](README.md). Read this once before running the workshop.

> ⚠️ This repository is **intentionally vulnerable**. Set expectations with attendees up front: every finding they see is real and detected by [GitHub Advanced Security (GHAS)](https://docs.github.com/en/code-security/getting-started/github-security-features) — the bugs and secrets are deliberate teaching aids, not mistakes.

---

## Pre-flight checklist

Run through this before attendees join. None of these are reversible mid-session and most will silently break the demo if missed.

1. **Confirm GHAS is on for this repo.** Repo → `Settings → Code security`. Look for green checkmarks next to *Code scanning*, *Secret scanning*, and *Dependabot alerts*. The org [`tkl-enteprises`](https://github.com/tkl-enteprises) has a GHAS license; new repos in the org may still need the recommended security configuration applied.
2. **Enable Dependabot alerts and security updates.** Repo → `Settings → Code security → Dependabot`. Turn on *Dependabot alerts*, *Dependabot security updates*, and *Dependabot version updates* (the last one needs the `dependabot.yml` shipped in `.github/`).
3. **Enable secret scanning + push protection.** Repo → `Settings → Code security → Secret scanning`. Turn on *Secret scanning*, *Push protection*, and *Push protection for contributors* if your org policy allows. Push protection is what makes lesson 2 land — without it, secrets only get flagged after the fact.
4. **Verify the CodeQL workflow ran at least once.** `Actions → CodeQL`. If you see a green checkmark, code scanning has a baseline. If you see nothing, push any commit (or click *Run workflow*) and wait — without that baseline, lesson 1 has nothing to show.
5. **Verify Copilot Autofix is enabled.** Repo → `Settings → Code security → Code scanning → Copilot Autofix`. This is what makes lesson 4 work; if it's off, attendees won't see the *Generate fix* button.
6. **Publish the two custom secret patterns for lesson 6.** Repo → `Settings → Code security → Secret scanning → Custom patterns → New pattern`. Lesson 6's `.github/secret_scanning.yml` was deliberately removed because that file only supports path exclusions — *not* custom-pattern definitions. Add these two by hand:
   - `TKL Internal Token` → format `TKL-INTERNAL-[A-Z0-9]{12,16}`, test string `TKL-INTERNAL-DEMO123ABC456`
   - `TKL Workshop Demo Key` → format `tkl_demo_[a-z0-9]{32}`, test string `tkl_demo_abcdef0123456789abcdef0123456789`
   Tick *Push protection* on each if you want lesson 6's optional push-block step to work. See [lesson 6 README](lessons/06-custom-secret-patterns/README.md) for screenshots of the preflight.
7. **Have the org Security Overview tab open on a second tab.** [https://github.com/orgs/tkl-enteprises/security/overview](https://github.com/orgs/tkl-enteprises/security/overview) — lesson 8 is entirely UI-driven and the page can take a few seconds to load on first visit.

## Per-lesson timing guidance

No clock times — pace varies wildly by audience. Use these qualitative buckets when planning your agenda:

| # | Lesson | Length | Notes |
| - | ------ | ------ | ----- |
| 1 | CodeQL Code Scanning | medium | The "wow" lesson. Spend time on the alert UI, dataflow path, and severity. |
| 2 | Secret Scanning + Push Protection | short | Live `git push` of a fake key is the whole demo — keep it tight. |
| 3 | Dependabot / Supply Chain | medium | Walk through both alerts *and* the auto-generated PRs. |
| 4 | Copilot Autofix | short | One-click suggestion → review → commit. Fast and visual. |
| 5 | Custom CodeQL Queries | long | The most technical lesson. Skip on non-engineering audiences. |
| 6 | Custom Secret Patterns | medium | Org admins love this; ICs less so. Match to your audience. |
| 7 | SARIF / 3rd-party Tool Integration | medium | Show how non-GitHub scanners surface in the same UI. |
| 8 | Security Overview (Org-level Governance) | short | Pure UI tour. No code. Best as a closer. |

## Common attendee gotchas

- ❌ **"My CodeQL workflow didn't run on my fork."** Workflows on forks need explicit consent — the first push from a fork triggers a *Workflow awaiting approval* state. Have attendees push to a branch on the upstream repo instead, or be ready to approve workflows from the *Actions* tab.
- ❌ **"Secret scanning isn't showing my fake key."** Three distinct causes:
  1. On the free tier, secret scanning only runs on public repos. This repo is public, so it works — but attendees re-running on a private fork without GHAS will see nothing.
  2. **AI-powered detection and provider denylists deliberately suppress obvious fakes** in committed history (e.g. AWS's documented canary `AKIAIOSFODNN7EXAMPLE`, or any string with `FAKE`/`DEMO`/`EXAMPLE` markers). That's the feature working correctly. The reliable workshop demo is the **push protection moment** — push a *fresh* canary line in a workshop branch and watch the push get blocked. Lesson 2's README sets this expectation explicitly.
  3. **As of last verification (2026-05-06), `0` partner-pattern alerts and `0` push-protection blocks fired on this repo.** The committed AWS canary, FAKE-marker Stripe, and FAKE-marker GitHub PAT are deliberately suppressed by AI heuristics — that's the feature, not a bug. The workshop's reliable detection moment is the live push of a fresh canary in step 2's hands-on flow. **Caveat from this verification run:** a freshly-generated `AKIA…` access-key + 40-char secret pair pushed to an ephemeral branch was *not* blocked either (push succeeded with `EXIT_CODE: 0`; see `docs/screenshots/push-protection-block.txt`). Before facilitating, re-confirm push protection is *actually* enforcing in repo *Settings → Code security → Secret scanning → Push protection* (and that the `tkl-enteprises` Enterprise GHAS license is attached) — the `secret-scanning/alerts` REST endpoint also returned `404` for a pull-only collaborator token, which is consistent with secret scanning not being active on this repo at the time of measurement.
- ❌ **"Push protection let me push my secret."** Push protection only blocks **patterns GitHub recognizes** by default. The fake AWS key in lesson 2 matches a partner pattern; randomly chosen strings will not. If a demo "fails," check the pattern, not the feature.
- ❌ **"Lesson 6 alerts aren't appearing."** Custom patterns are not version-controlled — they live in repo *Settings*. If you skipped step 6 of the preflight, the two custom patterns aren't published, and the demo files in lesson 6 will sit silent regardless of how long you wait.
- ❌ **"Dependabot didn't open a PR."** Dependabot security updates require the manifest file (e.g. `requirements.txt`) to be at a path Dependabot knows about. The `dependabot.yml` in `.github/` is what tells it where to look — if attendees move files around in their fork, the PRs stop.
- ❌ **"Autofix button is missing."** Either Autofix is off in repo settings, or the alert is in a language Autofix doesn't yet support. Lesson 4 picks alerts that are known-supported.
- ❌ **"Code scanning shows zero alerts."** The CodeQL workflow either hasn't finished its first run, or it ran on a branch with no vulnerable code. Check `Actions → CodeQL` first.
- ❌ **"Several 'Dependabot Updates' workflow runs show as failure."** Those red runs are Dependabot's *internal* rebase/recompute jobs, not the workshop's CI. They fire when Dependabot can't compute a clean update graph for a manifest (typically because a transitive dep also needs to move, or two PRs touch the same lockfile). They do **not** block PR creation — the seven pip-dep PRs in lesson 3 still appear, still surface their CVE annotations, and still merge correctly. Safe to ignore; do not panic-debug them mid-session.

## Reset between sessions

Several options, in order of cleanliness:

1. ✅ **Have each attendee fork the repo.** Cleanest reset. Each fork starts with its own alert state. Caveat: forks need workflows approved (see gotchas above), and secret scanning won't run on private forks without GHAS.
2. ✅ **Dismiss alerts as "False positive — used for testing"** between sessions. Closed alerts can be **re-opened** from the alert detail page (or via API), so this is a non-destructive reset. This is the recommended path if you're running back-to-back sessions on the same repo.
3. ⚠️ **Delete and re-create the repo.** Nuclear option. Loses any audience PRs and Dependabot history. Only do this if alerts are genuinely corrupted.

> 📝 Closed alerts re-open automatically the next time the underlying scanner re-detects the same finding (CodeQL on next workflow run, Dependabot on its next refresh, secret scanning on the next push that touches the file). You usually do not need to manually re-open anything.

## Talking points per pillar

One paragraph per lesson — use these as the verbal intro before each demo.

### 1. CodeQL Code Scanning
[CodeQL](https://codeql.github.com/) is GitHub's semantic code analysis engine. It builds a queryable database from your source and runs **dataflow queries** that follow tainted input from a *source* (e.g. an HTTP request) to a *sink* (e.g. a SQL query). Unlike regex-based linters, it understands variables, functions, and call graphs — which is why it finds real bugs and not just suspicious strings. The alerts surface in the same `Security → Code scanning` tab regardless of whether they came from the default suite, a custom pack, or a third-party tool via SARIF.

### 2. Secret Scanning + Push Protection
[Secret scanning](https://docs.github.com/en/code-security/secret-scanning) looks for known credential patterns (cloud provider keys, npm tokens, Stripe keys, ~200 partner patterns). **Push protection** moves that detection *left* — it runs at `git push` time and blocks the push before the secret reaches the remote. The mental model: secret scanning is the smoke detector; push protection is the sprinkler that goes off before the fire reaches the server room.

### 3. Dependabot / Supply Chain
[Dependabot](https://docs.github.com/en/code-security/dependabot) does three things people often conflate: **alerts** (your dependency has a known CVE), **security updates** (auto-PRs that bump the vulnerable dependency to a patched version), and **version updates** (routine bumps regardless of vulnerabilities). The dependency graph powering all three is also what feeds the [advisory database](https://github.com/advisories), which is the same data Dependabot reads.

### 4. Copilot Autofix
[Copilot Autofix](https://docs.github.com/en/code-security/code-scanning/managing-code-scanning-alerts/about-autofix-for-codeql-code-scanning) takes a CodeQL alert and uses an LLM grounded in the alert's dataflow path to draft a code fix as a suggestion you can commit straight from the PR review. The point isn't that the AI writes perfect code — it's that the *fix is grounded in the same dataflow analysis that found the bug*, so the suggestion is usually actually relevant. Always review before merging.

### 5. Custom CodeQL Queries
The default CodeQL suite is a starting point, not a ceiling. Security teams write **custom queries** for organization-specific patterns: deprecated internal APIs, banned functions, framework-specific anti-patterns. This lesson shows how to author a `.ql` file, run it locally with the CodeQL CLI, and ship it as part of the same code scanning workflow so its findings appear alongside the defaults.

### 6. Custom Secret Patterns
Beyond the ~200 partner patterns, GHAS lets org admins define **custom secret patterns** with regex + an optional pre/post-match heuristic. This is how you catch *your own* token formats — internal API keys, employee badge IDs, anything with a recognizable shape. Critically, custom patterns also participate in **push protection**, so they're enforceable, not just observable.

### 7. SARIF / 3rd-party Tool Integration
[SARIF](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) is the OASIS standard format for static analysis results. Any tool that emits SARIF (Bandit, Semgrep, Trivy, vendor scanners) can upload its findings via the `github/codeql-action/upload-sarif` action and they will appear in the same `Security → Code scanning` tab as CodeQL. Same triage UI, same alert lifecycle, same dismissal reasons. This is the pillar that lets security teams consolidate.

### 8. Security Overview (Org-level Governance)
At org scale, per-repo alert pages don't scale. The [Security Overview](https://docs.github.com/en/code-security/security-overview/about-security-overview) tab is the **CISO view**: which repos have which features enabled, where alerts are concentrating by severity, which teams own the most risk, and what *security configurations* are applied across the fleet. This is the upsell story — it's the difference between "we have GHAS" and "we manage GHAS."

## Where to capture screenshots

For the follow-up deck. Capture from a real tenant — the workshop materials intentionally do not bundle screenshots so each delivery can use a fresh, current UI.

- 📸 The **alert detail page** for one CodeQL finding (lesson 1) — show the dataflow path expanded.
- 📸 The **push protection block** in the terminal **and** the corresponding *Bypass* dialog in the GitHub UI (lesson 2).
- 📸 A **Dependabot security update PR** with the changelog and CVE link visible (lesson 3).
- 📸 The **Copilot Autofix suggestion diff** before and after acceptance (lesson 4).
- 📸 A **custom query** finding listed alongside default-suite findings in the same alerts list (lesson 5).
- 📸 A **custom secret pattern** match with the masking applied (lesson 6).
- 📸 A **third-party SARIF tool** finding (e.g. from Bandit) showing in `Security → Code scanning` (lesson 7).
- 📸 The **org Security Overview** dashboard, the **Coverage** view, the **Risk** view, and the **Configurations** page (lesson 8 — capture all four).
