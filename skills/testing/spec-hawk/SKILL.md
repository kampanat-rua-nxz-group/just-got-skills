---
name: spec-hawk
description: Use when reviewing or auditing Playwright and TypeScript automation specs, tests, services, models, helpers, or utilities, including pre-PR checks and the /spec-hawk trigger.
argument-hint: "[file-or-folder path]"
---

# Spec Hawk

Review Playwright + TypeScript automation in read-only mode. Discover the repo's conventions, then apply the nine-area checklist: layout, tagging/test-management, schema validation, code quality, linting, naming, duplication, function complexity, and race-prone shared test data. Return severity-tagged findings with file:line citations and TypeScript fix snippets.

This skill reviews existing automation code; generating test scaffolding, running tests, and checking CI output are outside its scope.

## Workflow

### Step 1 — Resolve the target

Accept **any** file or folder path the user passes — do not require it to match a particular repo structure. Accepted forms:
- A file path: a spec, test, service, model, helper, or utility, wherever it lives in the repo
- A folder: any directory containing automation code
- A diff description: `"the new sweep transaction spec"`
- No args: ask the user "Which file or folder should spec-hawk review?"

> **Recommended layout (not required):** the ideal spec path is
> `testCases/<domain>/<feature>/<feature>.business.spec.ts`. If the target follows
> a clearly different layout, review it as-is and — only if relevant — note the
> deviation under checklist #1 (layout & structure). Never refuse a path for not
> matching this shape.

### Step 2 — Select the reviewer or inline fallback

If the environment can invoke the dedicated reviewer `automation-qa-reviewer`, delegate the review with the working directory, repo name, resolved target, and a self-contained prompt:

```
Review <target> in this repo.

Discover the repo's conventions first, then apply the full nine-area checklist. Return one
markdown report with severity sections (CRITICAL / HIGH / MEDIUM / LOW / NIT).
Include file:line citations and TypeScript fix snippets. Do not write or edit any files.
```

If the dedicated reviewer is unavailable, run the inline fallback yourself in read-only mode. Read [CHECKLIST.md](CHECKLIST.md), bundled next to this skill, for discovery, all nine checklist areas, severity definitions, and the report format. Use available file-reading and file-search capabilities to inspect the repo's configuration and test layout, then apply the full contract.

In either branch, include the repo's QA rules (e.g. a `.qa-rules/` file or `CLAUDE.md` testing section) when present. Review the named target, include file:line citations for every finding and TypeScript fix snippets for CRITICAL/HIGH findings, and suppress empty severity sections.

### Step 3 — Relay the report

Relay the report verbatim to the user. Do not summarize, paraphrase, or trim findings — the user needs the full severity-tagged output to triage.

If the report is empty ("no findings"), confirm the full checklist ran and say so explicitly rather than just "looks good."

### Step 4 — Offer next action

After the report, offer one of:
- "Apply the HIGH/CRITICAL fixes?" → hand off to the user or a dev agent
- "Review another file?" → loop back to Step 1
- "Open a PR?" → remind the user that git ops are theirs to run

## Conditional setup: Claude Code

When using Claude Code, the dedicated reviewer can be installed by copying `agents/automation-qa-reviewer.md` from this repo into `~/.claude/agents/` (global) or `<project>/.claude/agents/`. If installed, invoke the `Agent` tool with `subagent_type: "automation-qa-reviewer"` and the Step 2 prompt. Without that agent or invocation capability, use the inline fallback.
