---
name: probe
description: Use when an expected result in a test design, mind map, or automation spec is TBD or TBC and the user wants the actual response, such as an error status, code, or message, found from the service's source code or a real API call, or invokes /probe.
argument-hint: "[outline or spec path, endpoint, or case; optional environment]"
---

# probe — fill TBD expected results from code or a live call

Find what the system actually returns for a case whose expected result is still `TBD` or `TBC` in the design. Read the service's source first. Call the real API only when the source is out of reach or does not settle the case.

What you find is **observed behavior**, not a requirement. The system may be wrong. Mark every filled value `@observed`, record its source, and leave the design owner to confirm it.

## Workflow

1. **List the open cases.** For a mind map outline, run:
   ```bash
   python3 <skill-dir>/scripts/list_tbd.py docs/testcases/<feature>-usecase-map.md
   ```
   It prints each `TBD`, `TBC`, or `@TBD` line with its line number and branch path. For automation specs, search for `TBD`, `TBC`, `test.skip`, and `test.fixme`. For each case, note the endpoint, the sample input, and which result fields are open: status, error code, message, or body shape.
2. **Choose the source for each case.**
   - **Code first.** Use this when the service repository is readable here.
   - **Live call.** Use this when the repository is out of reach, when the code path is ambiguous, or when the user wants the deployed behavior.
   - **Both.** Use both when the deployed version may lag the repository. A disagreement means the environment runs different code. Report both values and never pick one.
3. **Read the code path** (step 2 chose code).
   - Record the repository, branch, and commit: `git rev-parse --short HEAD`.
   - Find the route handler by its path or decorator. Follow the request through middleware, guards, validation schemas or DTOs, and the service code, to the branch that matches the case.
   - Find where that branch becomes a response: the thrown error, the exception filter or global error handler, and the error-code constants or translation files that hold the message.
   - Cite `file:line` for each value: status, error code, message, and body shape.
   - Stay read-only toward the service repository.
4. **Make the live call** (step 2 chose a live call).
   - **Use a test environment only.** Take the base URL from the user or the automation repo's config. Never call production.
   - **Read credentials from environment variables.** Never paste a token into a command, the outline, or the report.
   - **Run a control call first.** Send a valid baseline request built from an existing fixture or happy-path sample, and confirm it succeeds. When it fails, stop. Every probe result would be wrong, because the failure is in the setup, auth, or environment.
   - **Change exactly one thing** from the baseline to trigger the case. This matches the `Sample input:` rule in the `mindmap` skill.
   - **Ask before a call that can change state you cannot undo**, such as moving funds, sending a message, or closing an account. A validation error usually fails before any write, but a business-rule failure may not.
   - **Capture each result once:** status, relevant headers such as `Content-Type` and `Retry-After`, and the body. Repeat the call only when the result looks unstable, and report the count.
   - **Redact** tokens, cookies, and personal data before showing output.
   - Keep probe scripts in a scratch directory. Never commit them.
5. **Report, then update.** Present the results table. Then update the artifact the cases came from:
   - **Outline:** replace each resolved `TBD` leaf with the observed value. Change the fork's `@TBD` to `@observed`. Add an Open Questions / Notes entry for each change with the source (`file:line` and commit, or environment and date) and "confirm with <owner>". If the outline came from the `mindmap` skill, rerun its check and render steps.
   - **Automation spec:** update an expected assertion only when the user asked you to prepare the automation. Mark each such assertion with the repo's tag convention, or a one-line `// observed:` comment with its source when the repo has none.
   - Leave a case `TBD` when neither source settles it, and say what would settle it.

## Report

One row per case:

| Case | Source | Observed result | Label | Notes |
|---|---|---|---|---|
| Branch path from step 1 | `file:line` at commit, or environment, method, and path | Status, error code, message, body shape | `cited` (code) or `verified` (live call) | Conflicts, instability, and who confirms |

After the table, list:

- **Still TBD** — cases neither source settled, and what would settle each one.
- **Conflicts** — cases where the code and the live call disagree, with both values.
- **For the design owner** — every `@observed` value that needs confirmation.
