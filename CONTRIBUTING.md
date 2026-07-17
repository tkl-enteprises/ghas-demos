# Contributing

Thanks for helping improve the GitHub security workshop. This repo is a teaching tool — every change should make a lesson clearer, more reliable, or more fun to deliver.

## How to add a new lesson

Lessons live under [`lessons/`](lessons/) and follow a strict layout so facilitators can pick any one off the shelf:

```
lessons/[number]-[pillar]-[lesson]/
├── README.md          # the lesson itself (see structure below)
└── *.py               # vulnerable / annotated sample code
```

`[number]` is the two-digit workshop position (`01`–`11`), `[pillar]` is one of `code-security`, `secret-protection`, `supply-chain`, `governance`, or `code-quality`, and `[lesson]` is the concise lesson slug. Keep lessons grouped in that pillar order. Code Quality is a distinct pillar from Code Security even though both use CodeQL infrastructure.

Each lesson `README.md` MUST include these sections, in this order:

1. **Goal** — one sentence: which GitHub security or quality capability does this lesson demonstrate?
2. **Learning objectives** — bullet list of what the attendee can do afterwards.
3. **Estimated time** — minutes, including discussion.
4. **Walkthrough** — numbered steps the facilitator runs live, with explicit "click here in the UI" callouts.
5. **Exit criteria** — observable signals that the lesson worked (e.g. "alert appears on the Security and quality tab within 90 seconds").
6. **Key takeaways** — 2–4 bullets the audience should leave with.
7. **Discussion questions** — open-ended prompts for the room.
8. **Reset state** — exact steps to put the lesson back so the next group sees a clean slate.

## How to test a lesson change

1. **Fork** this repo (don't push directly to `main`).
2. On your fork, enable the required **GitHub Code Security** and **GitHub Secret Protection** capabilities (Settings → Code security).
3. Push your branch and watch the **Security and quality** tab on your fork — every alert the lesson promises should appear within a couple of minutes.
4. Run through the lesson's `Walkthrough` end-to-end with the fork's UI open. If a step references a URL or screenshot, update both.

## Style

- Hands-on, second-person voice ("Open the Security and quality tab", not "The Security and quality tab can be opened").
- Short paragraphs, lots of bullets, screenshots over prose where it helps.
- Match the tone of existing lessons — direct, concrete, no marketing language.

## Branching and pull requests

- All changes land on `main` via PR.
- The `main` branch is protected by a ruleset that requires the **CodeQL**, **Bandit**, and **Dependency Review** checks to pass before merge.
- Keep PRs small and scoped to one lesson where possible.

## Running tests locally

The repo ships a workshop-infrastructure pytest suite under [`tests/`](tests/) that validates static repo invariants (lesson layout, link integrity, workflow paths, script smoke, manifest shape). It does **not** assert security properties of the intentionally-vulnerable demo code — those are the GitHub security scanners' job.

```bash
pip install -r tests/requirements.txt
python -m pytest tests/ -v
```

The same suite runs in CI on every push/PR via the [`tests`](.github/workflows/tests.yml) workflow. It is *not* part of the required-status-checks ruleset on `main`; treat a red `tests` run as an early-warning signal that a recent change drifted the workshop scaffolding.

## Don't add real secrets

This repo's secret-scanning lessons rely on **fake / canary** credentials. Use the existing `FAKE-` marker pattern (see [`lessons/07-secret-protection-secret-scanning/`](lessons/07-secret-protection-secret-scanning/) and [`lessons/08-secret-protection-custom-patterns/`](lessons/08-secret-protection-custom-patterns/)). Never paste a real key, token, or password — even temporarily, even in a branch you plan to delete. If you do, rotate it immediately and tell a maintainer.
