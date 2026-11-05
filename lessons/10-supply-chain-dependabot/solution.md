# Solution — Dependabot triage & resolution playbook

This is the operational companion to `README.md`. It's written for the workshop facilitator (or a security engineer landing on a new repo) and covers: how to triage each alert, what your resolution options actually are, how to tune `dependabot.yml` so the alerts stay actionable, and the limits of "alert" vs "reachable risk".

## Fixture integrity

This lesson intentionally pins `Flask==0.12.0`, `Jinja2==2.10`, `Werkzeug==0.14`, `urllib3==1.24.1`, `requests==2.19.1`, `PyYAML==5.1`, and `cryptography==2.3` in both manifests. Each exact version is in the affected range of the representative GitHub Advisory Database entry listed in `README.md` and has a patched version available, making it eligible for the grouped security-update demo. Some packages match more than one advisory.

Never install these dependencies or execute `app.py`. Keep the manifest warning, exact pins, and the `applies-to: security-updates` group intact when resetting the workshop.

`malware-demo/requirements.txt` pins `requestsa==2.28.1`, the malicious release named in [GHSA-3pmj-h39m-cfpm](https://github.com/advisories/GHSA-3pmj-h39m-cfpm), only to raise the malware alert. PyPI no longer serves the project. Never install that file, generate a lockfile from it, or add its directory to `dependabot.yml`.

## Triage workflow

When a Dependabot alert lands, walk the same checklist every time:

1. **Severity & CVSS.** GitHub surfaces the advisory's CVSS vector. Critical / High alerts deserve a same-week response; Moderate / Low can be batched.
2. **Affected version range vs. your pin.** Confirm your pinned version is *actually* in the affected range — Dependabot does this for you, but double-check on the advisory page.
3. **Exploitability.** Is there a published PoC or a known-exploited tag (KEV)? An advisory with a public exploit + internet-facing surface is qualitatively different from a theoretical issue in a CLI helper.
4. **In-context use.** Do you call the vulnerable API at all? Example: `PyYAML` 5.1's `yaml.load` RCE only matters if you actually call `yaml.load` on untrusted input. If you only ever use `yaml.safe_load`, the alert is informational.
5. **Blast radius.** Is this dep loaded in a request-handling path, a build-time tool, or a test-only helper? Test-only deps usually deserve faster patches because nobody validates them, but lower priority because they don't touch production.
6. **Fix availability.** Does a fixed version exist *and* is it semver-compatible with your current pin? If yes → upgrade. If no → see "Resolution paths" below.

Document the decision on the alert itself with **Dismiss → Reason** so the next person (and your auditors) can see why. Dependabot's reasons are: *A fix has already been started*, *No bandwidth to fix this*, *Risk is tolerable to this project*, *This alert is inaccurate or incorrect*, and *Vulnerable code is not actually used*. (Code scanning has its own list — see lesson 01.)

## Resolution paths

| Path                | When to use it                                                                                     | How                                                                                                    |
|---------------------|----------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **Upgrade**         | A fixed version exists and your tests pass against it.                                             | Merge the Dependabot PR. For grouped updates, review the release notes Dependabot embeds in the PR.    |
| **Replace**         | The package is unmaintained or the fix forces a major-version migration you'd rather skip.        | Swap to an actively-maintained alternative (e.g. `requests` → `httpx`, `PyYAML` → `ruamel.yaml`).      |
| **Ignore w/ comment** | Vulnerable code path is provably unreachable in your usage.                                       | Dismiss the alert as **"Vulnerable code is not actually used"** with a written justification.          |
| **Accept risk**     | No fix available, replacement is unrealistic, exposure is bounded by other controls.               | Dismiss as **"Risk is tolerable to this project"**, log a tracking issue, set a recheck date in your risk register. |
| **Pin transitive**  | A vulnerability is in a transitive dep and your direct dep hasn't released a fix yet.              | Add a constraint file or `pyproject.toml` override pinning the transitive to a safe version.           |

## Dependabot configuration tips

The repository's [`.github/dependabot.yml`](../../.github/dependabot.yml) is the reference configuration for this lesson. A few knobs worth knowing for follow-up work:

- **Security grouping** — under the ecosystem entry, use `groups.<identifier>.applies-to: security-updates` plus `patterns`/`exclude-patterns`. Without `applies-to`, a group applies to version updates. This lesson uses `"*"` to group all eligible pip security fixes in its directory.
- **Schedule** — `schedule.interval` controls checks for version updates. Security updates react to Dependabot alerts and available fixes; the weekly schedule does not delay an alert until the next weekly run.
- **Cooldown** — since July 2026 version updates wait a default 3 days after a release before Dependabot proposes them (tune with `cooldown:`). Security updates are not delayed.
- **Version-update target branch** — `target-branch:` can point version updates at a long-lived integration branch. Do not set it on this security-update demo: security updates target the default branch.
- **Allow / ignore lists** — `allow:` restricts to specific dep types (e.g. only `direct`); `ignore:` lets you skip a known-noisy package or a major version you've consciously deferred. Always document *why* in a comment next to the entry.
- **Open PR limit** — `open-pull-requests-limit:` keeps the queue bounded. Pair with auto-merge for patch bumps.
- **Reviewers / labels / commit-message** — small ergonomics knobs that make Dependabot PRs blend into your normal review flow.

For Python specifically, prefer `package-ecosystem: pip` and let Dependabot infer the manifest. If you use Poetry exclusively, switch to `package-ecosystem: pip` with `directory:` pointing at the `pyproject.toml`'s folder — Dependabot understands both.

Grouped security updates require the dependency graph, Dependabot alerts, and Dependabot security updates to be enabled. The configuration must target the manifest directory on the default branch and must not set a non-default `target-branch`. Dependabot can leave an update outside a group when no fix exists or constraints cannot be resolved together; configuration changes can also close superseded individual PRs and open a grouped PR.

## Reachability

This is the most common source of confusion in workshops, so it's worth spelling out:

> **For this Python lesson, Dependabot alerts on the *presence* of a vulnerable dependency in your dep graph. It does not analyse whether your code actually calls the vulnerable function.**

Since October 2026, Dependabot **reachability analysis** (public preview) adds that context for **JavaScript and TypeScript** only: CodeQL builds a call graph across the repository and its dependencies and marks each alert *Reachable*, *Potentially reachable*, or *Unreachable*. It does not cover Python, so the reasoning below still applies to this fixture.

That means:

- A `Critical` alert on `PyYAML` 5.1 fires whether you use `yaml.safe_load` everywhere (safe) or `yaml.load` on user input (instant RCE).
- An alert on `requests` 2.19.1 fires whether you ever follow cross-origin redirects with credentials or not.

To get **reachability** — "does my code actually hit the vulnerable code path?" — you need a layer above Dependabot:

- **CodeQL** — GitHub's own static analyser. It can taint-track from sources (e.g. `request.args`) to sinks (e.g. `yaml.load`) and tell you when a Dependabot-flagged dep is reached by attacker-controlled data. This lesson's `app.py` shows it: `py/unsafe-deserialization` points at the same `yaml.load` call the PyYAML advisory is about.
- **Commercial SCA** (Snyk, Mend, Sonatype, Endor Labs) — each has its own reachability engine, with different language coverage and false-positive profiles.
- **Manual code review** — for small, critical libs, often the fastest path.

Best-practice flow: Dependabot tells you *what* is vulnerable, CodeQL/SCA tells you *whether it matters*, and your triage step (above) decides what to do about it.

## Further reading

- GitHub docs — Dependabot: <https://docs.github.com/en/code-security/dependabot>
- Dependabot options reference (`groups` and `applies-to`): <https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference>
- Configuring grouped security updates: <https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configuring-dependabot-security-updates>
- Dependabot malware alerts: <https://docs.github.com/en/code-security/concepts/supply-chain-security/malware-alerts>
- Organization security overview: <https://docs.github.com/en/code-security/concepts/security-at-scale/security-overview>
- GitHub Advisory Database: <https://github.com/advisories>
- `actions/dependency-review-action`: <https://github.com/actions/dependency-review-action>
- Automating Dependabot with Actions: <https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions>
