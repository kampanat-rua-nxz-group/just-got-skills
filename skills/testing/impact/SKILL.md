---
name: impact
description: Use when the user asks what a change, pull request, or diff could break beyond its own lines, wants a regression-risk or blast-radius check before release, or invokes /impact.
argument-hint: "[PR number, branch, commit range, or file; default: the current branch diff]"
---

# impact — what a change can break

Find what a change can break outside its own diff, then prove the fact its safety depends on by running real code. Listing callers is not the job; a search finds them in seconds. The job is the breakage a search does not show.

A risk report that sounds right is worth nothing until its key facts are proven. Stay read-only toward the project: put probe scripts in a scratch directory and never commit them.

## Evidence levels

Push each fact the change's safety depends on as far down this list as is cheap, and report the level it reached.

1. **Asserted** — you said so. Not evidence on its own.
2. **Cited** — a real `file:line`, or the library source at the pinned version.
3. **Reasoned** — you walked the failure step by step and showed it cannot happen.
4. **Run** — a script or test calls the real code and fails loudly if you are wrong.
5. **Reproduced** — you saw it in the running app or environment.

## Workflow

1. **Resolve the change.** Use the target the user names; otherwise use the diff from the merge base with the base branch through the working tree. Read the diff, the commits, and the PR description when available. List the symbols added, changed, and deleted, and the behavior that now differs, including what the diff does not spell out: defaults, ordering, error paths, and timing.
2. **Name the safety fact.** Most risky-looking changes are safe because of one or two facts, such as "the new field is optional in every consumer's schema". State the fact. When it holds, it clears many risks at once, so spend your time here, not on a long list of maybes.
3. **Look where search stops.**
   - **Contracts:** API response bodies, DB columns and migrations, event or message payloads, file formats, and other services or languages that read the same data.
   - **Configuration:** feature flags, environment variables, defaults, and per-environment settings.
   - **Timing:** async ordering, retries, timeouts, caching and cache invalidation, and teardown.
   - **Dependencies:** library source at the pinned version, plus local patches.
   - **Tests:** tests that cover the changed behavior, tests removed or weakened, mocks that hide the contract, and automation selectors, fixtures, or test data that depend on the changed UI or API.
   - **Downstream:** consumers several hops away, reports, exports, and scheduled jobs.
4. **Rate each risk honestly.** Give how it breaks, the `file:line`, a real likelihood, the cost if it happens, and how to check it. Never invent a caller or an API. A search that finds nothing is an answer; show the search.
5. **Prove the safety fact.** Write the smallest script or test that calls the real code, run it, and paste the command and its output. When it cannot run here, for example because of a missing environment or secret, say why, name the level reached, and give the exact command QA should run.
6. **Turn confirmed risks into regression checks.** For each confirmed risk, name the existing test to run or the new scenario to add, ordered by risk. When the user wants full scenarios, hand the confirmed risks to `scenario` if it is installed.

## Output

- **What changed** — including the part that is not obvious from the diff.
- **Safety fact** — the statement, its evidence level, and the proof (command and output), or `unproven`.
- **Risks** — confirmed risks only: how it breaks, `file:line`, likelihood, cost, and how to check.
- **Cleared** — what you checked and why it is fine.
- **Regression checks** — tests to run or add, highest risk first.
- **Not checked** — what you could not reach, and why.

---

Adapted from `blast-radius` in poteto's [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT).
