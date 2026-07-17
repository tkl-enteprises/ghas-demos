# ghas-demos

![CodeQL](https://github.com/tkl-enteprises/ghas-demos/actions/workflows/codeql.yml/badge.svg)
![tests](https://github.com/tkl-enteprises/ghas-demos/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Lessons: 11](https://img.shields.io/badge/Lessons-11-brightgreen)

> ⚠️ **WARNING — INTENTIONALLY VULNERABLE REPOSITORY** ⚠️
>
> This repository contains **intentionally vulnerable code**, **fake/canary credentials**, and **known-vulnerable dependencies** for educational purposes.
>
> ❌ **Do not deploy this code.**
> ❌ **Do not reuse any of it in production.**
> ❌ **Do not paste real secrets into this repo, even to "test" the scanners.**
>
> ✅ Every finding here demonstrates GitHub's integrated security capabilities, including [**GitHub Code Security** and **GitHub Secret Protection**](https://docs.github.com/en/code-security/getting-started/github-security-features) — that is the entire point.

---

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/tkl-enteprises/ghas-demos?quickstart=1)

![Repository Security and quality tab showing alert counts across Code scanning, Secret scanning, and Dependabot — the hero view this workshop builds toward.](docs/screenshots/00-security-overview.png)

*The repo's `Security and quality` tab — every lesson below ladders up to a number on this page._

---

## Table of contents

- [What are GitHub Code Security and GitHub Secret Protection?](#what-are-github-code-security-and-github-secret-protection)
- [Workshop format](#workshop-format)
- [Workshop pillars at a glance](#workshop-pillars-at-a-glance)
- [Lessons](#lessons)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Where to look in GitHub UI](#where-to-look-in-github-ui)
- [License](#license)
- [Disclaimer](#disclaimer)

## Quick start

**Option A — Codespaces (recommended for workshop attendees):**
[Open this repo in a Codespace](https://codespaces.new/tkl-enteprises/ghas-demos?quickstart=1) — the dev container pre-installs Python, the `gh` CLI, and the lesson dependencies. You can be running lesson 01 in under 60 seconds.

**Option B — Local clone:**
```bash
git clone https://github.com/tkl-enteprises/ghas-demos.git && cd ghas-demos
```
That's it for the source-review and UI lessons: no local package installation is required. Lesson 06 (Dependabot) is *intentionally* a list of vulnerable old pins in `lessons/06-dependabot-supply-chain/requirements.txt` — those packages won't install on Python 3.11 on purpose, and that's the demo (you don't need them locally; Dependabot scans the manifest from GitHub). Lesson 07's workflow installs Bandit for its SARIF exercise; lessons 10 and 11 use inert text/source fixtures that must not be executed or deployed.

## What are GitHub Code Security and GitHub Secret Protection?

[GitHub Advanced Security capabilities are sold as two products](https://docs.github.com/en/code-security/getting-started/github-security-features): **GitHub Code Security** helps find and fix vulnerabilities with code scanning, Copilot Autofix, dependency review, and premium Dependabot capabilities; **GitHub Secret Protection** detects exposed credentials with secret scanning and blocks new leaks with push protection. GitHub also provides core supply-chain features, including Dependabot alerts and security updates, across GitHub plans. The goal of this workshop is to make these capabilities fire on a small, friendly Python codebase so attendees can see, with their own eyes, what shows up where.

## Workshop format

- **9 core lessons + 2 optional preview lessons**, each in its own folder under [`lessons/`](lessons/).
- **Self-contained** — every lesson has its own `README.md` with goal, steps, and where to look in the GitHub UI.
- **Runnable in any order** — there are no cross-lesson dependencies. Pick the pillar your audience cares about and start there.
- **Python-first and source-review safe** — the core app examples are Python 3; lessons 10 and 11 add inert workflow and multi-language fixtures. No Docker build, Terraform apply, or cloud deployment is required.

## Workshop pillars at a glance

The seven pillars below are the mental model attendees should leave with — every lesson in the next section maps to one (or more) of them.

```mermaid
flowchart LR
  P1["Code Security: Code Scanning"] --> L1["Lesson 1: CodeQL"]
  P1                       --> L2["Lesson 2: Copilot Autofix"]
  P1                       --> L3["Lesson 3: Custom queries"]
  P1                       --> L10["Lesson 10: Actions scanning"]
  P2["Secret Protection: Secret Scanning"] --> L4["Lesson 4: Detection + push protection"]
  P2                       --> L5["Lesson 5: Custom patterns"]
  P3["Supply Chain"]       --> L6["Lesson 6: Dependabot + Malware"]
  P4["3rd-party / SARIF"]  --> L7["Lesson 7: Bandit + SARIF upload"]
  P5["Governance"]         --> L8["Lesson 8: Org Security Overview"]
  P6["Code Quality (public preview)"] -.-> L9["Lesson 9: Code Quality (bonus)"]
  P7["AI security detections (public preview)"] -.-> L11["Lesson 11: AI security detections"]
```

> The dashed arrows mark optional public-preview material. **GitHub Code Quality** is distinct from GitHub Code Security and GitHub Secret Protection; it uses CodeQL infrastructure with maintainability and reliability queries instead of security queries. GitHub documents general availability for July 20, 2026. During preview, scans consume GitHub Actions minutes but active-committer and AI-credit usage is not billed; [GA introduces additional usage charges](https://docs.github.com/en/billing/concepts/product-billing/github-code-quality). **AI-powered security detections** complement CodeQL with advisory, pull-request-only findings for coverage gaps and require a separately configured repository that uses CodeQL default setup. See [lesson 9](lessons/09-code-quality/) and [lesson 11](lessons/11-ai-security-detections/).

## Lessons

Lessons are grouped by workshop pillar — Code Scanning (1–3 and 10), Secret Scanning (4–5), Supply Chain (6), 3rd-party / SARIF (7), Governance (8), plus optional preview lessons for Code Quality (9) and AI-powered security detections (11).

| # | Pillar | Lesson | Folder |
| - | ------ | ------ | ------ |
| 1 | Code Scanning   | CodeQL Code Scanning | [`lessons/01-codeql-code-scanning/`](lessons/01-codeql-code-scanning/) |
| 2 | Code Scanning   | Copilot Autofix | [`lessons/02-copilot-autofix/`](lessons/02-copilot-autofix/) |
| 3 | Code Scanning   | Custom CodeQL Queries | [`lessons/03-custom-codeql-queries/`](lessons/03-custom-codeql-queries/) |
| 4 | Secret Scanning | Secret Scanning + Push Protection | [`lessons/04-secret-scanning/`](lessons/04-secret-scanning/) |
| 5 | Secret Scanning | Custom Secret Patterns | [`lessons/05-custom-secret-patterns/`](lessons/05-custom-secret-patterns/) |
| 6 | Supply Chain    | Dependabot / Supply Chain (+ Malware bonus) | [`lessons/06-dependabot-supply-chain/`](lessons/06-dependabot-supply-chain/) |
| 7 | 3rd-party / SARIF | SARIF / 3rd-party Tool Integration | [`lessons/07-sarif-integration/`](lessons/07-sarif-integration/) |
| 8 | Governance      | Security Overview (Org-level Governance) | [`lessons/08-security-overview/`](lessons/08-security-overview/) |
| 9 | Code Quality (bonus / public preview) | Code Quality — same engine, different queries | [`lessons/09-code-quality/`](lessons/09-code-quality/) |
| 10 | Code Scanning | CodeQL for GitHub Actions | [`lessons/10-codeql-actions/`](lessons/10-codeql-actions/) |
| 11 | AI security detections (optional / public preview) | AI-powered security detections in pull requests | [`lessons/11-ai-security-detections/`](lessons/11-ai-security-detections/) |

## Prerequisites

- A **GitHub Team or GitHub Enterprise Cloud organization**. Private or internal workshop repositories need access to **GitHub Code Security** and **GitHub Secret Protection**; many demonstrated capabilities are available free for public repositories. This repo lives under [`tkl-enteprises`](https://github.com/tkl-enteprises).
- **Python 3.11+** on the workstation following along.
- Optional: the [**CodeQL CLI**](https://docs.github.com/en/code-security/codeql-cli) for lesson 3 (custom queries) if you want to iterate locally.
- Optional: the [**`gh` CLI**](https://cli.github.com/) for cloning and triggering workflows from the terminal.

## Where to look in GitHub UI

Most of the demo value lives in the GitHub UI, not in the source code. Bookmark these:

- **`Security and quality → Code scanning`** → [https://github.com/tkl-enteprises/ghas-demos/security/code-scanning](https://github.com/tkl-enteprises/ghas-demos/security/code-scanning)
- **`Security and quality → Secret scanning`** → [https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning](https://github.com/tkl-enteprises/ghas-demos/security/secret-scanning)
- **`Security and quality → Dependabot`** → [https://github.com/tkl-enteprises/ghas-demos/security/dependabot](https://github.com/tkl-enteprises/ghas-demos/security/dependabot)
- **`Org → Security overview`** → [https://github.com/orgs/tkl-enteprises/security/overview](https://github.com/orgs/tkl-enteprises/security/overview)

## License

[MIT](LICENSE) — do whatever you want with the workshop materials, but please don't ship the vulnerable code.

## Disclaimer

This repository is **not affiliated with Microsoft or GitHub**. All opinions are the author's own. The code, configurations, and credentials in this repository are **intentionally vulnerable** and exist solely to demonstrate [GitHub Code Security, GitHub Secret Protection, and related GitHub security capabilities](https://docs.github.com/en/code-security/getting-started/github-security-features). **Do not use any of this in production.** If a scanner flags it, that's the feature working — not a bug.
