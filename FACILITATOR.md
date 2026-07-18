# Facilitator notes

Instructor-side companion to [`README.md`](README.md). Read this once before running the workshop.

> ⚠️ This repository is **intentionally vulnerable**. Set expectations with attendees up front: every finding they see is real and demonstrates [GitHub Code Security, GitHub Secret Protection, or a related GitHub security capability](https://docs.github.com/en/code-security/getting-started/github-security-features) — the bugs and secrets are deliberate teaching aids, not mistakes.

---

## Pre-flight checklist

> 🤖 **Run [`scripts/preflight.sh`](scripts/preflight.sh) ~24 hours before the workshop.** It verifies items 1–5 of this checklist plus current alert counts via the GitHub API and returns a green/red summary. Requires `gh` authenticated with `repo` + `read:org` scopes and admin on the demo repo. The manual list below is still authoritative for items the API can't observe (UI-only custom patterns, second-tab setup).

Run through this before attendees join. None of these are reversible mid-session and most will silently break the demo if missed.

1. **Confirm Code Security and Secret Protection capabilities are on for this repo.** Repo → `Settings → Code security`. Look for green checkmarks next to *Code scanning*, *Secret scanning*, and *Dependabot alerts*. The org [`tkl-enteprises`](https://github.com/tkl-enteprises) has the required product access; new repos in the org may still need the recommended security configuration applied.
2. **Enable Dependabot alerts and security updates.** Repo → `Settings → Code security → Dependabot`. Turn on *Dependabot alerts*, *Dependabot security updates*, and *Dependabot version updates* (the last one needs the `dependabot.yml` shipped in `.github/`).
3. **Enable secret scanning + push protection.** Repo → `Settings → Code security → Secret scanning`. Turn on *Secret scanning*, *Push protection*, and *Push protection for contributors* if your org policy allows. Push protection is what makes lesson 08 land — without it, secrets only get flagged after the fact.
4. **Verify the CodeQL workflow ran at least once.** `Actions → CodeQL`. If you see a green checkmark, code scanning has a baseline. If you see nothing, push any commit (or click *Run workflow*) and wait — without that baseline, lesson 01 has nothing to show.
5. **Verify Copilot Autofix is enabled.** Repo → `Settings → Code security → Code scanning → Copilot Autofix`. This is what makes lesson 2 work; if it's off, attendees won't see the *Generate fix* button.
6. **Publish the two custom secret patterns for lesson 09.** Repo → `Settings → Code security → Secret scanning → Custom patterns → New pattern`. Lesson 09's `.github/secret_scanning.yml` was deliberately removed because that file only supports path exclusions — *not* custom-pattern definitions. Add these two by hand:
   - `Contoso API Token` → format `CONTOSO-API-[A-Z0-9]{16,}`, test string `CONTOSO-API-FAKEDEMO0123456789ABCDEF`
   - `Contoso Workshop Demo Key` → format `contoso_demo_[a-z0-9]{32}`, test string `contoso_demo_abcdef0123456789abcdef0123456789`
   Tick *Push protection* on each if you want lesson 09's optional push-block step to work. See [lesson 09 README](lessons/09-secret-protection-custom-patterns/README.md) for screenshots of the preflight.
7. **Have the org Security Overview tab open on a second tab.** [https://github.com/orgs/tkl-enteprises/security/overview](https://github.com/orgs/tkl-enteprises/security/overview) — lesson 11 is entirely UI-driven and the page can take a few seconds to load on first visit.
8. **Prepare Code Quality lessons 06–07.** Confirm Code Quality is enabled and its workflow has completed. For lesson 07, merge a workshop PR that adds or changes `ai-findings-fixtures.js` after enablement; an old default-branch file or direct push is not a reliable AI findings trigger.

## Repo configuration baseline

The repo ships with the following config applied. If you fork/copy this repo, replicate these settings:

| Setting | Value | Why |
| --- | --- | --- |
| Secret scanning | enabled | Detects Azure `AccountKey=…`, `sk_test_…`, `ghp_…`, and 200+ other partner patterns. |
| Push protection | enabled | Blocks new partner-pattern secrets at push time |
| Secret scanning AI detection | enabled | Catches generic secrets the partner patterns miss |
| Validity checks | enabled | Tags alerts as Active / Inactive |
| Non-provider patterns | enabled | Generic password/key detection |
| Dependabot alerts + security updates | enabled | Powers lesson 10 |
| CodeQL (advanced workflow) | `build-mode: none` for Python | Default setup is OFF — would conflict |
| Code Quality Standard findings (lesson 06) | enabled | Runs deterministic reliability and maintainability rules with CodeQL |
| Code Quality AI findings (lesson 07) | enabled; qualifying PR merged | Reviews recently merged default-branch files |
| Branch protection on `main` | required checks: CodeQL, Bandit, Dependency Review; admins can bypass | Keeps `main` green |
| Custom secret patterns (lesson 09) | UI-only, not in source | See lesson 09 README + preflight step 6 |

Anything in the *Settings → Code security* sidebar that's NOT in the table above is intentionally left at GitHub's default — flag in a PR if you think we should change one.

## Per-lesson timing guidance

No clock times — pace varies wildly by audience. Use these qualitative buckets when planning your agenda:

| # | Lesson | Length | Notes |
| - | ------ | ------ | ----- |
| 01 | CodeQL Code Scanning | medium | The "wow" lesson. Spend time on the alert UI, dataflow path, and severity. |
| 02 | Copilot Autofix | short | One-click suggestion → review → commit. Fast and visual. |
| 03 | Custom CodeQL Queries | long | The most technical lesson. Skip on non-engineering audiences. |
| 04 | SARIF / 3rd-party Tool Integration | medium | Show how non-GitHub scanners surface in the same UI. |
| 05 | CodeQL for GitHub Actions | medium | Review trust boundaries first; use the inert `.txt` fixtures unless working in a disposable copy. |
| 06 | Code Quality Standard findings (bonus / public preview) | short | Same CodeQL engine, reliability and maintainability rules. |
| 07 | Code Quality AI findings (bonus / public preview) | short | Post-merge contextual review; include the grammar example and explain nondeterminism. |
| 08 | Secret Scanning + Push Protection | short | Live `git push` of a fake key is the whole demo — keep it tight. |
| 09 | Custom Secret Patterns | medium | Org admins love this; ICs less so. Match to your audience. |
| 10 | Dependabot / Supply Chain (+ Malware bonus) | medium | Walk through both alerts *and* the auto-generated PRs. End with the Malware tab tour. |
| 11 | Security Overview (Org-level Governance) | short | Pure UI tour. No code. Best as a closer. |

## Common attendee gotchas

- ❌ **"My CodeQL workflow didn't run on my fork."** Workflows on forks need explicit consent — the first push from a fork triggers a *Workflow awaiting approval* state. Have attendees push to a branch on the upstream repo instead, or be ready to approve workflows from the *Actions* tab.
- ❌ **"Secret scanning isn't showing my fake key."** Three distinct causes:
  1. On the free tier, secret scanning only runs on public repos. This repo is public, so it works — but attendees re-running on a private fork without GitHub Secret Protection will see nothing.
  2. **AI-powered detection and provider denylists deliberately suppress obvious fakes** in committed history (e.g. any provider's documented canary, or any string with `FAKE`/`DEMO`/`EXAMPLE` markers — including Azure storage `AccountKey=FAKEDEMO…==` shapes). That's the feature working correctly. The reliable workshop demo is the **push protection moment** — push a *fresh* canary line in a workshop branch and watch the push get blocked. Lesson 08's README sets this expectation explicitly.
   3. **As of last verification (2026-05-06), `0` partner-pattern alerts and `0` push-protection blocks fired on this repo.** The committed Azure-shaped, FAKE-marker Stripe, and FAKE-marker GitHub PAT canaries are deliberately suppressed by AI heuristics — that's the feature, not a bug. The workshop's reliable detection moment is the live push of a fresh canary in step 2's hands-on flow. **Caveat from this verification run:** a freshly-generated partner-pattern key pushed to an ephemeral branch was *not* blocked either (push succeeded with `EXIT_CODE: 0`; see `docs/screenshots/push-protection-block.txt`, which captures the historical AWS-shaped run — the failure mode is identical for any partner pattern). Before facilitating, re-confirm push protection is *actually* enforcing in repo *Settings → Code security → Secret scanning → Push protection* (and that the `tkl-enteprises` GitHub Secret Protection access is attached) — the `secret-scanning/alerts` REST endpoint also returned `404` for a pull-only collaborator token, which is consistent with secret scanning not being active on this repo at the time of measurement.
- ❌ **"Push protection let me push my secret."** Push protection only blocks **patterns GitHub recognizes** by default. The fake Azure connection string in lesson 08 matches a partner pattern; randomly chosen strings will not. If a demo "fails," check the pattern, not the feature.
- ❌ **"Lesson 09 alerts aren't appearing."** Custom patterns are not version-controlled — they live in repo *Settings*. If you skipped step 6 of the preflight, the two custom patterns aren't published, and the demo files in lesson 09 will sit silent regardless of how long you wait.
- ❌ **"Dependabot didn't open a PR."** Dependabot security updates require the manifest file (e.g. `requirements.txt`) to be at a path Dependabot knows about. The `dependabot.yml` in `.github/` is what tells it where to look — if attendees move files around in their fork, the PRs stop.
- ❌ **"Autofix button is missing."** Either Autofix is off in repo settings, or the alert is in a language Autofix doesn't yet support. Lesson 2 picks alerts that are known-supported.
- ❌ **"Code scanning shows zero alerts."** The CodeQL workflow either hasn't finished its first run, or it ran on a branch with no vulnerable code. Check `Actions → CodeQL` first.
- ❌ **"Several 'Dependabot Updates' workflow runs show as failure."** Those red runs are Dependabot's *internal* rebase/recompute jobs, not the workshop's CI. They fire when Dependabot can't compute a clean update graph for a manifest (typically because a transitive dep also needs to move, or two PRs touch the same lockfile). They do **not** block PR creation — the seven pip-dep PRs in lesson 10 still appear, still surface their CVE annotations, and still merge correctly. Safe to ignore; do not panic-debug them mid-session.
- 🎤 **Demo optics for Microsoft FTEs — lead with Azure / Contoso fixtures.** Lesson 08's primary fixture is an Azure storage connection string (`AccountKey=FAKEDEMO…==`) and lesson 09's custom patterns use the `Contoso` prefix on purpose: every Markdown file, every code sample, every screenshot is potential customer-facing material — one stray screenshot of a competitor-shaped key on Slack from an excited customer is a bad day. GitHub Secret Protection's secret-scanning coverage is genuinely vendor-neutral (200+ partner patterns covering every major cloud and SaaS provider), so the demo translates 1:1 to any environment; we just lead with Azure-shaped fixtures in source. Vendor-neutrality lives in the *prose* (e.g. solution.md's incident-response runbook is provider-agnostic).

### Push protection bypass — mitigations for live demos

The verification run logged in [`docs/screenshots/push-protection-block.txt`](docs/screenshots/push-protection-block.txt) shows the failure mode that surprises facilitators most: **a fresh partner-pattern canary pushed by an admin pushes through cleanly with `EXIT_CODE: 0` and no block prompt**, even with push protection switched on in repo settings. (The committed transcript captures the workshop's previous AWS-first fixtures — the failure mode is pattern-agnostic; the same admin-bypass behaviour applies to the current Azure-first lesson and to lesson 09's `CONTOSO-API-…` custom pattern.)

**Root cause.** Push protection is gated by the branch ruleset's *bypass list*. On this repo (and on most repos created from GitHub's recommended security configuration) the bypass list defaults to **"Anyone with write access"** — which means every admin and every collaborator with `write` silently bypasses the block. Worse, partner patterns are filtered through **validity checks** before push protection fires; an inactive / fake-looking key can be deprioritised by the validator and never trip the block, regardless of the bypass list.

**Three mitigations**, in increasing order of facilitator effort:

1. **Option 3 — Demo with a custom secret pattern (recommended for live workshops).** Lesson 09 ships two custom patterns (`CONTOSO-API-…` and `contoso_demo_…`). Custom patterns do **not** route through validity checks, and their push-protection enforcement is per-pattern instead of governed by the partner-pattern path. Pushing a fresh `CONTOSO-API-PUSHBLOCKDEMO0123` line on a workshop branch fires the block reliably for every account, every time. **No org-settings change required**, which is why this is the default for live delivery.
   ```python
   # paste this into lessons/09-secret-protection-custom-patterns/internal.py and push
   NEW_CONTOSO_KEY = "CONTOSO-API-" + "PUSHBLOCKDEMO" + "0123"  # 28 chars, matches CONTOSO-API-[A-Z0-9]{16,}
   ```
2. **Option 2 — Temporarily restrict the bypass list.** Repo → `Settings → Rules → Rulesets → main-branch-protection` → *Bypass list*. Switch from "Anyone with write access" to "Specific roles or teams" and leave the list empty for the duration of the workshop, then revert immediately afterwards. Side effect: while the bypass list is empty, *you* also can't bypass — emergency hotfixes during the session will fail. Set a calendar reminder to revert.
3. **Option 1 — Run the demo from a non-admin account.** The most realistic reproduction of an attendee experience. Create a `workshop-attendee` user (or use a personal scratch account), invite them with `write` access only, and demo the live `git push` from *that* account. Combined with Option 2 (empty bypass list) this gives you a perfectly clean block. Requires advance setup: a separate browser profile and SSH/HTTPS credentials wired up for the demo user.

**Recommendation.** Default to **Option 3** for every delivery. Reach for Option 2 only when an attendee specifically asks "but does it block my admin too?" and you want to demonstrate the answer. Option 1 is the right path for a customer pilot — not for a 60-minute workshop where setup time is already tight.

## Reset between sessions

Several options, in order of cleanliness:

1. ✅ **Have each attendee fork the repo.** Cleanest reset. Each fork starts with its own alert state. Caveat: forks need workflows approved (see gotchas above), and secret scanning won't run on private forks without GitHub Secret Protection.
2. ✅ **Dismiss alerts as "False positive — used for testing"** between sessions. Closed alerts can be **re-opened** from the alert detail page (or via API), so this is a non-destructive reset. This is the recommended path if you're running back-to-back sessions on the same repo.
3. ⚠️ **Delete and re-create the repo.** Nuclear option. Loses any audience PRs and Dependabot history. Only do this if alerts are genuinely corrupted.

> 📝 Closed alerts re-open automatically the next time the underlying scanner re-detects the same finding (CodeQL on next workflow run, Dependabot on its next refresh, secret scanning on the next push that touches the file). You usually do not need to manually re-open anything.

## Talking points in delivery order

One paragraph per lesson, ordered as Code Security, Code Quality, Secret Protection, Supply Chain, then Governance. Use these as the verbal intro before each demo. Code Quality follows the Code Security material as the next CodeQL use case while remaining a separate product.

### 01. CodeQL Code Scanning
[CodeQL](https://codeql.github.com/) is GitHub's semantic code analysis engine. It builds a queryable database from your source and runs **dataflow queries** that follow tainted input from a *source* (e.g. an HTTP request) to a *sink* (e.g. a SQL query). Unlike regex-based linters, it understands variables, functions, and call graphs — which is why it finds real bugs and not just suspicious strings. The alerts surface in the same `Security and quality → Code scanning` tab regardless of whether they came from the default suite, a custom pack, or a third-party tool via SARIF.

### 02. Copilot Autofix
[Copilot Autofix](https://docs.github.com/en/code-security/code-scanning/managing-code-scanning-alerts/about-autofix-for-codeql-code-scanning) takes a CodeQL alert and uses an LLM grounded in the alert's dataflow path to draft a code fix as a suggestion you can commit straight from the PR review. The point isn't that the AI writes perfect code — it's that the *fix is grounded in the same dataflow analysis that found the bug*, so the suggestion is usually actually relevant. Always review before merging.

### 03. Custom CodeQL Queries
The default CodeQL suite is a starting point, not a ceiling. Security teams write **custom queries** for organization-specific patterns: deprecated internal APIs, banned functions, framework-specific anti-patterns. This lesson shows how to author a `.ql` file, run it locally with the CodeQL CLI, and ship it as part of the same code scanning workflow so its findings appear alongside the defaults.

### 04. SARIF / 3rd-party Tool Integration
[SARIF](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) is the OASIS standard format for static analysis results. Any tool that emits SARIF (Bandit, Semgrep, Trivy, vendor scanners) can upload its findings via the `github/codeql-action/upload-sarif` action and they will appear in the same `Security and quality → Code scanning` tab as CodeQL. Same triage UI, same alert lifecycle, same dismissal reasons. This Code Security lesson shows how security teams consolidate third-party findings.

### 05. CodeQL for GitHub Actions
CodeQL can analyze workflow YAML as the `actions` language. Use the inert `.yml.txt` pair to show why privileged checkout, expression-to-shell interpolation, and mutable action tags are separate trust-boundary failures. The repository's dedicated **Analyze (actions)** job uses `build-mode: none`; `security-extended` adds the medium-precision unpinned-tag query.

### 06. Code Quality Standard findings (bonus / public preview)
[GitHub Code Quality](https://github.com/tkl-enteprises/ghas-demos/security/quality) is distinct from GitHub Code Security, but its Standard findings use the same CodeQL engine with reliability and maintainability queries. Named, deterministic rules scan the default branch and pull requests, contribute to repository ratings, and can support ruleset enforcement.

### 07. Code Quality AI findings (bonus / public preview)
After a pull request is merged, Code Quality runs a second LLM-powered review over recently changed default-branch files and can report contextual issues for up to five files. The lesson fixture includes grammar, incorrect fallback, mutation, and serial-work examples. Finding count and wording are nondeterministic; an empty tab can mean no qualifying recent merge or no suggestion from the model.

### 08. Secret Scanning + Push Protection
[Secret scanning](https://docs.github.com/en/code-security/secret-scanning) looks for known credential patterns (cloud provider keys, npm tokens, Stripe keys, ~200 partner patterns). **Push protection** moves that detection *left* — it runs at `git push` time and blocks the push before the secret reaches the remote. The mental model: secret scanning is the smoke detector; push protection is the sprinkler that goes off before the fire reaches the server room.

### 09. Custom Secret Patterns
Beyond the ~200 partner patterns, GitHub Secret Protection lets org admins define **custom secret patterns** with regex + an optional pre/post-match heuristic. This is how you catch *your own* token formats — internal API keys, employee badge IDs, anything with a recognizable shape. Critically, custom patterns also participate in **push protection**, so they're enforceable, not just observable.

### 10. Dependabot / Supply Chain
[Dependabot](https://docs.github.com/en/code-security/dependabot) does three things people often conflate: **alerts** (your dependency has a known CVE), **security updates** (auto-PRs that bump the vulnerable dependency to a patched version), and **version updates** (routine bumps regardless of vulnerabilities). The dependency graph powering all three is also what feeds the [advisory database](https://github.com/advisories), which is the same data Dependabot reads. Lesson 10 also tours the **Malware** tab — the supply-chain twin of vulnerability alerts, flagging actually-malicious packages from the Advisory DB.

### 11. Security Overview (Org-level Governance)
At org scale, per-repo alert pages don't scale. The [Security Overview](https://docs.github.com/en/code-security/security-overview/about-security-overview) tab is the **CISO view**: which repos have which features enabled, where alerts are concentrating by severity, which teams own the most risk, and what *security configurations* are applied across the fleet. This is the product-adoption story — it's the difference between "we enabled Code Security and Secret Protection" and "we manage them."

## Per-lesson notes

Lessons whose demo flow needs more than the timing bucket and the talking-point paragraph go here. Lessons not listed are fully captured by their lesson README and their *Talking points per pillar* entry above.

### 02. Copilot Autofix — live walkthrough

**Why no committed screenshot.** Lesson 02 is the only lesson with no embedded image. Autofix is intrinsically interactive — the proposed fix is generated on demand inside the PR review UI, takes 10–30 seconds to render, and then needs to be discussed live (accept / edit / dismiss). A still screenshot strips out everything that makes the lesson land.

**Recommended live alert.** Use the deterministic, Autofix-supported Lesson 02
finding:

| Rule | File | Why it's a good demo |
| --- | --- | --- |
| `py/sql-injection` | `lessons/02-code-security-copilot-autofix/insecure_login.py` | The remote-input-to-SQL dataflow is short, and the expected bound-parameter fix is easy to review. |

**Demo flow** (≈ 90 seconds end to end):

1. `Security and quality → Code scanning → Alerts`. Filter to **Tool: CodeQL** and path `lessons/02-code-security-copilot-autofix`, then open the SQL-injection alert.
2. Click **Generate fix** (button label may also read *"Autofix this alert"*). Wait 10–30 seconds — narrate the suggestion preview as it loads.
3. Click **Create PR with fix**. Walk through the diff Copilot proposes — *out loud, in the PR review UI*, before merging. This is the part attendees remember.
4. Demonstrate the **edit-then-accept** flow: change one line of Copilot's diff, push to the branch, show that the alert is still resolved when CodeQL re-runs on the PR. Reinforces that Autofix is a starting point, not a rubber stamp.
5. Close with the **dismiss with reason** flow on a separate alert — shows that not every Autofix suggestion has to land.

**Availability caveat.** Copilot Autofix for code scanning does **not** require a GitHub Copilot subscription and does not consume AI credits. It is available for public repositories on GitHub.com and for qualifying private or internal repositories with GitHub Code Security. Administrators can disable it, so verify that Autofix is allowed before the workshop. Agentic autofix is different: assigning an alert to Copilot requires Copilot cloud agent access and consumes AI credits.

## Where to capture screenshots

The repo ships with a frozen set of screenshots under [`docs/screenshots/`](docs/screenshots/), captured against the live `tkl-enteprises/ghas-demos` tenant. They're already embedded in the relevant lesson READMEs and the root README, so attendees see the same UI in markdown that you'll demo live. Re-capture against your own tenant before a deck — the `tkl-enteprises` images are workshop-grade, not customer-deck-grade.

| File | Lesson | Shows |
| --- | --- | --- |
| [`docs/screenshots/00-security-overview.png`](docs/screenshots/00-security-overview.png) | (root README hero) | Repo `Security and quality` tab landing page — alert counts across Code scanning, Secret scanning, and Dependabot. |
| [`docs/screenshots/01-code-scanning-alerts.png`](docs/screenshots/01-code-scanning-alerts.png) | 01 — CodeQL Code Scanning | Code-scanning alerts list filtered to **Tool: CodeQL**. |
| [`docs/screenshots/01-codeql-alert-detail.png`](docs/screenshots/01-codeql-alert-detail.png) | 01 — CodeQL Code Scanning | Alert detail page (SSTI) with the dataflow path expanded — source → sink hops visible. |
| [`docs/screenshots/04-actions-tab.png`](docs/screenshots/04-actions-tab.png) | 04 — SARIF Integration | Repo `Actions` tab showing CodeQL, Bandit-SARIF, Dependency review, and Dependabot Updates workflows green. |
| [`docs/screenshots/04-bandit-sarif-findings.png`](docs/screenshots/04-bandit-sarif-findings.png) | 04 — SARIF Integration | Code-scanning alerts filtered to **Tool: Bandit** — B303, B301, B307, B602/B603, B608, B101/B105/B107. |
| [`docs/screenshots/security-overview-with-code-quality.png`](docs/screenshots/security-overview-with-code-quality.png) | 06 — Code Quality Standard findings | Preview-era organization view listing Code Quality among enabled features. |
| [`docs/screenshots/08-push-protection-settings.png`](docs/screenshots/08-push-protection-settings.png) | 08 — Secret Scanning + Push Protection | Repo `Settings → Code security → Secret scanning` showing the push-protection toggle on. |
| [`docs/screenshots/08-secret-scanning-default-empty.png`](docs/screenshots/08-secret-scanning-default-empty.png) | 08 — Secret Scanning + Push Protection | `Security and quality → Secret scanning` **Default** tab showing "No secrets found" — illustrates AI suppression on committed canaries. |
| [`docs/screenshots/09-secret-scanning-generic-ai.png`](docs/screenshots/09-secret-scanning-generic-ai.png) | 08 + 09 — Secret scanning / Custom patterns | `Security and quality → Secret scanning` **Generic** tab — the AI classifier firing on `hunter2_FAKE_*`-style password assignments. |
| [`docs/screenshots/push-protection-block.txt`](docs/screenshots/push-protection-block.txt) | 08 — Secret Scanning + Push Protection | **Historical artifact** — verbatim terminal capture from the 2026-05-06 verification run against the workshop's *previous* AWS-first fixtures. **OBSERVED:** push protection did **not** block a fresh `AKIA…` canary on the ephemeral branch (`EXIT_CODE: 0`). The lesson's current Azure-first / Contoso fixtures behave the same way for the same root cause (admin bypass list + validity-check deprioritisation); we keep the historical evidence intact rather than re-recording. Re-verify enforcement before each delivery — see *Common attendee gotchas* and *Push protection bypass — mitigations for live demos* above for context. |
| [`docs/screenshots/10-dependabot-alerts.png`](docs/screenshots/10-dependabot-alerts.png) | 10 — Dependabot / Supply Chain | `Security and quality → Dependabot` alerts list across Flask, Jinja2, Werkzeug, urllib3, requests, PyYAML, cryptography. |
| [`docs/screenshots/10-dependabot-prs-list.png`](docs/screenshots/10-dependabot-prs-list.png) | 10 — Dependabot / Supply Chain | Pull requests tab filtered to `app/dependabot` — the seven open pip security-update PRs. |
| [`docs/screenshots/10-dependabot-pr-detail.png`](docs/screenshots/10-dependabot-pr-detail.png) | 10 — Dependabot / Supply Chain | A Flask-bump security-update PR with CVE annotation, severity badge, release notes, and compatibility score. |
| [`docs/screenshots/11-org-security-overview-risk.png`](docs/screenshots/11-org-security-overview-risk.png) | 11 — Security Overview | Org-level **Risk** view — open alerts by severity and repo. |
| [`docs/screenshots/11-org-security-overview-coverage.png`](docs/screenshots/11-org-security-overview-coverage.png) | 11 — Security Overview | Org-level **Coverage** view — per-repo enablement of CodeQL / Dependabot / secret scanning / push protection. |

Gaps still worth capturing live in your tenant for a follow-up deck:

- 📸 Lesson 02 — the **Copilot Autofix** suggestion diff (before / after acceptance) on the `py/sql-injection` alert in `insecure_login.py`.
- 📸 Lesson 03 — the code-scanning list and alert detail for `py/tkl/putin-khuylo-false`; the previous `DEBUG = True` captures were removed when the example changed.
- 📸 Lesson 11 — the **Configurations** page showing the `GitHub recommended` security configuration's feature toggles.
- 📸 Lesson 11 — a **Security campaigns** detail page (paid feature) with assigned repos and progress bars.

## Code Quality after Code Security

→ See [lesson 06](lessons/06-code-quality-standard-findings/) for deterministic CodeQL analysis and [lesson 07](lessons/07-code-quality-ai-findings/) for the post-merge AI walkthrough.

- **Same engine, different queries.** [GitHub Code Quality](https://github.com/tkl-enteprises/ghas-demos/security/quality) is distinct from GitHub Code Security and GitHub Secret Protection, but it runs on the same CodeQL engine. Maintainability and reliability queries replace the security-focused taint / SQLi / SSRF set.
- **Status:** **Public preview** in the July 2026 documentation; scheduled to become generally available on **July 20, 2026**.
- **Billing:** during preview, scans consume **GitHub Actions minutes**, but active-committer and AI-credit usage is not billed. From GA, costs can include Actions minutes, AI credits, and active-committer licenses. See [GitHub Code Quality billing](https://docs.github.com/en/billing/concepts/product-billing/github-code-quality).
- **Enforcement:** Code Quality supports rulesets that can block changes which miss configured quality standards or code-coverage thresholds. Push protection remains a Secret Protection capability, not a quality control.
- **Teaching contrast.** Standard findings use named CodeQL rules; AI findings are a second contextual scan after merge. Show them as separate lessons.
- **When to skip.** CISO briefings or pure-security audiences — drop it. The 60-min and 2-hour agendas skip it; whenever it is included, place it immediately after the Code Security block so the shared CodeQL engine is clear.

## Sample agendas

Three pre-built agendas. Pick one based on audience size, audience role, and the room you've been given. Total times below assume the [Pre-flight checklist](#pre-flight-checklist) has already been run and the repo is in a known-good state — they do **not** include setup time on the day.

### 60-minute executive overview (lessons 01, 08, 10, 11)

For C-suite, security leadership, or non-technical buyers. Uses one lesson from each security-focused pillar and skips the deeper technical and Code Quality material. Goal: leave the room knowing GitHub Code Security and GitHub Secret Protection cover code bugs and leaked secrets, GitHub's supply-chain features identify vulnerable dependencies, and there's a single org-level cockpit for all three.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:05 | — | Welcome + repo tour (`README.md` only) | Set expectations: repo is *intentionally* vulnerable; every alert is real. |
| 0:05–0:15 | 01 — CodeQL | Open alert #21 (SSTI). Walk the dataflow path source → sink. | Where does this fit in the SDLC? What changes if a developer never opens the PR? |
| 0:15–0:25 | 08 — Secret Scanning | Live `git push` of a fresh `CONTOSO-API-…` line on a workshop branch (custom pattern from lesson 09 — see *Push protection bypass* mitigations above). | What's our current MTTR on a leaked production secret? |
| 0:25–0:35 | 10 — Dependabot | Show the seven open pip security-update PRs. Open one and walk the CVE annotation. Tour the empty Malware tab. | Who owns merging these today? How long do they sit? |
| 0:35–0:50 | 11 — Security Overview | Org-level **Risk** + **Coverage** views. Highlight enablement gaps. | Which 5 repos do we turn this on next? Who signs off? |
| 0:50–1:00 | — | Q&A + close | Action items: pick the next 5 repos; assign an owner. |

**Total: 60 min.** ⚠️ The lesson-08 demo *must* use the lesson-09 custom pattern — partner-pattern push protection silently bypasses for admins (see mitigation note above).

### 2-hour developer enablement (lessons 01, 02, 04, 08, 09, 10, 11)

For platform / appsec / senior dev audiences who own day-to-day triage. Covers seven foundational lessons in delivery order; deliberately skips lesson 03 (custom CodeQL queries) and optional/advanced lessons 05, 06, and 07 — they'll crowd out hands-on triage in this format. Goal: every attendee leaves able to triage an alert, push past a custom-pattern block, and read a SARIF upload.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:10 | — | Repo tour + workshop pillar map (root README) | Today's three pillars: code, secrets, supply chain. |
| 0:10–0:25 | 01 — CodeQL | Alerts list → alert detail → dataflow. Triage one alert as "won't fix" with reason. | When should you mark something `won't fix` vs `false positive`? |
| 0:25–0:35 | 02 — Copilot Autofix | Generate-fix on alert #21 or #28. Edit-then-accept the diff. | When *not* to trust Autofix? What's your code-review SLA? |
| 0:35–0:50 | 04 — SARIF | Code-scanning alerts → filter Tool: Bandit. Show the same triage UI as CodeQL. | Which third-party scanners do we want in this view? |
| 0:50–1:00 | — | Code Security recap | How do CodeQL, Autofix, and third-party SARIF findings share a triage model? |
| 1:00–1:10 | — | ☕ Break | — |
| 1:10–1:25 | 08 — Secret Scanning | Live custom-pattern push protection block (see lesson 09). Show the secret-scanning Default + Generic tabs. | Why doesn't the Azure storage canary block? (Validity checks + bypass list — same root cause that suppresses the historical canary capture.) |
| 1:25–1:35 | 09 — Custom Patterns | Settings → Secret scanning → Custom patterns. Walk the two `Contoso …` patterns (pre-published per pre-flight step 6). Push a fresh `contoso_demo_…` and watch it block. | What internal token shapes belong here? (Badge IDs, internal API keys, vendor IDs.) |
| 1:35–1:45 | 10 — Dependabot | PR list filter `app/dependabot`. Walk one PR; mention the red "Dependabot Updates" runs are internal rebase jobs (gotchas). Tour Malware tab. | Auto-merge policy: green CI + Dependabot? Where's the line? |
| 1:45–1:55 | 11 — Security Overview | Org **Risk** + **Coverage** + Configurations. | Coverage gap → action plan. |
| 1:55–2:00 | — | Q&A + close | — |

**Total: 120 min.** Plan one ☕ break at the 1:00 mark to keep energy up.

### Half-day deep dive (all 11 lessons)

For mixed appsec + platform engineering audiences who want the full toolkit — including authoring custom CodeQL queries. 4 hours with two breaks. Goal: every attendee can walk away and stand this up on their own repo on Monday.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:15 | — | Welcome, repo tour, pre-flight walkthrough (`scripts/preflight.sh`) | What does enabling Code Security and Secret Protection actually mean? Five toggles. |
| 0:15–0:35 | 01 — CodeQL | Full triage flow on alert #21: detail → dataflow → close as fixed via PR. | When CodeQL is wrong: investigation flow + dismissal reasons. |
| 0:35–0:45 | 02 — Copilot Autofix | Autofix on alert #21. Edit-then-accept. | Where Autofix earns its keep; where it doesn't. |
| 0:45–1:15 | 03 — Custom CodeQL | Read and run `py/tkl/putin-khuylo-false`; show the finding on `noncompliant.py` and explain the Terraform/HCL extractor boundary. | Custom query vs. lint rule? |
| 1:15–1:30 | 04 — SARIF | Bandit upload → unified code-scanning view. | Which scanners stay? |
| 1:30–1:40 | 05 — Actions scanning | Compare the inert vulnerable and remediated workflow fixtures; show **Analyze (actions)**. | Where do workflow privileges cross trust boundaries? |
| 1:40–1:55 | — | ☕ Break | — |
| 1:55–2:10 | 06 — Code Quality Standard findings | Review deterministic findings, ratings, PR feedback, and ruleset options. | Would your team gate merges on quality? |
| 2:10–2:25 | 07 — Code Quality AI findings | Review the recent-merge grammar and contextual suggestions. | How should nondeterministic suggestions be governed? |
| 2:25–2:40 | 08 — Secret Scanning | Custom-pattern push block; show the validity-check distinction. | Leaks in commits vs CI logs vs images. |
| 2:40–3:00 | 09 — Custom Patterns | Walk the Contoso patterns and push-block a fresh demo value. | Pattern hygiene and false positives. |
| 3:00–3:15 | 10 — Dependabot (+ Malware) | Alerts → update PR → CVSS/EPSS; tour Malware. | Dependabot vs reachability. |
| 3:15–3:30 | — | ☕ Break | — |
| 3:30–3:50 | 11 — Security Overview | Org **Risk**, **Coverage**, **Configurations**, and **Campaigns** if available. | 90-day rollout plan. |
| 3:50–4:00 | — | Wrap, action items, follow-up resources | — |

**Total: 240 min** with two 15-minute breaks. Lesson 03 gets the largest slot because authoring and running a custom query is the most technical content. Lesson 07 requires a pull request merged after Code Quality was enabled; prepare that qualifying merge before the workshop.
