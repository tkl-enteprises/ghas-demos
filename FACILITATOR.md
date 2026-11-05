# Facilitator notes

Instructor-side companion to [`README.md`](README.md). Read this once before running the workshop.

> ⚠️ This repository is **intentionally vulnerable**. Set expectations with attendees up front: every finding they see is real and demonstrates [GitHub Code Security, GitHub Secret Protection, or a related GitHub security capability](https://docs.github.com/en/code-security/getting-started/github-security-features) — the bugs and secrets are deliberate teaching aids, not mistakes.

---

## Pre-flight checklist

> 🤖 **Run [`scripts/preflight.sh`](scripts/preflight.sh) ~24 hours before the workshop.** It verifies items 1–5 of this checklist, current alert counts, and — through [`scripts/demo-health.py`](scripts/demo-health.py) — that every intentional lesson finding in [`scripts/expected-alerts.json`](scripts/expected-alerts.json) is still open on `main`. Requires `gh` authenticated with `repo` + `read:org` scopes and admin on the demo repo. The manual list below is still authoritative for items the API can't observe (UI-only custom patterns, second-tab setup).

Run through this before attendees join. None of these are reversible mid-session and most will silently break the demo if missed.

1. **Confirm Code Security and Secret Protection capabilities are on for this repo.** Repo → `Settings → Advanced Security`. Look for green checkmarks next to *Code scanning*, *Secret scanning*, and *Dependabot alerts*. The org [`tkl-enteprises`](https://github.com/tkl-enteprises) has the required product access; new repos in the org may still need the recommended security configuration applied.
2. **Enable Dependabot alerts and security updates.** Repo → `Settings → Advanced Security → Dependabot`. Turn on *Dependabot alerts*, *Dependabot security updates*, and *Dependabot version updates* (the last one needs the `dependabot.yml` shipped in `.github/`).
3. **Enable secret scanning + push protection.** Repo → `Settings → Advanced Security → Secret Protection`. Turn on *Secret scanning* and *Push protection*. Push protection is what makes lesson 08 land — without it, secrets only get flagged after the fact. Check *Who can bypass push protection* and make sure the presenter's account is **not an exempt actor**: exempt pushes skip push protection entirely, so your live block would silently not happen.
4. **Verify the CodeQL workflow ran at least once.** `Actions → CodeQL`. If you see a green checkmark, code scanning has a baseline. If you see nothing, push any commit (or click *Run workflow*) and wait — without that baseline, lesson 01 has nothing to show.
5. **Verify Copilot Autofix is enabled, and decide on agentic autofix.** Repo → `Settings → Advanced Security → Code scanning`. Copilot Autofix is what makes lesson 02 work; if it's off, attendees won't see the *Generate fix* button. If agentic autofix (GA October 15, 2026) is enabled for the repository or inherited from the organization, *Generate fix* is replaced by *Assign to Copilot*, and each assignment consumes Code Security AI credits — choose which flow lesson 02 shows.
6. **Publish the two custom secret patterns for lesson 09.** Repo → `Settings → Advanced Security → Secret Protection → Custom patterns → New pattern`. Lesson 09's `.github/secret_scanning.yml` was deliberately removed because that file only supports path exclusions — *not* custom-pattern definitions. Add these two by hand:
   - `Contoso API Token` → format `CONTOSO-API-[A-Z0-9]{16,}`, test string `CONTOSO-API-FAKEDEMO0123456789ABCDEF`
   - `Contoso Workshop Demo Key` → format `contoso_demo_[a-z0-9]{32}`, test string `contoso_demo_abcdef0123456789abcdef0123456789`
   Enable *Push protection* on each after publishing. Lesson 08's live block uses the `Contoso API Token` pattern, so this step is required for the most reliable demo. See [lesson 09 README](lessons/09-secret-protection-custom-patterns/README.md) for the AI-candidate and dry-run flow.
7. **Have the org Security Overview tab open on a second tab.** [https://github.com/orgs/tkl-enteprises/security/overview](https://github.com/orgs/tkl-enteprises/security/overview) — lesson 11 is entirely UI-driven and the page can take a few seconds to load on first visit.
8. **Prepare Code Quality lessons 06–07.** Confirm Code Quality is enabled and its workflow has completed. For lesson 07, merge a workshop PR that adds or changes `ai-findings-fixtures.js` after enablement; an old default-branch file or direct push is not a reliable AI findings trigger.
9. **Check that the last session left no fixes or secrets behind.** Run `python -m pytest tests/`: the fixture guards fail if a merged Autofix or Copilot PR removed a planted vulnerability, or if a live push-protection demo left a real token in `.env`/`.env.example`. Also check that the **Demo health** workflow's *Intentional lesson findings* row is green.
10. **Close stale demo PRs without merging.** Copilot, Autofix, and Dependabot PRs against the lesson fixtures should never land on `main` (see *Reset between sessions*).

## Repo configuration baseline

The repo ships with the following config applied. If you fork/copy this repo, replicate these settings:

| Setting | Value | Why |
| --- | --- | --- |
| Secret scanning | enabled | Detects Azure `AccountKey=…`, `sk_test_…`, `ghp_…`, and 500+ other secret types from 200+ providers. |
| Push protection | enabled; default bypass (anyone with write access, with a reason) | Blocks new secrets from push-protected patterns. Never make the presenter an exempt actor. |
| AI-detected secrets (API field `secret_scanning_ai_detection`) | enabled | Catches passwords and other unstructured secrets that patterns miss. Renamed from *Copilot secret scanning* in July 2026. |
| Validity checks | enabled | Tags alerts as Active / Inactive |
| Generic patterns (API field `secret_scanning_non_provider_patterns`) | enabled | Private keys, connection strings, and other secrets without a provider format. Renamed from *non-provider patterns* in July 2026. |
| Dependabot alerts + security updates | enabled | Powers lesson 10 |
| CodeQL (advanced workflow) | `build-mode: none` for Python; separate `actions` job | Default setup is OFF — would conflict |
| Copilot Autofix | enabled (default) | Lesson 02's *Generate fix*. Agentic autofix replaces that button when enabled. |
| Code Quality Standard findings (lesson 06) | enabled | Runs deterministic reliability and maintainability rules with CodeQL |
| Code Quality AI findings (lesson 07) | enabled; qualifying PR merged | Reviews recently merged default-branch files |
| Branch protection on `main` | required checks: CodeQL, Bandit, Dependency Review; admins can bypass | Keeps `main` green |
| Custom secret patterns (lesson 09) | UI-only, not in source | See lesson 09 README + preflight step 6 |

Anything in the *Settings → Advanced Security* page that's NOT in the table above is intentionally left at GitHub's default — flag in a PR if you think we should change one.

## Product changes since the July 2026 refresh

Verified against the GitHub changelog and docs on November 5, 2026. The lessons already reflect these; use the table to brief co-facilitators.

| Date | Change | Lessons |
| --- | --- | --- |
| Jun 18, 2026 (backport Jul 20) | [`actions/checkout` v7 refuses fork PR checkouts](https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout) in `pull_request_target` and `workflow_run`; floating major tags such as `@v4` got the backport, SHA pins did not. | 05 |
| Jul 10, 2026 | [Detector renames](https://github.blog/changelog/2026-07-10-clearer-names-for-secret-scanning-detector-types/): *Copilot secret scanning* → **AI-detected secrets**; *non-provider patterns* → **generic patterns**. | 08, 09 |
| Jul 13, 2026 | [Custom patterns REST API](https://github.blog/changelog/2026-07-13-create-and-manage-secret-scanning-custom-patterns-via-rest-api/) is GA; dry run and publishing still happen in the UI. | 09 |
| Jul 14, 2026 | [Dependabot version updates wait a default 3-day cooldown](https://github.blog/changelog/2026-07-14-dependabot-version-updates-introduce-default-package-cooldown/); security updates are not delayed. | 10 |
| Jul 20, 2026 | [GitHub Code Quality is GA](https://github.blog/changelog/2026-07-20-github-code-quality-is-now-generally-available/): $10 per active committer plus AI credits and Actions minutes; *ratings* are now *scores*; AI findings stay in public preview. | 06, 07 |
| Jul 28, 2026 | [Malware alerts expand beyond npm](https://github.blog/changelog/2026-07-28-dependabot-alerts-on-malicious-packages-across-more-ecosystems/) to PyPI and more via OpenSSF advisories. | 10 |
| Aug 4, 2026 | [Default setup accepts a CodeQL config file](https://github.blog/changelog/2026-08-04-customize-code-scanning-default-setup-at-scale/) through the `github-codeql-config-file` repository property. | 03 |
| Aug 20, 2026 | [New code scanning dismissal reason *Mitigated*](https://github.blog/changelog/2026-08-20-code-scanning-adds-a-mitigated-alert-dismissal-reason). | 01 |
| Sep 9, 2026 | [Ruleset rule *Require secret scanning alerts are resolved*](https://github.blog/changelog/2026-09-09-block-pull-requests-with-exposed-secrets-from-merging) blocks merges (public preview). | 08 |
| Oct 15, 2026 | [Agentic autofix is GA](https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability/); when enabled it replaces *Generate fix* with *Assign to Copilot* and consumes Code Security AI credits. | 01, 02, 11 |
| Oct 28, 2026 | [Push protection for AI-detected secrets](https://github.blog/changelog/2026-10-28-push-protection-beyond-predefined-secret-patterns/) (public preview, AI credits). | 08 |
| Oct 28, 2026 | [Workflow lockfiles are GA](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/) (`gh actions-lock`, *Require lockfile* policy); CodeQL's `actions/unpinned-tag` honors them. | 05 |
| Oct 28, 2026 | [Dependabot reachability analysis](https://github.blog/changelog/2026-10-28-prioritize-dependabot-alerts-with-reachability-analysis) (public preview, JavaScript/TypeScript only). | 10 |
| Nov 2, 2026 | [`pull_request_target` blocked by default in public repositories from Dec 2, 2026](https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2/); brownouts Nov 9 and 16, 16:00–18:00 UTC. | 05 |
| Nov 2, 2026 | [Risk assessments show protected vs. unprotected repositories](https://github.blog/changelog/2026-11-02-security-risk-assessments-include-repository-protection-status/). | 11 |

## Per-lesson timing guidance

No clock times — pace varies wildly by audience. Use these qualitative buckets when planning your agenda:

| # | Lesson | Length | Notes |
| - | ------ | ------ | ----- |
| 01 | CodeQL Code Scanning | medium | The "wow" lesson. Spend time on the alert UI, dataflow path, and severity. |
| 02 | Copilot Autofix | short | One-click suggestion → review → commit. Fast and visual. |
| 03 | Custom CodeQL Queries | long | The most technical lesson. Skip on non-engineering audiences. |
| 04 | SARIF / 3rd-party Tool Integration | medium | Show how non-GitHub scanners surface in the same UI. |
| 05 | CodeQL for GitHub Actions | medium | Review trust boundaries first; use the inert `.txt` fixtures unless working in a disposable copy. |
| 06 | Code Quality Standard findings (optional) | short | Same CodeQL engine, reliability and maintainability rules. Code Quality is GA since July 20, 2026. |
| 07 | Code Quality AI findings (optional; public preview) | short | Post-merge contextual review; include the grammar example and explain nondeterminism. |
| 08 | Secret Scanning + Push Protection | short | Live `git push` of a fake key is the whole demo — keep it tight. |
| 09 | Custom Secret Patterns | medium | Org admins love this; ICs less so. Match to your audience. |
| 10 | Dependabot / Supply Chain (+ Malware bonus) | medium | Walk through both alerts *and* the auto-generated PRs. End with the `requestsa` malware alert. |
| 11 | Security Overview (Org-level Governance) | short | Pure UI tour. No code. Best as a closer. |

## Common attendee gotchas

- ❌ **"My CodeQL workflow didn't run on my fork."** Workflows on forks need explicit consent — the first push from a fork triggers a *Workflow awaiting approval* state. Have attendees push to a branch on the upstream repo instead, or be ready to approve workflows from the *Actions* tab.
- ❌ **"Secret scanning isn't showing my fake key."** Three distinct causes:
  1. On the free tier, secret scanning only runs on public repos. This repo is public, so it works — but attendees re-running on a private fork without GitHub Secret Protection will see nothing.
  2. **Deliberately fake fixtures may not alert.** Provider patterns combine regular expressions with additional checks such as entropy analysis, so low-entropy values that spell `FAKE`/`DEMO` (including the Azure storage `AccountKey=FAKEDEMO…==` shape) may produce no provider alert. That is expected and safer than committing a live credential. The reliable workshop moment is the **push protection block** with the lesson 09 custom pattern — see lesson 08's *Push protection demo*.
  3. **Current state (verified November 2026).** This repository does have open secret scanning alerts: GitHub PAT alerts left by earlier live demos (marked *push protection bypassed*) and `Contoso` custom-pattern alerts. The committed `FAKE` fixtures still produce no provider alerts. The May 2026 run recorded in `docs/screenshots/push-protection-block.txt`, where a fresh key was not blocked, is explained under *Push protection — what actually controls a block* below.
- ❌ **"Push protection let me push my secret."** Push protection blocks only a subset of the most identifiable patterns, plus custom patterns where you enabled it. A push also goes through when repository push protection is off, the pattern is excluded by an organization or enterprise setting, the pusher is an **exempt actor**, the push is very large (more than 1,000 existing secrets, or more than 50 MB to a public repository), or the scan times out. Low-entropy demo values can fail pattern checks. A *bypass*, by contrast, is never silent: it needs a reason and creates an alert. If a demo "fails," check the pattern and the exemption list, not the feature.
- ❌ **"Lesson 09 alerts aren't appearing."** Custom patterns are not version-controlled — they live in repo *Settings*. If you skipped step 6 of the preflight, the two custom patterns aren't published, and the demo files in lesson 09 will sit silent regardless of how long you wait.
- ❌ **"Dependabot didn't open a PR."** Dependabot security updates require the manifest file (e.g. `requirements.txt`) to be at a path Dependabot knows about. The `dependabot.yml` in `.github/` is what tells it where to look — if attendees move files around in their fork, the PRs stop.
- ❌ **"Autofix button is missing."** Either Autofix is off in repo settings, the alert is in a language Autofix doesn't yet support, or agentic autofix is enabled and has replaced *Generate fix* with *Assign to Copilot*. Lesson 02 picks an alert that is known to be supported.
- ❌ **"Code scanning shows zero alerts."** The CodeQL workflow either hasn't finished its first run, or it ran on a branch with no vulnerable code. Check `Actions → CodeQL` first.
- ❌ **"Several 'Dependabot Updates' workflow runs show as failure."** Until November 2026 every weekly run named `pip in /lessons/04-code-security-sarif-integration` failed, because that `dependabot.yml` entry pointed at a folder with no manifest. The folder now has a `requirements.txt` holding the Bandit version used by the SARIF workflow, and a test fails if any pip entry lacks a manifest. If red runs reappear, read the run name first: it says which ecosystem and directory failed.
- ❌ **"Copilot opened a PR that fixes the demo."** Copilot coding agent and Autofix PRs against the lesson fixtures (for example *Fix SQL injection in vulnerable_app.py* or *add `@admin_required` to `export_users`*) are expected during lessons 01–03 — and must not be merged. The `tests` check fails on such PRs with an explanation. If one was merged, revert it; that is exactly what removed lesson 01's `lookup_user` SQL injection in July 2026.
- 🎤 **Demo optics for Microsoft FTEs — lead with Azure / Contoso fixtures.** Lesson 08's primary fixture is an Azure storage connection string (`AccountKey=FAKEDEMO…==`) and lesson 09's custom patterns use the `Contoso` prefix on purpose: every Markdown file, every code sample, every screenshot is potential customer-facing material — one stray screenshot of a competitor-shaped key on Slack from an excited customer is a bad day. GitHub Secret Protection's secret-scanning coverage is genuinely vendor-neutral (500+ secret types from 200+ providers covering every major cloud and SaaS vendor), so the demo translates 1:1 to any environment; we just lead with Azure-shaped fixtures in source. Vendor-neutrality lives in the *prose* (e.g. solution.md's incident-response runbook is provider-agnostic).

### Push protection — what actually controls a block

The May 2026 run in [`docs/screenshots/push-protection-block.txt`](docs/screenshots/push-protection-block.txt) recorded a fresh partner-pattern canary pushing through with `EXIT_CODE: 0`. Earlier versions of this guide blamed a branch-ruleset bypass list and validity checks. Neither is how push protection works, and the cause of that run was never confirmed. By July 2026 push protection was demonstrably blocking on this repository: real GitHub tokens pushed through the web editor were blocked and then bypassed, which left alerts marked *push protection bypassed*.

What is actually true (GitHub Docs, verified November 2026):

- **Who can bypass is a security setting, not a ruleset.** By default anyone with write access can bypass a block by choosing a reason. Every bypass creates an alert, an audit-log event, and an email to watchers — it is never silent. *Delegated bypass* (repo `Settings → Advanced Security`, or *Bypass privileges* in a security configuration) restricts who may bypass and adds a request-and-approve flow.
- **Exemption is different from bypass.** An exempt actor's pushes skip push protection entirely: no block, no request. Configurable from repository settings since March 2026. Check that the presenter isn't exempt.
- **Validity checks don't gate blocking.** They label alerts *Active*/*Inactive*; they don't decide whether a push is rejected.
- **Coverage is a subset.** Push protection blocks the most identifiable patterns, and patterns include entropy checks, so low-entropy fake values may not block.

**Recommended live demo.** Use the `Contoso API Token` custom pattern (preflight item 6, with push protection enabled) on a throwaway branch. Secret scanning reads raw text, so write the value out in full. A split literal such as `"CONTOSO-API-" + "PUSHBLOCKDEMO"` never matches. This one-liner joins it at run time so this guide doesn't trip the pattern itself:

```bash
git switch -c test-push-protection-ephemeral
printf 'NEW_CONTOSO_KEY = "%s%s"\n' 'CONTOSO-API-' 'PUSHBLOCKDEMO0123' \
  >> lessons/09-secret-protection-custom-patterns/internal.py
git commit -am "test push protection" && git push -u origin test-push-protection-ephemeral
```

**Optional extras.** To show the approval workflow, set *Who can bypass push protection* to specific roles or teams and push from a write-only account, then review the request under *Security and quality → Requests*. To show the merge-time backstop, describe the public-preview ruleset rule *Require secret scanning alerts are resolved* (lesson 08). Restore the bypass setting after the session.

## Reset between sessions

Live demos change real repository state. After every delivery:

1. **Close demo PRs without merging.** Autofix (*Create PR with fix*), agentic autofix or Copilot coding agent PRs, push-protection test branches, and any "test dependency review" PRs. If a fix was merged, revert it — the `tests` check names the lesson whose planted vulnerability disappeared, and the next CodeQL run reopens the fixed alert.
2. **Revoke real credentials first.** If a real token was pushed and bypassed during the secret-scanning demo, revoke it at the issuer, remove the file or value via PR, and close the alert as *Revoked*. `.env` is gitignored for a reason; the tests fail while a `.env` file is tracked or `.env.example` holds a value.
3. **Reopen dismissed alerts.** Dismissals persist across scans — a dismissed alert does *not* reopen when the scanner finds the same issue again. Reopen anything attendees dismissed (alert page → *Reopen*, or `gh api -X PATCH repos/tkl-enteprises/ghas-demos/code-scanning/alerts/NUMBER -f state=open`). Only *fixed* code scanning alerts reopen automatically, when the vulnerable code comes back.
4. **Run the checks.** `python -m pytest tests/` locally, then `scripts/preflight.sh`, which also runs `scripts/demo-health.py` against the live repository.

For back-to-back cohorts, having each attendee fork the repository is still the cleanest isolation. Forks need workflows approved, and secret scanning won't run on private forks without GitHub Secret Protection.

## Talking points in delivery order

One paragraph per lesson, ordered as Code Security, Code Quality, Secret Protection, Supply Chain, then Governance. Use these as the verbal intro before each demo. Code Quality follows the Code Security material as the next CodeQL use case while remaining a separate product.

### 01. CodeQL Code Scanning
[CodeQL](https://codeql.github.com/) is GitHub's semantic code analysis engine. It builds a queryable database from your source and runs **dataflow queries** that follow tainted input from a *source* (e.g. an HTTP request) to a *sink* (e.g. a SQL query). Unlike regex-based linters, it understands variables, functions, and call graphs — which is why it finds real bugs and not just suspicious strings. The alerts surface in the same `Security and quality → Code scanning` tab regardless of whether they came from the default suite, a custom pack, or a third-party tool via SARIF.

### 02. Copilot Autofix
[Copilot Autofix](https://docs.github.com/en/code-security/concepts/code-scanning/autofix-for-code-scanning) takes a CodeQL alert and uses an LLM grounded in the alert's dataflow path to draft a code fix as a suggestion you can commit straight from the PR review. The point isn't that the AI writes perfect code — it's that the *fix is grounded in the same dataflow analysis that found the bug*, so the suggestion is usually actually relevant. Since October 2026, **agentic autofix** (GA) goes further: assign an alert to Copilot and it explores the codebase, reruns CodeQL to validate its fix, and opens a draft PR — at the cost of AI credits. Always review before merging.

### 03. Custom CodeQL Queries
The default CodeQL suite is a starting point, not a ceiling. Security teams write **custom queries** for organization-specific patterns: deprecated internal APIs, banned functions, framework-specific anti-patterns. The lesson's example is an authorization convention no default query can know: every Flask route under `/admin` must use the `@admin_required` decorator. This lesson shows how to author a `.ql` file, run it locally with the CodeQL CLI, and ship it as part of the same code scanning workflow so its findings appear alongside the defaults.

### 04. SARIF / 3rd-party Tool Integration
[SARIF](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) is the OASIS standard format for static analysis results. Any tool that emits SARIF (Bandit, Semgrep, Trivy, vendor scanners) can upload its findings via the `github/codeql-action/upload-sarif` action and they will appear in the same `Security and quality → Code scanning` tab as CodeQL. Same triage UI, same alert lifecycle, same dismissal reasons. This Code Security lesson shows how security teams consolidate third-party findings.

### 05. CodeQL for GitHub Actions
CodeQL can analyze workflow YAML as the `actions` language. Use the inert `.yml.txt` pair to show why privileged checkout, expression-to-shell interpolation, and mutable action tags are separate trust-boundary failures. The repository's dedicated **Analyze (actions)** job uses `build-mode: none`; `security-extended` adds the medium-precision unpinned-tag query. Close with 2026's platform changes: `actions/checkout` v7 refuses fork checkouts in `pull_request_target`, public repositories block that trigger by default from December 2, 2026, and workflow lockfiles are GA.

### 06. Code Quality Standard findings (optional)
[GitHub Code Quality](https://github.com/tkl-enteprises/ghas-demos/security/quality) is distinct from GitHub Code Security, but its Standard findings use the same CodeQL engine with reliability and maintainability queries. Named, deterministic rules scan the default branch and pull requests, contribute to repository scores, and can support ruleset enforcement. Generally available since July 20, 2026.

### 07. Code Quality AI findings (optional; public preview)
After a pull request is merged, Code Quality runs a second LLM-powered review over recently changed default-branch files and can report up to 5 findings per file in up to 5 files. This part of Code Quality is still a public preview. The lesson fixture includes grammar, incorrect fallback, mutation, and serial-work examples. Finding count and wording are nondeterministic; an empty tab can mean no qualifying recent merge or no suggestion from the model.

### 08. Secret Scanning + Push Protection
[Secret scanning](https://docs.github.com/en/code-security/secret-scanning) looks for known credential patterns (500+ secret types from 200+ providers: cloud keys, npm tokens, Stripe keys) plus generic patterns and AI-detected secrets such as passwords. **Push protection** moves that detection *left* — it runs at `git push` time and blocks the push before the secret reaches the remote. The mental model: secret scanning is the smoke detector; push protection is the sprinkler that goes off before the fire reaches the server room.

### 09. Custom Secret Patterns
Beyond the built-in patterns, GitHub Secret Protection lets org admins define **custom secret patterns** with regex + an optional pre/post-match heuristic, and since July 2026 manage them through the REST API (dry run and publish stay in the UI). This is how you catch *your own* token formats — internal API keys, employee badge IDs, anything with a recognizable shape. Critically, custom patterns also participate in **push protection**, so they're enforceable, not just observable.

### 10. Dependabot / Supply Chain
[Dependabot](https://docs.github.com/en/code-security/dependabot) does three things people often conflate: **alerts** (your dependency has a known CVE), **security updates** (auto-PRs that bump the vulnerable dependency to a patched version), and **version updates** (routine bumps regardless of vulnerabilities). The dependency graph powering all three is also what feeds the [advisory database](https://github.com/advisories), which is the same data Dependabot reads. Lesson 10 also opens a **Malware** alert — the supply-chain twin of vulnerability alerts, flagging actually-malicious packages from the Advisory DB (npm, PyPI, and more since July 2026). Its fixture pins `requestsa`, a typosquat of `requests` that PyPI has already removed.

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
2. Click **Generate fix** (button label may also read *"Autofix this alert"*). Wait 10–30 seconds — narrate the suggestion preview as it loads. If the alert shows **Assign to Copilot** instead, agentic autofix is enabled: follow lesson 02's agentic path and narrate the session instead.
3. Click **Create PR with fix**. Walk through the diff Copilot proposes — *out loud, in the PR review UI*, before merging. This is the part attendees remember.
4. Demonstrate the **edit-then-accept** flow: change one line of Copilot's diff, push to the branch, show that the alert is still resolved when CodeQL re-runs on the PR. Reinforces that Autofix is a starting point, not a rubber stamp.
5. Close with the **dismiss with reason** flow on a separate alert — shows that not every Autofix suggestion has to land. Mention the *Mitigated* reason added in August 2026, and reopen the alert afterwards.
6. **Close the PR without merging.** The `tests` check on the PR fails on purpose, explaining that the fix removes a planted vulnerability: a good closing point about tests guarding intended behavior.

**Availability caveat.** Copilot Autofix for code scanning does **not** require a GitHub Copilot subscription and does not consume AI credits. It is available for public repositories on GitHub.com and for qualifying private or internal repositories with GitHub Code Security. Administrators can disable it, so verify that Autofix is allowed before the workshop. Agentic autofix (*Assign to Copilot*) is generally available since October 15, 2026 on GitHub Enterprise Cloud. It doesn't need a Copilot license, but it does need the enterprise *Agentic autofix* policy, organization enablement, and a Copilot billing method. It consumes Code Security AI credits plus Actions minutes, and when enabled it replaces *Generate fix*.

## Where to capture screenshots

The repo ships with a frozen set of screenshots under [`docs/screenshots/`](docs/screenshots/), captured against the live `tkl-enteprises/ghas-demos` tenant. They're already embedded in the relevant lesson READMEs and the root README, so attendees see the same UI in markdown that you'll demo live. Re-capture against your own tenant before a deck — the `tkl-enteprises` images are workshop-grade, not customer-deck-grade.

| File | Lesson | Shows |
| --- | --- | --- |
| [`docs/screenshots/00-security-overview.png`](docs/screenshots/00-security-overview.png) | (root README hero) | Repo `Security and quality` tab landing page — alert counts across Code scanning, Secret scanning, and Dependabot. |
| [`docs/screenshots/01-code-scanning-alerts.png`](docs/screenshots/01-code-scanning-alerts.png) | 01 — CodeQL Code Scanning | Code-scanning alerts list filtered to **Tool: CodeQL**. |
| [`docs/screenshots/01-codeql-alert-detail.png`](docs/screenshots/01-codeql-alert-detail.png) | 01 — CodeQL Code Scanning | Alert detail page (SSTI) with the dataflow path expanded — source → sink hops visible. |
| [`docs/screenshots/04-actions-tab.png`](docs/screenshots/04-actions-tab.png) | 04 — SARIF Integration | Repo `Actions` tab showing CodeQL, Bandit-SARIF, Dependency review, and Dependabot Updates workflows green. |
| [`docs/screenshots/04-bandit-sarif-findings.png`](docs/screenshots/04-bandit-sarif-findings.png) | 04 — SARIF Integration | Code-scanning alerts filtered to **Tool: Bandit** — 20 open, led by B324 (MD5), B602 (`shell=True`), B201 (Flask debug), B301 (pickle). Paths predate the lesson renumbering. |
| [`docs/screenshots/security-overview-with-code-quality.png`](docs/screenshots/security-overview-with-code-quality.png) | 06 — Code Quality Standard findings | Preview-era organization view listing Code Quality among enabled features. |
| [`docs/screenshots/08-push-protection-settings.png`](docs/screenshots/08-push-protection-settings.png) | 08 — Secret Scanning + Push Protection | Repo security settings (now `Settings → Advanced Security`) showing the push-protection toggle on. |
| [`docs/screenshots/08-secret-scanning-default-empty.png`](docs/screenshots/08-secret-scanning-default-empty.png) | 08 — Secret Scanning + Push Protection | `Security and quality → Secret scanning` **Default** tab showing "No secrets found" — illustrates AI suppression on committed canaries. |
| [`docs/screenshots/09-secret-scanning-generic-ai.png`](docs/screenshots/09-secret-scanning-generic-ai.png) | 08 + 09 — Secret scanning / Custom patterns | `Security and quality → Secret scanning` **Generic** view — AI-detected secrets (formerly *Copilot secret scanning*) firing on `hunter2_FAKE_*`-style password assignments. |
| [`docs/screenshots/push-protection-block.txt`](docs/screenshots/push-protection-block.txt) | 08 — Secret Scanning + Push Protection | **Historical artifact** — verbatim terminal capture from a May 6, 2026 test against the workshop's previous AWS-first fixtures, where a fresh `AKIA…`-shaped canary was *not* blocked (`EXIT_CODE: 0`). The cause was never confirmed; the earlier explanation (ruleset bypass list, validity checks) was wrong. See *Push protection — what actually controls a block*. Re-verify enforcement before each delivery. |
| [`docs/screenshots/10-dependabot-alerts.png`](docs/screenshots/10-dependabot-alerts.png) | 10 — Dependabot / Supply Chain | `Security and quality → Dependabot` alerts list across Flask, Jinja2, Werkzeug, urllib3, requests, PyYAML, cryptography. |
| [`docs/screenshots/10-dependabot-prs-list.png`](docs/screenshots/10-dependabot-prs-list.png) | 10 — Dependabot / Supply Chain | Pull requests tab filtered to `app/dependabot` — individual pip update PRs, captured before grouping. With the current `dependabot.yml`, expect one grouped security-update PR and one grouped version-update PR. |
| [`docs/screenshots/10-dependabot-pr-detail.png`](docs/screenshots/10-dependabot-pr-detail.png) | 10 — Dependabot / Supply Chain | A Flask-bump security-update PR with CVE annotation, severity badge, release notes, and compatibility score. |
| [`docs/screenshots/11-org-security-overview-risk.png`](docs/screenshots/11-org-security-overview-risk.png) | 11 — Security Overview | Org-level **Risk** view — open alerts by severity and repo. |
| [`docs/screenshots/11-org-security-overview-coverage.png`](docs/screenshots/11-org-security-overview-coverage.png) | 11 — Security Overview | Org-level **Coverage** view — per-repo enablement of CodeQL / Dependabot / secret scanning / push protection. |

Gaps still worth capturing live in your tenant for a follow-up deck:

- 📸 Lesson 02 — the **Copilot Autofix** suggestion diff (before / after acceptance), or the agentic autofix draft PR, on the `py/sql-injection` alert in `insecure_login.py`.
- 📸 Lesson 03 — the code-scanning list and alert detail for `py/tkl/unprotected-admin-route`, including the rule help rendered from `UnprotectedAdminRoute.md`.
- 📸 Lesson 10 — the **Malware** view and alert detail for `requestsa`. The earlier empty-state capture was removed when the fixture was added.
- 📸 Lesson 11 — the **Configurations** page showing the `GitHub recommended` security configuration's feature toggles.
- 📸 Lesson 11 — a **Security campaigns** detail page (paid feature) with assigned repos and progress bars.

## Code Quality after Code Security

→ See [lesson 06](lessons/06-code-quality-standard-findings/) for deterministic CodeQL analysis and [lesson 07](lessons/07-code-quality-ai-findings/) for the post-merge AI walkthrough.

- **Same engine, different queries.** [GitHub Code Quality](https://github.com/tkl-enteprises/ghas-demos/security/quality) is distinct from GitHub Code Security and GitHub Secret Protection, but it runs on the same CodeQL engine. Maintainability and reliability queries replace the security-focused taint / SQLi / SSRF set.
- **Status:** **Generally available since July 20, 2026** on GitHub Team and GitHub Enterprise Cloud (not GitHub Enterprise Server). AI findings (lesson 07) remain in public preview.
- **Billing:** a standalone product: **$10 per active committer per month** (pushed to a Code Quality-enabled repository in the last 90 days; counted once per organization; bots free), plus usage-based **AI credits** for AI-assisted detection and Autofix, plus **GitHub Actions minutes** for the CodeQL analysis. No Copilot subscription needed. See [GitHub Code Quality billing](https://docs.github.com/en/billing/concepts/product-billing/github-code-quality).
- **Enforcement:** Code Quality supports rulesets that can block changes which miss configured quality standards or code-coverage thresholds, with an *evaluate* mode for gradual rollout. Push protection remains a Secret Protection capability, not a quality control.
- **Teaching contrast.** Standard findings use named CodeQL rules; AI findings are a second contextual scan after merge. Show them as separate lessons.
- **When to skip.** CISO briefings or pure-security audiences — drop it. The 60-min and 2-hour agendas skip it; whenever it is included, place it immediately after the Code Security block so the shared CodeQL engine is clear.

## Sample agendas

Three pre-built agendas. Pick one based on audience size, audience role, and the room you've been given. Total times below assume the [Pre-flight checklist](#pre-flight-checklist) has already been run and the repo is in a known-good state — they do **not** include setup time on the day.

### 60-minute executive overview (lessons 01, 08, 10, 11)

For C-suite, security leadership, or non-technical buyers. Uses one lesson from each security-focused pillar and skips the deeper technical and Code Quality material. Goal: leave the room knowing GitHub Code Security and GitHub Secret Protection cover code bugs and leaked secrets, GitHub's supply-chain features identify vulnerable dependencies, and there's a single org-level cockpit for all three.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:05 | — | Welcome + repo tour (`README.md` only) | Set expectations: repo is *intentionally* vulnerable; every alert is real. |
| 0:05–0:15 | 01 — CodeQL | Open the [SSTI alert](https://github.com/tkl-enteprises/ghas-demos/security/code-scanning?query=is%3Aopen+branch%3Amain+rule%3Apy%2Ftemplate-injection) (`py/template-injection` in `lessons/10-supply-chain-dependabot/app.py`). Walk the dataflow path source → sink. | Where does this fit in the SDLC? What changes if a developer never opens the PR? |
| 0:15–0:25 | 08 — Secret Scanning | Live `git push` of a fresh `CONTOSO-API-…` line on a workshop branch (custom pattern from lesson 09 — see *Push protection bypass* mitigations above). | What's our current MTTR on a leaked production secret? |
| 0:25–0:35 | 10 — Dependabot | Show the grouped pip security-update PR and contrast it with the grouped version-update PR. Walk the advisory annotations. Open the `requestsa` malware alert. | Who owns merging these today? How long do they sit? |
| 0:35–0:50 | 11 — Security Overview | Org-level **Risk** + **Coverage** views. Highlight enablement gaps. | Which 5 repos do we turn this on next? Who signs off? |
| 0:50–1:00 | — | Q&A + close | Action items: pick the next 5 repos; assign an owner. |

**Total: 60 min.** ⚠️ The lesson-08 demo *must* use the lesson-09 custom pattern — partner-pattern push protection silently bypasses for admins (see mitigation note above).

### 2-hour developer enablement (lessons 01, 02, 04, 08, 09, 10, 11)

For platform / appsec / senior dev audiences who own day-to-day triage. Covers seven foundational lessons in delivery order; deliberately skips lesson 03 (custom CodeQL queries) and optional/advanced lessons 05, 06, and 07 — they'll crowd out hands-on triage in this format. Goal: every attendee leaves able to triage an alert, push past a custom-pattern block, and read a SARIF upload.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:10 | — | Repo tour + workshop pillar map (root README) | Today's three pillars: code, secrets, supply chain. |
| 0:10–0:25 | 01 — CodeQL | Alerts list → alert detail → dataflow. Triage one alert as "won't fix" with reason. | When should you mark something `won't fix` vs `false positive`? |
| 0:25–0:35 | 02 — Copilot Autofix | *Generate fix* (or *Assign to Copilot*) on the lesson 02 `py/sql-injection` alert. Edit-then-accept the diff in the draft PR; don't merge. | When *not* to trust Autofix? What's your code-review SLA? |
| 0:35–0:50 | 04 — SARIF | Code-scanning alerts → filter Tool: Bandit. Show the same triage UI as CodeQL. | Which third-party scanners do we want in this view? |
| 0:50–1:00 | — | Code Security recap | How do CodeQL, Autofix, and third-party SARIF findings share a triage model? |
| 1:00–1:10 | — | ☕ Break | — |
| 1:10–1:25 | 08 — Secret Scanning | Live custom-pattern push protection block (see lesson 09). Show the secret-scanning Default + Generic tabs. | Why might a low-entropy Azure canary not block? (Push protection covers a subset of high-confidence patterns and applies entropy checks; validity checks don't gate blocking.) |
| 1:25–1:35 | 09 — Custom Patterns | Settings → Secret scanning → Custom patterns. Walk the two `Contoso …` patterns (pre-published per pre-flight step 6). Push a fresh `contoso_demo_…` and watch it block. | What internal token shapes belong here? (Badge IDs, internal API keys, vendor IDs.) |
| 1:35–1:45 | 10 — Dependabot | PR list filter `app/dependabot`. Walk the grouped security-update PR. Open the `requestsa` malware alert. | Auto-merge policy: green CI + Dependabot? Where's the line? |
| 1:45–1:55 | 11 — Security Overview | Org **Risk** + **Coverage** + Configurations. | Coverage gap → action plan. |
| 1:55–2:00 | — | Q&A + close | — |

**Total: 120 min.** Plan one ☕ break at the 1:00 mark to keep energy up.

### Half-day deep dive (all 11 lessons)

For mixed appsec + platform engineering audiences who want the full toolkit — including authoring custom CodeQL queries. 4 hours with two breaks. Goal: every attendee can walk away and stand this up on their own repo on Monday.

| Time | Lesson | Demo | Discussion |
| --- | --- | --- | --- |
| 0:00–0:15 | — | Welcome, repo tour, pre-flight walkthrough (`scripts/preflight.sh`) | What does enabling Code Security and Secret Protection actually mean? Five toggles. |
| 0:15–0:35 | 01 — CodeQL | Full triage flow on the SSTI alert: detail → dataflow → draft fix PR (close it unmerged). | When CodeQL is wrong: investigation flow + dismissal reasons. |
| 0:35–0:45 | 02 — Copilot Autofix | Autofix on the lesson 02 SQL-injection alert. Edit-then-accept; don't merge. | Where Autofix earns its keep; where it doesn't. |
| 0:45–1:15 | 03 — Custom CodeQL | Read and run `py/tkl/unprotected-admin-route`; show the finding on `noncompliant.py`, compare it with `compliant.py`, and open the alert's rule help. | Custom query vs. lint rule? |
| 1:15–1:30 | 04 — SARIF | Bandit upload → unified code-scanning view. | Which scanners stay? |
| 1:30–1:40 | 05 — Actions scanning | Compare the inert vulnerable and remediated workflow fixtures; show **Analyze (actions)**. | Where do workflow privileges cross trust boundaries? |
| 1:40–1:55 | — | ☕ Break | — |
| 1:55–2:10 | 06 — Code Quality Standard findings | Review deterministic findings, ratings, PR feedback, and ruleset options. | Would your team gate merges on quality? |
| 2:10–2:25 | 07 — Code Quality AI findings | Review the recent-merge grammar and contextual suggestions. | How should nondeterministic suggestions be governed? |
| 2:25–2:40 | 08 — Secret Scanning | Custom-pattern push block; show the validity-check distinction. | Leaks in commits vs CI logs vs images. |
| 2:40–3:00 | 09 — Custom Patterns | Walk the Contoso patterns and push-block a fresh demo value. | Pattern hygiene and false positives. |
| 3:00–3:15 | 10 — Dependabot (+ Malware) | Alerts → update PR → CVSS/EPSS; open the `requestsa` malware alert. | Dependabot vs reachability. |
| 3:15–3:30 | — | ☕ Break | — |
| 3:30–3:50 | 11 — Security Overview | Org **Risk**, **Coverage**, **Configurations**, and **Campaigns** if available. | 90-day rollout plan. |
| 3:50–4:00 | — | Wrap, action items, follow-up resources | — |

**Total: 240 min** with two 15-minute breaks. Lesson 03 gets the largest slot because authoring and running a custom query is the most technical content. Lesson 07 requires a pull request merged after Code Quality was enabled; prepare that qualifying merge before the workshop.
