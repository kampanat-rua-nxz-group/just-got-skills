---
name: spec-hawk
description: Runs a severity-tagged QA review of Playwright + TypeScript automation specs by spawning the automation-qa-reviewer subagent. Returns a structured report with CRITICAL/HIGH/MEDIUM/LOW/NIT findings, file:line citations, and suggested-fix snippets. Use when the user asks to review, audit, or check automation test files, services, models, or utils in any *-automation repo. Trigger on /spec-hawk and proactively when the user says "review this spec", "check my test", "audit my service", or pastes a file path from a testCases/ or supports/ directory.
---

# Spec Hawk

Spot problems in your automation specs before they reach the team — severity-tagged, line-cited, fix-ready.

## Overview

`/spec-hawk` wraps the `automation-qa-reviewer` subagent: a strict, read-only reviewer built specifically for the `*-automation` repos (lockbox-api-automation, lockbox-bo-api-automation, lockbox-ui-automation, oceanxz-automation, solar-billing-automation). It applies a 10-point checklist — layout, tagging, schema validation, code quality, naming, duplication, complexity, spec classification, and required case matrix — then returns one structured markdown report. It never writes files.

## When to Use

- User pastes a file path from `testCases/` or `supports/` and asks for a review
- User says "check my spec", "review this service", "audit my test", "what's wrong with this file"
- User is about to open a PR on an automation repo and wants a pre-PR sanity check
- User wants to know if a new spec follows repo conventions

**Not for:**
- Generating new test scaffolding (spec-hawk does not write files)
- Reviewing non-automation code (use `/scrutinize` for that)
- Running tests or checking CI output (use `/demo-check` or run commands directly)

## Workflow

### Step 1 — Parse the target

Read the args the user passed. Accepted forms:
- A file path: `testCases/merchant/getWalletAddresses/business.spec.ts`
- A folder: `testCases/settlement/`
- A diff description: `"the new sweep transaction spec"`
- No args: ask the user "Which file or folder should spec-hawk review?"

### Step 2 — Spawn automation-qa-reviewer

Use the `Agent` tool with `subagent_type: "automation-qa-reviewer"`. Write a self-contained prompt that includes:

```
Review <target> in this repo.

Apply the full 10-point checklist. Return one markdown report with severity sections
(CRITICAL / HIGH / MEDIUM / LOW / NIT). Include file:line citations and TypeScript
fix snippets. Do not write or edit any files.
```

Pass the working directory context (repo name, target path) so the subagent can orient itself.

### Step 3 — Relay the report

Relay the subagent's markdown report verbatim to the user. Do not summarize, paraphrase, or trim findings — the user needs the full severity-tagged output to triage.

If the subagent returns an empty report ("no findings"), confirm it ran the full checklist and say so explicitly rather than just "looks good."

### Step 4 — Offer next action

After the report, offer one of:
- "Apply the HIGH/CRITICAL fixes?" → hand off to the user or a dev agent
- "Review another file?" → loop back to Step 1
- "Open a PR?" → remind user that git ops are manual per project rules

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The file looks fine at a glance, I'll skip spawning" | Spec-hawk's value is in the 10-point checklist — gut feel misses layer violations, missing tags, and silent test isolation bugs |
| "The user only asked about one thing, I'll skip the rest of the checklist" | Partial review is worse than no review — it gives false confidence. Run the full checklist, suppress empty sections |
| "I'll write the fix directly instead of showing a snippet" | Spec-hawk is read-only by design. Showing the fix and letting the user apply it prevents accidental overwrites |
| "The subagent isn't available, so I'll skip the review entirely" | If `automation-qa-reviewer` isn't found, apply the checklist inline using the rules from `.qa-rules/api-testing.md` in the active repo |

## Verification

After completing a review, confirm:

- [ ] The subagent was spawned (or the fallback was explicitly triggered)
- [ ] The full 10-point checklist was applied — not a subset
- [ ] Every finding has a `file:line` citation
- [ ] CRITICAL and HIGH findings include a TypeScript fix snippet
- [ ] The report was relayed verbatim — not summarized
- [ ] An offer for next action was made
