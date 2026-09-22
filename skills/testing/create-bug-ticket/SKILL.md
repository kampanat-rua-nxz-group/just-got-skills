---
name: create-bug-ticket
description: Use when the user wants to document or file a defect from QA evidence such as text, screenshots, API responses, DevTools output, automation failures, or production monitoring.
---

# Create Bug Ticket

Produce a developer-ready English Jira bug ticket that a developer can reproduce and fix without follow-up.

## Workflow

**Step 0 — Classify the source:**

- Text, screenshot, API response, DevTools output, or manual note: evidence is available; continue to Step 1.
- Local automation test failure: confirm it through Step 0a before drafting.

**Step 0a — Confirm an automation-sourced defect:**

Invoke `debug-mantra`, then:

1. Run the failing test and capture the actual error or stack verbatim.
2. Record whether it is deterministic or intermittent; include the observed rate in Frequency.
3. Localize the failure to product code or test code.

Continue only with a confirmed product defect. Flaky / selector / test-data / stale-assertion failures are test fixes — say so and stop. Use `REFERENCE.md` → **Automation-sourced Bugs** for the triage table and confirmation criteria.

**Step 1 — Extract facts and resolve required gaps:**

- Capture the affected feature or page, actual and expected behavior, environment, severity, and frequency.
- Ask only for genuinely missing facts; ask for an unclear severity or environment before drafting. Infer every supported fact from clear screenshots or other evidence.

**Step 2 — Write the ticket in this ten-section structure:**

1. **Title** — `[Exact Feature/Page/Endpoint] Short specific summary`
   - FE: `[Portfolio Overview - Filter Dropdown] Selected filter resets on page refresh`
   - BE: `[GET /api/v1/portfolio/summary] Returns stale data when coin filter is changed`
   - Use an exact feature, page, or endpoint tag; `[UI]`, `[API]`, and `[Backend]` need an exact replacement.

2. **Environment** — use the FE or BE table in `REFERENCE.md` → **Environment Tables**.

3. **Description** — 2–4 sentences covering the feature, failure, evidence, and scope.

4. **Steps to Reproduce** — numbered steps that anyone can follow with zero prior context.

5. **Expected Result** — state the expected behavior and relevant field names or endpoints.

6. **Actual Result** — include exact errors, observed API calls, and silent failures.

7. **Impact / Severity** — use the table and severity guidance in `REFERENCE.md` → **Severity Selection**.

8. **Root Cause** — state a confirmed or suspected layer, specific detail, and suggested fix; use `likely` or `possibly` for a hypothesis. Select the issue type with `REFERENCE.md` → **Issue Type Definitions**.

9. **Attachments** — table every piece of evidence; otherwise write: `No attachments provided. QA to attach before filing.`

10. **QA Note** — a `> 💡 **QA Note:**` block covering regression scenarios, edge cases, and related components.

Before presenting, apply `REFERENCE.md` → **Tone Contract** and complete its **Quality Checklist**.
