# ghas-demos

> ⚠️ **WARNING — INTENTIONALLY VULNERABLE REPOSITORY** ⚠️
>
> This repository contains **intentionally vulnerable code**, **fake/canary credentials**, and **known-vulnerable dependencies** for educational purposes.
>
> ❌ **Do not deploy this code.**
> ❌ **Do not reuse any of it in production.**
> ❌ **Do not paste real secrets into this repo, even to "test" the scanners.**
>
> ✅ Every finding here is **detected by [GitHub Advanced Security (GHAS)](https://docs.github.com/en/code-security/getting-started/github-security-features)** — that is the entire point.

---

## What is GHAS?

[GitHub Advanced Security](https://docs.github.com/en/code-security/getting-started/github-security-features) (GHAS) is GitHub's native application security suite. It bundles **CodeQL code scanning**, **secret scanning with push protection**, **Dependabot supply chain alerts**, **Copilot Autofix**, and **org-level security overview / governance** into the same UI your developers already use for code review. The goal of this workshop is to make every one of those features fire on a small, friendly Python codebase so attendees can see, with their own eyes, what shows up where.

## Workshop format

- **8 lessons**, each in its own folder under [`lessons/`](lessons/).
- **Self-contained** — every lesson has its own `README.md` with goal, steps, and where to look in the GitHub UI.
- **Runnable in any order** — there are no cross-lesson dependencies. Pick the pillar your audience cares about and start there.
- **Python-only** — every code sample is plain Python 3. No build tools, no Docker, no cloud accounts required.

## Lessons

| # | Lesson | Folder |
| - | ------ | ------ |
| 1 | CodeQL Code Scanning | [`lessons/01-codeql-code-scanning/`](lessons/01-codeql-code-scanning/) |
| 2 | Secret Scanning + Push Protection | [`lessons/02-secret-scanning/`](lessons/02-secret-scanning/) |
| 3 | Dependabot / Supply Chain | [`lessons/03-dependabot-supply-chain/`](lessons/03-dependabot-supply-chain/) |
| 4 | Copilot Autofix | [`lessons/04-copilot-autofix/`](lessons/04-copilot-autofix/) |
| 5 | Custom CodeQL Queries | [`lessons/05-custom-codeql-queries/`](lessons/05-custom-codeql-queries/) |
| 6 | Custom Secret Patterns | [`lessons/06-custom-secret-patterns/`](lessons/06-custom-secret-patterns/) |
| 7 | SARIF / 3rd-party Tool Integration | [`lessons/07-sarif-integration/`](lessons/07-sarif-integration/) |
| 8 | Security Overview (Org-level Governance) | [`lessons/08-security-overview/`](lessons/08-security-overview/) |

## Prerequisites

- A **GitHub Enterprise organization with GHAS enabled** (this repo lives under [`tkl-enteprises`](https://github.com/tkl-enteprises), which has GHAS).
- **Python 3.11+** on the workstation following along.
- Optional: the [**CodeQL CLI**](https://docs.github.com/en/code-security/codeql-cli) for lesson 5 (custom queries) if you want to iterate locally.
- Optional: the [**`gh` CLI**](https://cli.github.com/) for cloning and triggering workflows from the terminal.

## Quick start

```bash
gh repo clone tkl-enteprises/ghas-demos && cd ghas-demos && cat lessons/01-codeql-code-scanning/README.md
```

Then open the repo in your browser and keep the **Security** tab visible on a second monitor — most of the lesson payoff happens there, not in the code.

## Where to look in GitHub UI

Most of the demo value lives in the GitHub UI, not in the source code. Bookmark these:

- **`Security → Code scanning`** → [https://github.com/tkl-enteprises/ghas-demos/security/code-scanning](https://github.com/tkl-enteprises/ghas-demos/security/code-scanning)
- **`Security → Secret scanning`** → [https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning](https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning)
- **`Security → Dependabot`** → [https://github.com/tkl-enteprises/ghas-demos/security/dependabot](https://github.com/tkl-enteprises/ghas-demos/security/dependabot)
- **`Org → Security overview`** → [https://github.com/orgs/tkl-enteprises/security/overview](https://github.com/orgs/tkl-enteprises/security/overview)

## License

[MIT](LICENSE) — do whatever you want with the workshop materials, but please don't ship the vulnerable code.

## Disclaimer

This repository is **not affiliated with Microsoft or GitHub**. All opinions are the author's own. The code, configurations, and credentials in this repository are **intentionally vulnerable** and exist solely to demonstrate detection capabilities of [GitHub Advanced Security](https://docs.github.com/en/code-security/getting-started/github-security-features). **Do not use any of this in production.** If a scanner flags it, that's the feature working — not a bug.
