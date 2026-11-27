---
name: tdd
description: Use when the user asks for TDD, a failing test first, or a regression test for a confirmed bug, or when a confirmed bug has a cheap local test path, including the /tdd trigger.
argument-hint: "[defect ticket, failing behavior, or test path]"
---

# tdd — failing test first

Make a bug executable before production code changes: a focused regression test that fails before the fix and passes after it. Prefer no new test over a bad test.

## When to skip a new test

Skip the new test when it needs broad harness setup, brittle mocks, slow end-to-end infrastructure for a small fix, production-only state, vague reproduction steps, or large fixture churn. Use the closest executable check instead: a targeted script, a reproduction command, browser automation, an API call with an assertion, or a log assertion.

A bad test mostly tests mocks, encodes implementation details, depends on timing or shared test data, needs expensive infrastructure for a small fix, or would be deleted right after it proves the fix.

## Workflow

1. **Understand the bug.** State the intended behavior, the current behavior, the affected path, and the smallest observable reproduction. When the input is a ticket from the `defect` skill, use its Steps to Reproduce, Expected Result, and Actual Result.
2. **Choose the narrowest check the repo already uses** for that path: unit, component, API, integration, or Playwright. Follow the repo's existing test layout, naming, tags, and fixtures. Do not add a new framework.
3. **Write the failing test first.** Assert what users can observe, such as response fields, UI state, or stored data, not internals.
4. **Run it before any fix.** It must fail for the intended reason: the assertion that encodes the bug. When it passes, or fails on setup, a selector, or test data, fix the test before touching production code.
5. **Fix only when the user asked for the fix.** Otherwise stop and hand over the failing test with its output as evidence for the developer. A fix is the smallest production change that meets the intended behavior.
6. **Rerun the regression test and the nearby tests.** Confirm they pass. For an intermittent bug, run the test repeatedly and report the pass count.

## Guardrails

- Never change a test to match a wrong implementation.
- Never weaken an existing assertion unless the expected behavior changed, and state the reason.
- Keep the test deterministic: own its test data and wait on conditions, not fixed sleeps.
- Keep the test focused on the bug. Add sibling coverage only after the focused test lands.
- When the user commits, suggest that the failing test lands before the fix in history.

## Report

- **Failing before** — the test name, the command, and the failure output, verbatim and trimmed to the relevant lines.
- **Passing after** — the command and its result, plus any nearby validation.
- **No failing-before evidence** — why it could not be shown, and the closest check used instead.

---

Adapted from `tdd` in poteto's [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT).
