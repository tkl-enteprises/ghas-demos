# Facilitator notes

Instructor-side companion to [`README.md`](README.md). Read this once before running the workshop.

> ⚠️ This repository is **intentionally vulnerable**. Set expectations with attendees up front: every finding they see is real and detected by [GitHub Advanced Security (GHAS)](https://docs.github.com/en/code-security/getting-started/github-security-features) — the bugs and secrets are deliberate teaching aids, not mistakes.

---

## Pre-flight checklist

> 🤖 **Run [`scripts/preflight.sh`](scripts/preflight.sh) ~24 hours before the workshop.** It verifies items 1–5 of this checklist plus current alert counts via the GitHub API and returns a green/red summary. Requires `gh` authenticated with `repo` + `read:org` scopes and admin on the demo repo. The manual list below is still authoritative for items the API can't observe (UI-only custom patterns, second-tab setup).

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

## Repo configuration baseline

The repo ships with the following config applied. If you fork/copy this repo, replicate these settings:

| Setting | Value | Why |
| --- | --- | --- |
| Secret scanning | enabled | Detects `AKIA…`, `sk_test_…`, `ghp_…` etc. |
| Push protection | enabled | Blocks new partner-pattern secrets at push time |
| Secret scanning AI detection | enabled | Catches generic secrets the partner patterns miss |
| Validity checks | enabled | Tags alerts as Active / Inactive |
| Non-provider patterns | enabled | Generic password/key detection |
| Dependabot alerts + security updates | enabled | Powers lesson 3 |
| CodeQL (advanced workflow) | `build-mode: none` for Python | Default setup is OFF — would conflict |
| Branch protection on `main` | required checks: CodeQL, Bandit, Dependency Review; admins can bypass | Keeps `main` green |
| Custom secret patterns (lesson 6) | UI-only, not in source | See lesson 6 README + preflight step 6 |

Anything in the *Settings → Code security* sidebar that's NOT in the table above is intentionally left at GitHub's default — flag in a PR if you think we should change one.

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

### Push protection bypass — mitigations for live demos

The verification run logged in [`docs/screenshots/push-protection-block.txt`](docs/screenshots/push-protection-block.txt) shows the failure mode that surprises facilitators most: **a fresh `AKIA…`-shaped canary pushed by an admin pushes through cleanly with `EXIT_CODE: 0` and no block prompt**, even with push protection switched on in repo settings.

**Root cause.** Push protection is gated by the branch ruleset's *bypass list*. On this repo (and on most repos created from GitHub's recommended security configuration) the bypass list defaults to **"Anyone with write access"** — which means every admin and every collaborator with `write` silently bypasses the block. Worse, partner patterns like `AKIA…` are filtered through **validity checks** before push protection fires; an inactive / fake-looking key can be deprioritised by the validator and never trip the block, regardless of the bypass list.

**Three mitigations**, in increasing order of facilitator effort:

1. **Option 3 — Demo with a custom secret pattern (recommended for live workshops).** Lesson 06 ships two custom patterns (`TKL-INTERNAL-…` and `tkl_demo_…`). Custom patterns do **not** route through validity checks, and their push-protection enforcement is per-pattern instead of governed by the partner-pattern path. Pushing a fresh `TKL-INTERNAL-DEMO123ABC456` line on a workshop branch fires the block reliably for every account, every time. **No org-settings change required**, which is why this is the default for live delivery.
2. **Option 2 — Temporarily restrict the bypass list.** Repo → `Settings → Rules → Rulesets → main-branch-protection` → *Bypass list*. Switch from "Anyone with write access" to "Specific roles or teams" and leave the list empty for the duration of the workshop, then revert immediately afterwards. Side effect: while the bypass list is empty, *you* also can't bypass — emergency hotfixes during the session will fail. Set a calendar reminder to revert.
3. **Option 1 — Run the demo from a non-admin account.** The most realistic reproduction of an attendee experience. Create a `workshop-attendee` user (or use a personal scratch account), invite them with `write` access only, and demo the live `git push` from *that* account. Combined with Option 2 (empty bypass list) this gives you a perfectly clean block. Requires advance setup: a separate browser profile and SSH/HTTPS credentials wired up for the demo user.

**Recommendation.** Default to **Option 3** for every delivery. Reach for Option 2 only when an attendee specifically asks "but does it block my admin too?" and you want to demonstrate the answer. Option 1 is the right path for a customer pilot — not for a 60-minute workshop where setup time is already tight.

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

## Per-lesson notes

Lessons whose demo flow needs more than the timing bucket and the talking-point paragraph go here. Lessons not listed are fully captured by their lesson README and their *Talking points per pillar* entry above.

### 4. Copilot Autofix — live walkthrough

**Why no committed screenshot.** Lesson 04 is the only pillar with no embedded image. Autofix is intrinsically interactive — the proposed fix is generated on demand inside the PR review UI, takes 10–30 seconds to render, and then needs to be discussed live (accept / edit / dismiss). A still screenshot strips out everything that makes the lesson land.

**Recommended live alert.** Pick one of these two — both are deterministic and Autofix-supported on this repo:

| Alert | Rule | File | Why it's a good demo |
| --- | --- | --- | --- |
| **#21** | `py/template-injection` (SSTI) | `lessons/01-codeql-code-scanning/insecure_login.py` | High severity, dataflow path is short, Copilot's fix typically introduces `escape()` / autoescape config — easy to read. |
| **#28** | `py/weak-cryptographic-algorithm` | `lessons/01-codeql-code-scanning/insecure_login.py` | Smallest possible fix surface (one-line MD5 → SHA-256 swap). Use this when you have ≤ 5 minutes for the lesson. |

**Demo flow** (≈ 90 seconds end to end):

1. `Security → Code scanning → Alerts`. Filter to **Tool: CodeQL** and click into alert #21 (or #28).
2. Click **Generate fix** (button label may also read *"Autofix this alert"*). Wait 10–30 seconds — narrate the suggestion preview as it loads.
3. Click **Create PR with fix**. Walk through the diff Copilot proposes — *out loud, in the PR review UI*, before merging. This is the part attendees remember.
4. Demonstrate the **edit-then-accept** flow: change one line of Copilot's diff, push to the branch, show that the alert is still resolved when CodeQL re-runs on the PR. Reinforces that Autofix is a starting point, not a rubber stamp.
5. Close with the **dismiss with reason** flow on a separate alert — shows that not every Autofix suggestion has to land.

**License caveat.** The *Generate fix* button only renders for users on a Copilot-enabled organization. If the org doesn't have a Copilot license attached, the button is silently absent — the alert page looks identical otherwise. Verify before the workshop:

```sh
gh api orgs/tkl-enteprises/copilot/billing --jq '.seat_breakdown.total // "none"'
```

A non-zero number means the seat pool exists; `none` (or a 404) means Copilot isn't enabled on the org and lesson 04 should be **swapped for an extra pass through lesson 1** (CodeQL alert triage UI). Document this in the agenda you send attendees so nobody opens a Copilot tab and finds it empty.

## Where to capture screenshots

The repo ships with a frozen set of screenshots under [`docs/screenshots/`](docs/screenshots/), captured against the live `tkl-enteprises/ghas-demos` tenant. They're already embedded in the relevant lesson READMEs and the root README, so attendees see the same UI in markdown that you'll demo live. Re-capture against your own tenant before a deck — the `tkl-enteprises` images are workshop-grade, not customer-deck-grade.

| File | Lesson | Shows |
| --- | --- | --- |
| [`docs/screenshots/00-security-overview.png`](docs/screenshots/00-security-overview.png) | (root README hero) | Repo `Security` tab landing page — alert counts across Code scanning, Secret scanning, and Dependabot. |
| [`docs/screenshots/01-code-scanning-alerts.png`](docs/screenshots/01-code-scanning-alerts.png) | 1 — CodeQL Code Scanning | Code-scanning alerts list filtered to **Tool: CodeQL**. |
| [`docs/screenshots/02-codeql-alert-detail.png`](docs/screenshots/02-codeql-alert-detail.png) | 1 — CodeQL Code Scanning | Alert detail page (SSTI) with the dataflow path expanded — source → sink hops visible. |
| [`docs/screenshots/02-push-protection-settings.png`](docs/screenshots/02-push-protection-settings.png) | 2 — Secret Scanning + Push Protection | Repo `Settings → Code security → Secret scanning` showing the push-protection toggle on. |
| [`docs/screenshots/06-secret-scanning-default-empty.png`](docs/screenshots/06-secret-scanning-default-empty.png) | 2 — Secret Scanning + Push Protection | `Security → Secret scanning` **Default** tab showing "No secrets found" — illustrates AI suppression on committed canaries. |
| [`docs/screenshots/06-secret-scanning-generic-ai.png`](docs/screenshots/06-secret-scanning-generic-ai.png) | 2 + 6 — Secret scanning / Custom patterns | `Security → Secret scanning` **Generic** tab — the AI classifier firing on `hunter2_FAKE_*`-style password assignments. |
| [`docs/screenshots/03-dependabot-alerts.png`](docs/screenshots/03-dependabot-alerts.png) | 3 — Dependabot / Supply Chain | `Security → Dependabot` alerts list across Flask, Jinja2, Werkzeug, urllib3, requests, PyYAML, cryptography. |
| [`docs/screenshots/03-dependabot-prs-list.png`](docs/screenshots/03-dependabot-prs-list.png) | 3 — Dependabot / Supply Chain | Pull requests tab filtered to `app/dependabot` — the seven open pip security-update PRs. |
| [`docs/screenshots/03-dependabot-pr-detail.png`](docs/screenshots/03-dependabot-pr-detail.png) | 3 — Dependabot / Supply Chain | A Flask-bump security-update PR with CVE annotation, release notes, and compatibility score. |
| [`docs/screenshots/05-custom-codeql-rule-list.png`](docs/screenshots/05-custom-codeql-rule-list.png) | 5 — Custom CodeQL Queries | Code-scanning alerts filtered to rule `py/tkl/hardcoded-debug-true` — proves precision (`bypass.py` absent) and recall (`target.py` present). |
| [`docs/screenshots/05-custom-codeql-alert-detail.png`](docs/screenshots/05-custom-codeql-alert-detail.png) | 5 — Custom CodeQL Queries | Alert detail for the custom-query finding — `@id`, `@kind`, source location. |
| [`docs/screenshots/07-actions-tab.png`](docs/screenshots/07-actions-tab.png) | 7 — SARIF Integration | Repo `Actions` tab showing CodeQL, Bandit-SARIF, Dependency review, and Dependabot Updates workflows green. |
| [`docs/screenshots/07-bandit-sarif-findings.png`](docs/screenshots/07-bandit-sarif-findings.png) | 7 — SARIF Integration | Code-scanning alerts filtered to **Tool: Bandit** — B303, B301, B307, B602/B603, B608, B101/B105/B107. |
| [`docs/screenshots/08-org-security-overview-risk.png`](docs/screenshots/08-org-security-overview-risk.png) | 8 — Security Overview | Org-level **Risk** view — open alerts by severity and repo. |
| [`docs/screenshots/08-org-security-overview-coverage.png`](docs/screenshots/08-org-security-overview-coverage.png) | 8 — Security Overview | Org-level **Coverage** view — per-repo enablement of CodeQL / Dependabot / secret scanning / push protection. |
| [`docs/screenshots/push-protection-block.txt`](docs/screenshots/push-protection-block.txt) | 2 — Secret Scanning + Push Protection | Verbatim terminal capture from the 2026-05-06 verification run. **OBSERVED:** push protection did **not** block a fresh `AKIA…` canary on the ephemeral branch (`EXIT_CODE: 0`). Re-verify enforcement before each delivery — see *Common attendee gotchas* above for context. |

Gaps still worth capturing live in your tenant for a follow-up deck:

- 📸 Lesson 4 — the **Copilot Autofix** suggestion diff (before / after acceptance) on the `py/sql-injection` alert in `insecure_login.py`.
- 📸 Lesson 8 — the **Configurations** page showing the `GitHub recommended` security configuration's feature toggles.
- 📸 Lesson 8 — a **Security campaigns** detail page (paid feature) with assigned repos and progress bars.

## Bonus: Code Quality (preview)

[Code Quality](https://github.com/tkl-enteprises/ghas-demos/security/quality) is a *separate* GitHub product from GHAS, but it runs on the same CodeQL engine. Instead of security queries (taint, SQLi, SSRF, etc.) it runs a **maintainability + reliability** query pack (cyclomatic complexity, dead code, unreachable branches, code smells). It's enabled on this repo so attendees can see the boundary clearly.

![Security overview now showing Code Quality enabled](docs/screenshots/security-overview-with-code-quality.png)

**Why mention it in a GHAS workshop?**
- Reinforces the "CodeQL is just an engine — the queries are the product" mental model from lesson 5.
- Lets the room ask "wait, can I write quality queries with the same syntax?" — yes (the answer is: it's the same QL language, just a different query suite).
- Useful counter-example to "every CodeQL alert is a security risk" — quality alerts are advisory, not blocking.

**The teaching moment that makes this worth 3 minutes:** despite this repo having **132 security findings** (32 code-scanning + 98 Dependabot + 2 secret-scanning), it has **0 standard quality findings + 0 AI quality findings** — Maintainability and Reliability both rated "Excellent". Same engine, same code, totally different verdict. The point: "secure" and "high-quality" are independent axes, and you need both query packs to see both views.

![Code Quality findings: 0 standard, 0 AI, Excellent rating](docs/screenshots/code-quality-findings.png)

**How to demo (≤ 3 minutes, slot anywhere after lesson 5):**
1. Settings → Security and quality → **Code quality** is *Enabled* (Preview tag visible).
2. `Security and quality → Code quality → Standard findings` (left nav). Show the empty state with "Excellent" Maintainability and Reliability scores.
3. Compare side-by-side with `Code scanning` (also left nav) — same UI shell, but 32 alerts. Same engine, different query suite.
4. Talking points:
   - **Billing**: charged as Action minutes (NOT GHAS seats) — important for buyers.
   - **Status**: Preview — UI may change before GA.
   - **Push protection / branch ruleset**: NOT applied to quality findings (advisory only).
   - **Same workflow runner type as security CodeQL**: standard GitHub runner; the existing `Code Quality: CodeQL Setup` dynamic workflow handles it — no new YAML to author.

**When to skip:** if your audience cares only about security (e.g. CISO briefing), drop this — it muddies the GHAS-vs-not-GHAS line. The 60-min agenda below skips it; the half-day agenda includes it as a 5-min interlude after lesson 5.

## Sample agendas

Three pre-built agendas. Pick one based on audience size, audience role, and the room you've been given. Total times below assume the [Pre-flight checklist](#pre-flight-checklist) has already been run and the repo is in a known-good state — they do **not** include setup time on the day.

### 60-minute executive overview (lessons 1, 2, 3, 8)

For C-suite, security leadership, or non-technical buyers. Skips lessons 4–7 — those land flatter without an engineering audience. Goal: leave the room knowing GHAS catches code bugs, leaked secrets, and vulnerable dependencies, and that there's a single org-level cockpit for all three.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:05 | — | Welcome + repo tour (`README.md` only) | Set expectations: repo is *intentionally* vulnerable; every alert is real. |
| 0:05–0:15 | 1 — CodeQL | Open alert #21 (SSTI). Walk the dataflow path source → sink. | Where does this fit in the SDLC? What changes if a developer never opens the PR? |
| 0:15–0:25 | 2 — Secret Scanning | Live `git push` of a fresh `TKL-INTERNAL-…` line on a workshop branch (custom pattern from lesson 6 — see *Push protection bypass* mitigations above). | What's our current MTTR on a leaked production secret? |
| 0:25–0:35 | 3 — Dependabot | Show the seven open pip security-update PRs. Open one and walk the CVE annotation. | Who owns merging these today? How long do they sit? |
| 0:35–0:50 | 8 — Security Overview | Org-level **Risk** + **Coverage** views. Highlight enablement gaps. | Which 5 repos do we turn this on next? Who signs off? |
| 0:50–1:00 | — | Q&A + close | Action items: pick the next 5 repos; assign an owner. |

**Total: 60 min.** ⚠️ The lesson-2 demo *must* use the lesson-06 custom pattern — partner-pattern push protection silently bypasses for admins (see mitigation note above).

### 2-hour developer enablement (lessons 1, 2, 3, 4, 6, 7, 8)

For platform / appsec / senior dev audiences who own day-to-day triage. Covers seven of eight lessons; deliberately skips lesson 5 (custom CodeQL queries) — that's its own half-day topic and you'll lose the room if you try to compress it into 15 minutes. Goal: every attendee leaves able to triage an alert, push past a custom-pattern block, and read a SARIF upload.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:10 | — | Repo tour + GHAS pillar map (root README) | Today's three pillars: code, secrets, supply chain. |
| 0:10–0:25 | 1 — CodeQL | Alerts list → alert detail → dataflow. Triage one alert as "won't fix" with reason. | When should you mark something `won't fix` vs `false positive`? |
| 0:25–0:35 | 2 — Secret Scanning | Live custom-pattern push protection block (see lesson 06). Show the secret-scanning Default + Generic tabs. | Why doesn't AWS canary `AKIA…` block? (Validity checks + bypass list.) |
| 0:35–0:50 | 3 — Dependabot | PR list filter `app/dependabot`. Walk one PR; mention the red "Dependabot Updates" runs are internal rebase jobs (gotchas). | Auto-merge policy: green CI + Dependabot? Where's the line? |
| 0:50–1:00 | 4 — Copilot Autofix | Generate-fix on alert #21 or #28. Edit-then-accept the diff. | When *not* to trust Autofix? What's your code-review SLA? |
| 1:00–1:10 | — | ☕ Break | — |
| 1:10–1:25 | 6 — Custom Patterns | Settings → Secret scanning → Custom patterns. Walk the two `TKL_…` patterns (pre-published per pre-flight step 6). Push a fresh `tkl_demo_…` and watch it block. | What internal token shapes belong here? (Badge IDs, internal API keys, vendor IDs.) |
| 1:25–1:40 | 7 — SARIF | Code-scanning alerts → filter Tool: Bandit. Show the same triage UI as CodeQL. | Which third-party scanners do we want in this view? |
| 1:40–1:55 | 8 — Security Overview | Org **Risk** + **Coverage** + Configurations. | Coverage gap → action plan. |
| 1:55–2:00 | — | Q&A + close | — |

**Total: 120 min.** Plan one ☕ break at the 1:00 mark to keep energy up.

### Half-day deep dive (all 8 lessons)

For mixed appsec + platform engineering audiences who want the full toolkit — including authoring custom CodeQL queries. 4 hours with two breaks. Goal: every attendee can walk away and stand this up on their own repo on Monday.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:15 | — | Welcome, repo tour, pre-flight walkthrough (`scripts/preflight.sh`) | What does "GHAS turned on" actually mean? Five toggles. |
| 0:15–0:40 | 1 — CodeQL | Full triage flow on alert #21: detail → dataflow → close as fixed via PR. | When CodeQL is wrong: investigation flow + dismissal reasons. |
| 0:40–1:00 | 2 — Secret Scanning | Custom-pattern push block (lesson 06). Show AI-suppressed `AKIA…` canary. Walk validity-check flag in alert detail. | Threat model: leaked secrets in commits vs CI logs vs container images. |
| 1:00–1:25 | 3 — Dependabot | Alerts list → PR list → PR detail. Show CVSS + EPSS + compatibility score. | Dependabot vs reachability: where do we draw the line? |
| 1:25–1:40 | — | ☕ Break | — |
| 1:40–1:55 | 4 — Copilot Autofix | Autofix on alert #21. Edit-then-accept. Try a second alert and dismiss-with-reason. | Where Autofix earns its keep; where it doesn't. |
| 1:55–2:40 | 5 — Custom CodeQL | Walk `lessons/05-custom-codeql-queries/queries/` — read `py/tkl/hardcoded-debug-true.ql`. Run locally with `codeql database analyze`. Show the alert appearing on the next PR. | Authoring custom queries: when is this the right tool vs. a lint rule? |
| 2:40–2:55 | — | ☕ Break | — |
| 2:55–3:15 | 6 — Custom Patterns | Walk the two `TKL_…` patterns; push-block a fresh `tkl_demo_…`; show the matching alert. | Pattern hygiene: pre/post-match heuristics, false-positive rate. |
| 3:15–3:35 | 7 — SARIF | `Bandit-SARIF` workflow run → upload-sarif step → unified Code-scanning view. Show how Bandit findings interleave with CodeQL findings. | Tool consolidation: which scanners stay, which go? |
| 3:35–3:55 | 8 — Security Overview | Org **Risk**, **Coverage**, **Configurations**, **Campaigns** (if licensed). Walk a Configurations apply. | 90-day rollout plan: who, what, when. |
| 3:55–4:00 | — | Wrap, action items, follow-up resources | — |

**Total: 240 min** with two 15-minute breaks. Lesson 5 gets the largest slot (45 min) because authoring + running a custom query takes real time and is the most technical content of the day.
