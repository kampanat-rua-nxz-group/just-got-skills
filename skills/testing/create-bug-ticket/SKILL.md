---
name: create-bug-ticket
description: >
  Write developer-ready Jira bug tickets from any QA input — text, screenshot,
  API response, DevTools output, or automation failure. Use when the user wants
  to document a bug, file a defect, write a bug report, create a Jira ticket,
  or report an issue found during testing or production monitoring.
---

# Create Bug Ticket

Produce a Jira bug ticket clear enough that any developer can reproduce and fix
the bug without follow-up.

## Workflow

**Step 0 — Classify the source:**
- Screenshot / API response / DevTools / manual note → evidence is already in hand; go to Step 1.
- **Local automation test failure** → reproduce and confirm first (Step 0a).

**Step 0a — Reproduce & confirm (automation only):**
Invoke `debug-mantra`, then:
1. Run the failing test; capture the actual error/stack **verbatim**.
2. Determine determinism — always vs intermittent (record rate for Frequency field).
3. Localize: product code vs test code.

Only a confirmed **product defect** continues to Step 1.
Flaky / selector / test-data / stale-assertion failures are test fixes — say so and stop.
See REFERENCE.md → Automation-sourced Bugs for triage table.

**Step 1 — Extract; ask only for what is genuinely missing:**
- Feature / page affected, actual vs expected behavior
- Environment (Staging / Production / Dev / UAT), Severity, Frequency
- If severity or environment is unclear → ask before writing
- Clear screenshot → infer as much as possible

**Step 2 — Write the ticket in English using this structure:**

1. **Title** — `[Exact Feature/Page/Endpoint] Short specific summary`
   - FE: `[Portfolio Overview - Filter Dropdown] Selected filter resets on page refresh`
   - BE: `[GET /api/v1/portfolio/summary] Returns stale data when coin filter is changed`
   - Never use generic tags like `[UI]` `[API]` `[Backend]`

2. **Environment** — FE table or BE table (see REFERENCE.md)

3. **Description** — 2–4 sentences: what feature, what is broken, evidence/scope

4. **Steps to Reproduce** — numbered; reproducible by anyone with zero prior context

5. **Expected Result** — specific; reference field names / endpoints where relevant

6. **Actual Result** — exact errors quoted, API calls observed or not, silent failures noted

7. **Impact / Severity** — table format (see REFERENCE.md for severity guidelines)

8. **Root Cause** — confirmed or suspected; identify layer and specific detail; suggest fix
   - Use "likely" / "possibly" for suspected causes

9. **Attachments** — table of all evidence; if none: "No attachments provided. QA to attach before filing."

10. **QA Note** — `> 💡 **QA Note:**` block with regression scenarios, edge cases, related components

Before presenting, run the quality checklist in REFERENCE.md.
