# Lesson 10 — Governance and Security Overview

> Docs-only lesson. Every demo step happens in the GitHub UI.

## Goal

Use the organization and enterprise **Security and quality** views to answer:

- Where is risk concentrated?
- Which repositories are not covered?
- Are teams detecting, preventing, and remediating findings?
- How can security leaders turn a backlog into owned remediation work?

This lesson uses [`tkl-enteprises`](https://github.com/tkl-enteprises), but the same flow applies to any eligible organization.

## Learning objectives

After this lesson, attendees can:

- Navigate the current organization and enterprise **Security and quality** views.
- Explain the difference between **Overview**, **Risk**, **Coverage**, **Assessments**, feature-specific findings, and **Campaigns**.
- Run or interpret the free Secret Risk Assessment and Code Security Risk Assessment.
- Distinguish a point-in-time risk assessment from continuously enabled GitHub security products.
- Use the dedicated **Dependabot** overview to prioritize supply-chain risk.
- Describe licensing, role, and preview fallbacks without blocking a governance discussion.

## Estimated time

**20-minute demo + 10-minute discussion**

## Prerequisites

Complete this preflight before the session:

- Use an organization on **GitHub Team or GitHub Enterprise Cloud**. Security overview is available to eligible organizations that have run a Secret Risk Assessment.
- Prefer an **organization owner** or **security manager** account. Those roles can see all repositories and use **Assessments**. Organization members see only repositories for which they have appropriate alert access.
- For an enterprise demo, use an organization-owner or security-manager role in each organization whose data you need to show. Enterprise ownership alone does not grant repository-level security visibility.
- Ensure the organization contains representative dependency, code scanning, or secret scanning data. Lessons 01–09 can create useful examples.
- Confirm product entitlements before promising a feature:
  - Dependabot data and the free risk assessments do not require GitHub Code Security or GitHub Secret Protection.
  - Private or internal repository data from code scanning and continuous secret scanning requires the corresponding GitHub Advanced Security product. Eligible public repositories may expose these features without a paid license.
  - Code and secret security campaigns depend on the corresponding alert data and product availability.
- If demonstrating a live assessment, run it before the session or allow time for asynchronous completion. Assessments can be rerun only every **90 days**.
- Do not publish a campaign during a shared demo unless repository owners have agreed to notifications and issues. A draft is sufficient.

Official permission details: [Security overview permissions](https://docs.github.com/en/enterprise-cloud@latest/code-security/reference/permissions/security-overview).

## Product and status guardrails

Treat this table as a facilitator preflight, not a licensing quote. GitHub plans and previews change; verify the linked documentation shortly before each delivery.

| Surface | Eligibility and status | Important caveat |
| --- | --- | --- |
| Security overview | Organizations on GitHub Team or GitHub Enterprise that have run a Secret Risk Assessment; additional views exist for enterprises and licensed Advanced Security products | Every view is permission-scoped. Summary views use default-branch/default-alert data and can differ from feature-specific findings. |
| Secret Risk Assessment | Free for organizations on GitHub Team or GitHub Enterprise; organization owners and security managers; rerunnable every 90 days | A point-in-time report, not continuous secret scanning or push protection. The current docs present it as an available feature rather than a preview. |
| Code Security Risk Assessment | Free for GitHub Team and GitHub Enterprise Cloud organizations; organization owners and security managers; rerunnable every 90 days | Announced in **public preview** and subject to change. It scans at most 20 selected private/internal repositories and is not continuous code scanning. |
| Code scanning campaigns | Requires available code scanning alerts and the applicable Code Security/GHAS entitlement; created by owners, security managers, or organization members with the admin role | Templates select alerts supported by Copilot Autofix. Creating a campaign can notify developers; publishing can optionally create repository issues. |
| Secret scanning campaigns | Requires available secret scanning alerts and the applicable Secret Protection/GHAS entitlement | GitHub announced general availability in November 2025, but the current campaign concept and creation docs still carry a **public preview** warning. Treat the documented workflow as changeable and verify the tenant before delivery. |
| Dependabot overview | Dependabot data is available in security overview for eligible organizations without a GHAS license | It summarizes vulnerable-dependency risk and remediation. Update schedules and pull requests are still configured at repository level. |

## Current Security and quality map

Open the organization at [https://github.com/orgs/tkl-enteprises/security/overview](https://github.com/orgs/tkl-enteprises/security/overview), or select the organization’s **Security and quality** tab.

- **Overview** — trends in **Detection**, **Remediation**, and **Prevention**.
- **Risk** — current repository risk across Dependabot, code scanning, and secret scanning.
- **Coverage** — feature adoption by repository; “not enabled” identifies governance gaps.
- **Assessments** — free point-in-time Code Security and Secret Protection reports.
- **Campaigns** — scoped, owned remediation efforts with due dates and progress.
- **Enablement** — adoption trends for Dependabot, code scanning, and secret scanning.
- **CodeQL pull requests** — impact of CodeQL analysis in pull requests.
- **Dependabot** — dedicated supply-chain risk and remediation view.
- **Secret scanning** — secret and push-protection trends when the required data is available.
- Feature-specific findings — detailed code scanning, Dependabot, or secret scanning alerts and filters.

All views show only repositories the viewer may access. Overview, Coverage, and Risk are based on default branches and omit generic secret alerts and alerts from ignored directories, so their totals can be lower than the dedicated findings views. No alerts can also mean that a feature is disabled, not that a repository is safe.

## Step-by-step navigation

### 1. Establish the governance dashboard

1. Open the organization and click **Security and quality**.
2. On **Overview**, switch between **Detection**, **Remediation**, and **Prevention**.
3. Change the date range and add one repository, team, or tool filter.
4. Point out that all tiles and metrics update with the filters.

**Expected outcome:** Attendees can explain that Overview measures trends, while detailed findings remain in feature-specific views.

**Fallback:** If Overview is empty, use the empty state to discuss data prerequisites, then open the [official overview documentation](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/security-at-scale/about-security-overview). Do not imply that zero visible alerts means zero risk.

### 2. Compare Risk and Coverage

1. Open **Risk** and identify the repository with the highest visible critical or high-severity count.
2. Filter to a single alert type, then show how the repository ordering changes.
3. Open **Coverage** and choose **not enabled** for one feature.
4. Ask whether each gap is an exception, an unsupported ecosystem, or an onboarding failure.
5. If available, open **Enablement** and compare the trend with today’s Coverage snapshot.

**Expected outcome:** Attendees distinguish exposure (**Risk**) from control adoption (**Coverage**) and adoption over time (**Enablement**).

![Org-level Security Overview → Risk view for `tkl-enteprises` showing open alerts by severity and repository, with `ghas-demos` as the dominant contributor.](../../docs/screenshots/10-org-security-overview-risk.png)

*Risk identifies where intervention is needed. Alert counts naturally change between cohorts.*

![Org-level Security Overview → Coverage view for `tkl-enteprises` showing per-repo enablement of CodeQL, Dependabot alerts, secret scanning, and push protection.](../../docs/screenshots/10-org-security-overview-coverage.png)

*Coverage answers whether the expected controls are enabled.*

### 3. Use the dedicated Dependabot overview

1. In the sidebar, select **Dependabot** rather than stopping at the aggregate Risk view.
2. Filter to open critical or high-severity vulnerable dependencies.
3. Identify the repositories, ecosystems, and advisories contributing most risk.
4. Open one finding only if the account has access; point out the affected manifest, severity, and fixed version when available.
5. Return to **Coverage** and check whether any repositories show Dependabot as disabled or paused.

**Expected outcome:** Attendees use the dedicated view to prioritize supply-chain remediation and understand that “paused” updates and disabled alerts need different responses.

**Fallback:** If there are no findings, show the Dependabot tab and use [About Dependabot alerts](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/supply-chain-security/dependabot-alerts) to explain how default-branch dependency data and the GitHub Advisory Database produce alerts. Lesson 09 remains the repository-level update workflow.

### 4. Explain and inspect the free risk assessments

1. Select **Assessments**.
2. If reports already exist, switch between **Code Security** and **Secret Protection**.
3. For the Secret Risk Assessment, call out total secrets, public leaks, preventable leaks, secret categories, and affected repositories.
4. For the Code Security Risk Assessment, call out vulnerabilities by severity and the count supported by Copilot Autofix.
5. Show the report date and the next eligible rerun date.
6. If no report exists, explain that **Scan your organization** starts both assessments on the first run. Start it only if the facilitator is authorized and the selected repositories have been reviewed.

**Expected outcome:** Attendees can describe both assessments as free discovery tools and avoid presenting them as continuous protection.

#### Secret Risk Assessment limits

- Available to organization owners and security managers on GitHub Team or GitHub Enterprise.
- Free and rerunnable once every 90 days.
- Point-in-time discovery; continuous monitoring and push protection require GitHub Secret Protection for private/internal repositories.

#### Code Security Risk Assessment limits

- Available to organization owners and security managers on GitHub Team or GitHub Enterprise Cloud.
- Free: no Code Security license charge, and assessment GitHub Actions minutes are provided at no cost.
- Preselects up to **20 private or internal repositories** based on commit activity in the previous 90 days; the facilitator can change the selection.
- Only repositories with a code-scanning-supported language are selectable.
- Each scan has a one-hour timeout. A repository is reported if at least one language succeeds.
- Rerunnable once every 90 days.
- Public-preview behavior and labels can change; confirm the current docs before delivery.

**Fallback:** If **Assessments** is absent, confirm the plan and role rather than searching for a GHAS toggle. Use the official report examples linked below. If the 90-day lockout applies, interpret the existing report instead of rerunning it.

### 5. Demonstrate a code scanning campaign safely

1. Select **Campaigns** and click **Create campaign**.
2. Choose a **Code** template, or choose **From code scanning filters**.
3. Use a narrow example such as `is:open autofilter:true autofix:supported severity:critical`.
4. Review the selected alerts and repository owners. Campaigns support at most 1,000 alerts.
5. Choose **Draft campaign**, add a clear name, due date, manager, and contact link, then stop before publishing.
6. Explain that code campaign alerts are submitted to Copilot Autofix and that publishing can notify contributors and optionally create repository issues.

**Expected outcome:** Attendees can turn a filtered code scanning backlog into a measurable, owned remediation effort without surprising developers.

**Fallback:** If **Campaigns**, **Create campaign**, or templates are absent, do not improvise licensing. Confirm the role, Code Security entitlement, available alerts, and whether the feature is enabled for the organization. Walk through the [official creation guide](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/manage-security-alerts/remediate-alerts-at-scale/creating-managing-security-campaigns) without publishing.

### 6. Show the secret scanning campaign expansion

1. From **Create campaign**, look for a **Secrets** template or **From secret scanning filters**.
2. If available, use a narrow filter such as `is:open provider:azure`.
3. Explain the operational difference: leaked credentials generally require revocation or rotation as well as removing the secret from code.
4. Save only as a draft, or cancel before saving.

**Expected outcome:** Attendees understand that the campaign workflow now extends to secret scanning alerts, while remediation differs from a code fix.

**Fallback:** GitHub's November 2025 changelog calls this capability generally available, while current campaign docs still label it **public preview and subject to change**. If the option is absent, show the code campaign flow, explain the status discrepancy, and verify the tenant's Secret Protection entitlement, permissions, eligible alerts, and rollout. Do not treat absence as proof of a configuration failure.

### 7. Optional enterprise roll-up

1. Open the enterprise account from the profile menu.
2. Select the enterprise **Security and quality** tab.
3. Open **Overview**, **Risk**, or **Coverage** and use the `owner` filter to isolate an organization.
4. Compare the enterprise aggregate with the organization view.
5. If available, mention **Public monitoring**, which surfaces secrets leaked by enterprise members in public repositories outside the enterprise.

**Expected outcome:** Attendees understand that enterprise views aggregate organizations but preserve repository permissions.

**Fallback:** If the enterprise tab or details are unavailable, demonstrate the organization view and explain the role requirement. An enterprise owner must also have the appropriate organization role to see repository-level data.

## Security configurations

Security configurations are reusable policy bundles used to apply security settings consistently across repositories.

1. Open [organization security settings](https://github.com/organizations/tkl-enteprises/settings/security_products).
2. Review the **GitHub recommended** configuration.
3. Explain when to clone it for a custom tier such as `production` or `internal-only`.
4. Show how a configuration can target repositories and new-repository defaults.

**Expected outcome:** Attendees connect Coverage gaps to a scalable control-deployment mechanism.

**Fallback:** If the account cannot edit settings, discuss the recommended configuration without changing it. Do not change organization policy during a workshop.

## Facilitator fallback matrix

| Symptom | Likely cause | Continue with |
| --- | --- | --- |
| **Security and quality** is missing | Ineligible plan or wrong account context | Official screenshots/docs and an eligible demo organization |
| Only some repositories appear | Viewer permissions | Explain permission-scoped governance; switch to an owner/security-manager account if authorized |
| Advanced Security metrics are empty | Products not licensed/enabled, no scans, or no alerts | Dependabot, Coverage, and free Assessments |
| **Assessments** is missing | Viewer is not an owner/security manager, or organization is ineligible | Existing exported report or official interpretation guide |
| Assessment cannot rerun | 90-day limit or scan already running | Interpret the latest report |
| Code assessment repo is unavailable | Public repo, unsupported language, or selection limit | Select an eligible private/internal repository; explain the 20-repository cap |
| Campaign creation is missing | Role, entitlement, feature availability, or no eligible alerts | Filter findings and walk through the creation guide |
| Secret campaign option is missing | Public-preview rollout or Secret Protection/alert prerequisites | Demonstrate a code campaign and explain the preview |
| Enterprise details are missing | Enterprise owner lacks the required organization role | Stay at organization scope |

## Key takeaways

- **Risk and coverage answer different questions:** alert concentration is not the same as control adoption.
- **Visibility is permission-scoped:** an empty view can mean missing access, data, or enablement rather than low risk.
- **Assessments are discovery tools:** point-in-time reports do not replace continuous Code Security or Secret Protection.
- **Governance needs ownership:** configurations and campaigns turn findings into repeatable enablement and remediation work.

## Discussion prompts

1. Which Coverage gaps are acceptable exceptions, and how will exceptions expire?
2. Which result from a point-in-time assessment justifies enabling continuous protection?
3. Who owns remediation when a high-risk repository has no active maintainer?
4. What SLA and success metric would you attach to a campaign?
5. How should enterprise reporting handle teams that expose only permission-scoped data?
6. When should a Dependabot finding become a campaign or incident rather than a normal update pull request?

## Exit criteria

The lesson is complete when attendees can:

- Find **Risk**, **Coverage**, **Assessments**, **Campaigns**, and **Dependabot** under **Security and quality**.
- Explain why Overview totals may differ from feature-specific findings.
- State who can run each free assessment, what it scans, and the 90-day restriction.
- Describe a code scanning campaign and the public-preview status of secret scanning campaigns.
- Name a useful fallback when licensing, roles, data, or preview rollout blocks a live demo.

## Official references

- [About security overview](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/security-at-scale/about-security-overview)
- [Viewing security insights for organizations and enterprises](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/view-and-interpret-data/analyze-organization-data/viewing-security-insights)
- [Assessing security risk with Risk and findings views](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/view-and-interpret-data/analyze-organization-data/assessing-code-security-risk)
- [Assessing adoption with Coverage and Enablement](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/view-and-interpret-data/analyze-organization-data/assessing-adoption-code-security)
- [Security overview permissions](https://docs.github.com/en/enterprise-cloud@latest/code-security/reference/permissions/security-overview)
- [Running the Secret Risk Assessment](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-at-scale/configure-organization-security/configure-specific-tools/assess-your-secret-risk)
- [Code Security Risk Assessment: eligibility and limits](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/code-scanning/code-security-risk-assessment)
- [Running the Code Security Risk Assessment](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-at-scale/configure-organization-security/configure-specific-tools/assess-your-vulnerability-risk)
- [Viewing assessment reports](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-at-scale/configure-organization-security/configure-specific-tools/viewing-your-security-risk-assessment-reports)
- [Code Security Risk Assessment public-preview announcement](https://github.blog/changelog/2026-04-08-code-security-risk-assessment-available-for-organizations/)
- [About security campaigns](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/security-at-scale/about-security-campaigns)
- [Creating and managing security campaigns](https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/manage-security-alerts/remediate-alerts-at-scale/creating-managing-security-campaigns)
- [Secret scanning campaigns general-availability announcement](https://github.blog/changelog/2025-11-25-secret-scanning-alert-assignees-security-campaigns-are-generally-available/)
- [About Dependabot alerts](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/supply-chain-security/dependabot-alerts)
- [About GitHub Advanced Security products](https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/about-github-advanced-security)

## Reset state

There is no repository state to reset. Delete any draft campaign created solely for practice, but do not delete shared campaigns or rerun assessments unnecessarily. Organization alert counts naturally drift between cohorts.
