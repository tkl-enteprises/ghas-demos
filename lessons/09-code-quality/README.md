# Lesson 09 — Code Quality (bonus, preview)

> 🎁 **Bonus lesson, preview product.** Code Quality is a *separate* GitHub product that runs on the **same CodeQL engine** as code scanning, but with a **maintainability + reliability** query pack instead of security queries. As of late 2025 it's billed as **Action minutes (NOT GHAS seats)** and is in **Preview** — the UI may change before GA.

The point of this lesson is contrast: same engine, same code, *very* different verdict. This repo has 132 security findings and 0 standard quality findings. "Secure" and "high-quality" are independent axes; you need both query packs to see both views.

## Goal

Show the room that the CodeQL engine they just learned to read is also what powers Code Quality — and that "secure" and "high-quality" are two independent verdicts on the same source code.

## Learning objectives

After this lesson you can:

- Explain how Code Quality and Code Scanning relate (same engine, different query suite).
- Locate the **Code quality** tab under repo `Security and quality` and read both Standard and AI findings.
- Articulate why quality findings are **advisory only** — not gated by push protection or branch rulesets.
- Speak to the buying-conversation impact: Action minutes vs GHAS seats.

## Estimated time

**~5 min demo + 5 min discussion**

## Prerequisites

- [Lesson 1 — CodeQL Code Scanning](../01-codeql-code-scanning/) — you need the "alerts → dataflow → severity" mental model from lesson 1 for the side-by-side comparison to land.
- Ideally [Lesson 3 — Custom CodeQL Queries](../03-custom-codeql-queries/) too — once attendees understand that the engine runs whatever queries you point it at, the "same engine, different queries" pitch for Code Quality is one sentence.
- Repo → `Settings → Code security` shows **Code quality** as *Enabled* (Preview tag visible).

## What's in this lesson

Nothing under this folder needs to be *run* — every step happens in the GitHub UI. Attendees only browse the alerts page; they don't push code. There is no `solution.md` because there's no remediation flow to walk: quality findings are advisory.

## Walkthrough

1. **Show that Code Quality is enabled.** Repo → `Settings → Code security`. Scroll to the **Code quality** row — it's marked *Enabled (Preview)*. This is what makes the Security tab show the extra rows in step 5.

   ![Settings → Code security with the Code quality row toggled on, "Preview" tag visible](../../docs/screenshots/code-quality-enabled.png)

2. **Look at Standard findings.** `Security and quality → Code quality → Standard findings` (left nav). The repo scores **Excellent** on both Maintainability and Reliability, with **No open findings**. Same dataflow engine that just lit up 32 security alerts on this codebase says the *quality* of that code is fine — and that contrast is the headline.

   ![Code Quality Standard findings page: Excellent maintainability, Excellent reliability, 0 standard findings, 5 AI findings](../../docs/screenshots/code-quality-findings.png)

3. **Switch to AI findings.** Same left nav, *AI findings* tab. There are **5 findings on `FACILITATOR.md`** — the AI scan looks at recently-changed files (markdown counts), and FACILITATOR.md was just updated. Click into one finding to show the suggestion UI. **Do not** click *Assign to Copilot* during a workshop — it costs Copilot tokens and you don't get the suggestion in time to keep the audience engaged.

   ![Code Quality AI findings: 5 findings, all on FACILITATOR.md, with category labels (Documentation / Style / Clarity)](../../docs/screenshots/code-quality-ai-findings.png)

4. **Compare side-by-side with Code Scanning.** Click `Code scanning` in the same left nav. **Same UI shell.** Same Tool / Severity / Branch filters. Same alert detail layout. The only thing that changed is the *Tool* filter value: `CodeQL` (32 alerts, security queries) vs `CodeQL: Code Quality` (0 standard alerts, quality queries). Land the punchline: **same engine, different queries.**

5. **Show the org-level Enabled list.** Org → `Settings → Code security → Configurations` (or the security overview Coverage view). Code Quality now shows up as a 6th row in the Enabled features list alongside CodeQL, Secret scanning, Push protection, Dependabot alerts, and Dependabot security updates.

   ![Org security overview with Code Quality listed as an Enabled feature row alongside the five GHAS features](../../docs/screenshots/security-overview-with-code-quality.png)

## Talking points

While you're on each tab above, drop these into the room:

- **Same engine, different queries.** CodeQL Code Quality runs on identical infrastructure to security CodeQL — same compiler, same database, same dataflow engine. The maintainability + reliability query packs are just another `.qlpack` you point at the database. Authoring a custom *quality* query is the same QL syntax as authoring a custom *security* query (lesson 3).
- **Billing.** Code Quality is metered as **Action minutes**, not GHAS seats. Important for the buying conversation: a customer who can't justify GHAS seats can still afford Code Quality if their existing Actions minute budget can absorb it.
- **Status.** **Preview** as of late 2025 — the UI is still moving and there's no SLA. Set expectations with the room.
- **No push protection / no ruleset gating.** Quality findings are **advisory only**. You cannot block a merge on a quality finding the way you can block on a CodeQL security finding via branch protection. If a team wants to gate on quality, they have to wire that themselves with a custom required-status check.

## Exit criteria

The demo has landed when:

- Attendees can describe Code Quality in one sentence: "same CodeQL engine, maintainability + reliability queries instead of security queries."
- Attendees correctly identify that quality findings are advisory and **not** push-protection-blockable.
- Attendees notice the difference between **Standard findings** (full CodeQL pack on the whole repo) and **AI findings** (LLM scan focused on recently-changed files) — and don't conflate the two.

## Key takeaways

- **Same engine, different queries.** Code Quality and Code Scanning share the CodeQL infrastructure — only the query pack differs.
- **Secure ≠ high-quality.** This repo's 132 security findings + 0 standard quality findings is the headline proof: you need both query packs to see both views.
- **Advisory only.** Quality findings don't gate merges — push protection / branch rulesets don't apply.
- **Action minutes, not GHAS seats.** Different billing surface than the rest of this workshop.

## Discussion questions

1. "Same engine, different queries — how would you author a custom *quality* query for your team? (Same QL syntax as lesson 3 — only the metadata `@kind` and the query suite tag changes.)"
2. "When would advisory-only quality findings become a blocker for a team? (When platform owns the rollout target and a 'no-new-quality-debt' policy is the cultural lever you have.)"
3. "Should this repo gate merges on quality findings? Why or why not? (No — workshop repo, intentionally vulnerable, would conflate two failure modes for attendees. In a production repo: maybe, on a *delta* basis, never on absolute counts.)"
4. "How does Code Quality billing (Action minutes) change the buying conversation versus GHAS seats? (Lower-friction path-to-value for teams with constrained licensing budgets but available Actions minutes; positions Code Quality as a developer-experience product, not a security-team product.)"
5. "Why did the AI findings light up on `FACILITATOR.md` (a markdown file) but Standard found zero alerts on the Python source? (AI scan focuses on recently-changed files — FACILITATOR.md was just edited. Standard runs the full CodeQL maintainability pack against the whole repo, where the actual *code* is small, simple, and not maintainability-flawed.)"

## Reset state

Trivial — nothing to reset. Attendees only browse the alerts UI; they don't push code, don't trigger workflows, don't change settings. The next cohort sees an identical Code Quality page on first visit.

```bash
git checkout main && git pull
```

If a future facilitator runs `Assign to Copilot` on an AI finding during a session, the suggestion thread persists on the alert and is visible to the next cohort. That's not a problem — it actually strengthens the demo by giving the room a real Copilot diff to read instead of a blank slate.
