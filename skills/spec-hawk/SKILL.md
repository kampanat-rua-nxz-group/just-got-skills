---
name: spec-hawk
description: Runs a severity-tagged QA review of Playwright + TypeScript automation specs by spawning the automation-qa-reviewer subagent. Returns a structured report with CRITICAL/HIGH/MEDIUM/LOW/NIT findings, file:line citations, and suggested-fix snippets. Use when the user asks to review, audit, or check automation test files, services, models, or utils in a Playwright + TypeScript repo. Trigger on /spec-hawk and proactively when the user says "review this spec", "check my test", "audit my service", or pastes a file path from a test or supports directory.
---

# Spec Hawk

Spot problems in your automation specs before they reach the team — severity-tagged, line-cited, fix-ready.

## Overview

`/spec-hawk` wraps the `automation-qa-reviewer` subagent: a strict, read-only reviewer for **any Playwright + TypeScript automation repo**. The reviewer discovers the repo's own conventions (folder layout, tag scheme, shared package, config module) and then applies an 8-point checklist — layout, tagging/test-management, schema validation, code quality, linting, naming, duplication, and function complexity — returning one structured markdown report. It never writes files.

> **Setup:** spec-hawk needs the `automation-qa-reviewer` agent installed. Copy `agents/automation-qa-reviewer.md` from this repo into `~/.claude/agents/` (global) or `<project>/.claude/agents/`. Without it, spec-hawk runs the inline fallback (Step 2b) but the dedicated agent gives the best results.

## When to Use

- User pastes a file path from a test folder (`testCases/`, `tests/`, `e2e/`) or a `supports/` helper area and asks for a review
- User says "check my spec", "review this service", "audit my test", "what's wrong with this file"
- User is about to open a PR on an automation repo and wants a pre-PR sanity check
- User wants to know if a new spec follows repo conventions

**Not for:**
- Generating new test scaffolding (spec-hawk does not write files)
- Reviewing non-automation code
- Running tests or checking CI output (run commands directly)

## Workflow

### Step 1 — Parse the target

Accept **any** file or folder path the user passes — do not require it to match a particular repo structure. Accepted forms:
- A file path: any `*.spec.ts` (or `*.test.ts`) file, wherever it lives in the repo
- A folder: any directory containing specs
- A diff description: `"the new sweep transaction spec"`
- No args: ask the user "Which file or folder should spec-hawk review?"

> **Recommended layout (not required):** the ideal spec path is
> `testCases/<domain>/<feature>/<feature>.business.spec.ts`. If the target follows
> a clearly different layout, review it as-is and — only if relevant — note the
> deviation under checklist #1 (layout & structure). Never refuse a path for not
> matching this shape.

### Step 2 — Spawn automation-qa-reviewer

Use the `Agent` tool with `subagent_type: "automation-qa-reviewer"`. Write a self-contained prompt that includes:

```
Review <target> in this repo.

Discover the repo's conventions first, then apply the full checklist. Return one
markdown report with severity sections (CRITICAL / HIGH / MEDIUM / LOW / NIT).
Include file:line citations and TypeScript fix snippets. Do not write or edit any files.
```

Pass the working directory context (repo name, target path) so the subagent can orient itself.

### Step 2b — Fallback if the agent isn't installed

If `automation-qa-reviewer` is not available, do **not** skip the review. Run the checklist inline yourself, in read-only mode:
1. Discover the repo's conventions (read `package.json`, the config/constants module, the linter config, and `Glob` the test layout).
2. Apply the same 8-point checklist and severity scale the agent uses.
3. Produce the same structured report format.
If the repo ships its own QA rules doc (e.g. a `.qa-rules/` file or `CLAUDE.md` testing section), fold those in.

### Step 3 — Relay the report

Relay the report verbatim to the user. Do not summarize, paraphrase, or trim findings — the user needs the full severity-tagged output to triage.

If the report is empty ("no findings"), confirm the full checklist ran and say so explicitly rather than just "looks good."

### Step 4 — Offer next action

After the report, offer one of:
- "Apply the HIGH/CRITICAL fixes?" → hand off to the user or a dev agent
- "Review another file?" → loop back to Step 1
- "Open a PR?" → remind the user that git ops are theirs to run

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The file looks fine at a glance, I'll skip spawning" | Spec-hawk's value is in the full checklist — gut feel misses layer violations, missing tags, and silent test isolation bugs |
| "The user only asked about one thing, I'll skip the rest of the checklist" | Partial review is worse than no review — it gives false confidence. Run the full checklist, suppress empty sections |
| "I'll write the fix directly instead of showing a snippet" | Spec-hawk is read-only by design. Showing the fix and letting the user apply it prevents accidental overwrites |
| "The subagent isn't available, so I'll skip the review entirely" | If `automation-qa-reviewer` isn't found, run the inline fallback (Step 2b) — never skip the review |

## Verification

After completing a review, confirm:

- [ ] The subagent was spawned (or the Step 2b fallback was explicitly triggered)
- [ ] The repo's conventions were discovered, not assumed
- [ ] The full checklist was applied — not a subset
- [ ] Every finding has a `file:line` citation
- [ ] CRITICAL and HIGH findings include a TypeScript fix snippet
- [ ] The report was relayed verbatim — not summarized
- [ ] An offer for next action was made
