# Lesson 07 — Code Quality AI findings

> **Preview behavior is time-sensitive.** AI findings are LLM-generated suggestions for recently merged files. Their count, wording, and availability are not deterministic.

## Goal

Merge safe, inert examples into the default branch and inspect the contextual quality suggestions produced in **Security and quality → Code quality → AI findings**.

## Learning objectives

After this lesson you can:

- Explain when the post-merge AI scan runs.
- Distinguish AI findings from CodeQL-powered Standard findings and PR comments.
- Review suggestions for grammar, correctness, mutation, and performance concerns.
- Open a one-file Autofix PR or delegate one or more files to Copilot cloud agent.
- Explain why an empty AI findings tab does not prove that recently merged code is high quality.

## Estimated time

**~10 min demo + scan wait + 5 min discussion**

## Prerequisites

- GitHub Code Quality is enabled.
- At least one pull request is merged after Code Quality was enabled.
- You have write access to the repository.
- A Copilot license is required only to delegate remediation to Copilot cloud agent; opening a one-file PR from an AI suggestion does not require the cloud agent.

GitHub's official tutorial states that the view can remain empty when the repository is inactive or when the LLM cannot suggest improvements in recent default-branch changes. A direct push or a fixture that was already on the default branch before enablement is not a reliable trigger.

## Example findings

[`ai-findings-fixtures.js`](ai-findings-fixtures.js) exports functions but calls none of them. Importing the file performs no network, filesystem, timer, or console activity.

| Function | Quality concern the AI may identify |
|---|---|
| `buildRegistrationMessage` | User-facing text contains the spelling and grammar errors “were succesfully saved.” |
| `findWorkshopById` | A missing ID silently returns the first workshop instead of an explicit missing value. |
| `normalizeAttendees` | Sorting occurs before trimming, and the function mutates the caller's array and objects. |
| `loadWorkshopDetails` | Independent fetch operations are awaited serially instead of concurrently. |

These examples increase the likelihood of useful suggestions but cannot guarantee exact findings. The model may combine concerns, omit one, or propose a different valid improvement.

## Walkthrough

1. **Inspect the fixture.**

   ```bash
   node --check ai-findings-fixtures.js
   ```

2. **Create the qualifying merge.** Code Quality must already be enabled. Add or change `ai-findings-fixtures.js` on a workshop branch, open a pull request, and merge it into the default branch. The PR merge is the trigger described by GitHub's tutorial.

3. **Wait for the post-merge scan.** Open **Security and quality → Code quality → AI findings**. Results can include findings for up to five recently changed files.

   ![Code Quality AI findings grouped by recently changed file](../../docs/screenshots/code-quality-ai-findings.png)

4. **Open the fixture result.** Compare the explanation and proposed patch with the concerns above. Treat generated output as untrusted review input, not as a deterministic test result.

5. **Review remediation choices.**
   - Use **Open pull request** to apply suggestions for one file.
   - Use **Assign to Copilot** for one or multiple files when Copilot cloud agent is licensed and enabled.
   - Add the finding context to the PR summary so reviewers understand why the change exists.

6. **Observe lifecycle.** After a remediation PR is merged, fixed findings should disappear from the AI findings view after the next scan.

7. **Contrast with lesson 06.** Standard findings come from named CodeQL rules and can annotate PRs. AI findings are a second, post-merge LLM analysis of recently changed default-branch files.

## Exit criteria

The demo has landed when attendees can:

- Explain why the tab was initially empty.
- Identify the merged file and review at least one contextual suggestion.
- Distinguish the post-merge AI scan from Standard findings and PR annotations.
- Explain the one-file PR and multi-file Copilot cloud agent options.

## Key takeaways

- **Merge timing matters:** enable Code Quality first, then merge a PR.
- **Contextual coverage:** the AI can review grammar and cross-cutting code concerns without a named CodeQL rule.
- **No deterministic count:** an absent or different suggestion is expected LLM behavior.
- **Review every patch:** AI explanations and fixes can be incomplete or wrong.

## Discussion questions

1. Which kinds of user-facing grammar issues should block a release?
2. How should reviewers validate a behavior-changing AI suggestion?
3. When is serial asynchronous work intentional rather than a performance problem?
4. Which repositories are suitable for a post-merge AI pilot?

## Reset state

AI findings are transient. If a remediation PR is merged, restore the fixture through a new workshop PR before the next session; that merge also provides a fresh recently changed file. Do not change shared Code Quality or organization policy during a workshop.

## Official references

- [Improve the quality of recently merged code](https://docs.github.com/en/code-security/tutorials/improve-code-quality/improve-recent-merges)
- [About GitHub Code Quality](https://docs.github.com/en/code-security/code-quality/concepts/about-code-quality)
- [GitHub Code Quality billing](https://docs.github.com/en/billing/concepts/product-billing/github-code-quality)
