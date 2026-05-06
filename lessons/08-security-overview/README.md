# Lesson 8 — Security Overview (Org-level Governance)

> Docs-only lesson. There is no code in this folder — every step happens in the GitHub UI.

## Goal

Walk attendees through the **org-level Security Overview** at [https://github.com/orgs/tkl-enteprises/security/overview](https://github.com/orgs/tkl-enteprises/security/overview) so they can answer the question every CISO eventually asks: *"How is GHAS actually doing across all our repos?"*

This is the **GHAS governance story** — the upsell vs. the free, public-repo features the previous lessons demonstrated. Per-repo alerts are great for developers; an org-wide rollup is what security and compliance teams need. Org-level views require a **GHAS license**, which [`tkl-enteprises`](https://github.com/tkl-enteprises) has.

## What it shows

The Security Overview surface bundles four jobs into one tab:

- **Coverage** — which repos have CodeQL / Dependabot / secret scanning **enabled**, broken out per feature. Answers *"are we even running the scanners everywhere?"*
- **Risk** — open alerts grouped by repo, severity, and feature. Answers *"where is the most exposure right now?"*
- **Alerts** — a flat, filterable list of every open finding across the org. Answers *"show me every critical SQL injection alert across the company."*
- **Configurations** — security configurations (policy bundles) that admins apply to repos to roll out CodeQL, Dependabot, and secret scanning settings consistently. Answers *"how do we make sure new repos start secure by default?"*

## Step-by-step navigation

1. Go to the org page: [https://github.com/tkl-enteprises](https://github.com/tkl-enteprises).
2. Click the **`Security`** tab in the org-level top nav (not the repo-level one).
3. The left rail now shows the Security Overview sub-pages. Click through them in this order:
   1. **Overview** — the landing dashboard. Numbers across the top, trend tiles below.
   2. **Coverage** — feature-by-feature, repo-by-repo enablement matrix. Filter by *Not enabled* to find your gaps.
   3. **Risk** — heatmap-style view of open alerts. Sort by severity to find the worst offenders.
   4. **Alerts** — the cross-repo alert list. Combine filters: `severity:critical tool:codeql` is a great starter.
   5. **Configurations** — policy bundles. See *Mention security configurations* below.
4. 📸 Insert screenshot here — Overview dashboard with the trend tiles visible.
5. 📸 Insert screenshot here — Coverage view filtered to *Not enabled*.
6. 📸 Insert screenshot here — Risk view sorted by severity.

## Security configurations

Security configurations are **named, reusable policy bundles** that an org admin defines once and applies to many repos. They let you say *"these 50 repos all get CodeQL on default queries, Dependabot alerts on, secret scanning + push protection on, and they auto-apply to any new repo created in the `backend` team."*

- Open: [https://github.com/organizations/tkl-enteprises/settings/security_products](https://github.com/organizations/tkl-enteprises/settings/security_products)
- The **default `GitHub recommended` configuration** ships out of the box. New repos in the org can be auto-enrolled into it.
- You can clone the recommended config to make a custom one (e.g. `prod-tier`, `internal-only`) and apply it selectively.
- 📸 Insert screenshot here — the `GitHub recommended` configuration detail page with the feature toggles visible.

## Security campaigns (paid feature)

[Security campaigns](https://docs.github.com/en/code-security/security-campaigns) let a security team **batch-assign a set of related alerts** to the engineering teams who own them, with a deadline and progress tracking. The mental model: a campaign is a project board for "fix these N alerts by Friday," scoped across many repos at once.

- Useful when a new high-severity advisory drops and you need to chase down every affected repo without spamming individual alert links into chats.
- Campaigns are a **paid GHAS feature** and require admin permissions on the org.
- 📸 Insert screenshot here — a campaign detail page showing assigned repos and progress bars.

## Discussion prompts

Use these to spark the room — don't try to answer them all yourself.

1. **"How would you onboard a new repo into your org's security configuration?"** Auto-enrollment vs. manual apply. What changes when the team behind the repo hasn't asked for security review yet?
2. **"How would you measure GHAS coverage across 100+ repos?"** Coverage view is the visual answer; the [GraphQL API](https://docs.github.com/en/graphql) is the programmatic answer for dashboards. What does "covered" actually mean when not every repo runs every language CodeQL supports?
3. **"What's the SLA for a critical CodeQL alert in your org today?"** Most teams don't have one. The Risk view is what surfaces the gap.
4. **"Who owns triage when an alert is filed against a repo with no clear maintainer?"** This is the org-design conversation security campaigns are meant to enable.

## Where this fits in the workshop

This is the **closer** lesson. By this point, attendees have seen each pillar fire on a single repo. Lesson 8 is the moment to zoom out and show that the same data feeds an org-wide governance surface — which is the conversation that turns "we use GHAS" into "we manage GHAS."
