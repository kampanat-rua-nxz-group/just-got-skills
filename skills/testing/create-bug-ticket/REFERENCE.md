# Create Bug Ticket — Reference

Use this file for environment table formats, severity guidelines,
Issue Type definitions, tone rules, and the quality checklist.

---

## Environment Tables

### FE Bug
> Issue visible in UI: rendering, interaction, layout, client-side logic,
> or missing/incorrect API call triggered by user action.

| Field | Detail |
|---|---|
| **Environment** | Staging / Production / Development / UAT |
| **URL** | Full URL where bug was observed |
| **Page / Feature** | Page name and component affected |
| **Browser** | Chrome / Safari / Firefox + version if known |
| **OS** | Windows / macOS / Android / iOS + version if known |
| **Build / Version** | App version if known, otherwise "Not specified" |
| **Frequency** | Always (100%) / Sometimes (intermittent) / Once / Under specific conditions |

### BE Bug
> Issue in API layer: wrong response shape, incorrect data, missing field,
> status code error, or server-side logic failure.

| Field | Detail |
|---|---|
| **Environment** | Staging / Production / Development / UAT |
| **API Endpoint** | HTTP method + full path, e.g. `GET /api/v1/orders` |
| **Request Payload** | Key request params or body (redact sensitive values) |
| **Response Received** | Status code + relevant response body |
| **Build / Version** | API version if known, otherwise "Not specified" |
| **Frequency** | Always (100%) / Sometimes (intermittent) / Once / Under specific conditions |

> **FE + BE bug** — Use FE table; add an **API Endpoint** row after the URL row.

---

## Impact / Severity Table

| Field | Detail |
|---|---|
| **Severity** | Critical / High / Medium / Low |
| **Priority** | Critical / High / Medium / Low |
| **Issue Type** | Select from Issue Type definitions below |
| **Scope** | Single component / Single page / Multiple pages / Platform-wide |
| **Workaround** | ✅ Description of workaround, or ❌ None |
| **Impact** | Plain-language explanation of user / system impact |

### Severity Guidelines

| Severity | Criteria |
|---|---|
| **Critical** | System crash, data loss, security issue, complete feature outage blocking all users |
| **High** | Major feature broken, no workaround, significant user impact |
| **Medium** | Feature partially broken, workaround exists, moderate user impact |
| **Low** | Cosmetic/UI issue, minor UX degradation, no functional impact |

---

## Issue Type Definitions

| # | Issue Type | Description |
|---|---|---|
| 1 | **Environment / Configuration** | Config or infra differences between environments |
| 2 | **Deployment Process** | Error during rollout — incomplete steps, wrong order |
| 3 | **Code Implementation** | Incomplete requirement coverage, PR issues (cherry-pick, missing commits) |
| 4 | **Third-party Service** | External service outage or error impacting the system |
| 5 | **Requirement Change** | AC changed mid-development, unclear requirements, UX/UI changed during sprint |
| 6 | **Miscommunication** | Misalignment between PO, Dev, and QA |
| 7 | **Technical Design** | Changes to technical design that affected system behavior |
| 8 | **Device / OS Compatibility** | Issue specific to certain devices or OS versions |
| 9 | **Performance Limitation** | System unable to handle expected load |
| 10 | **Invalid Bug** | Confirmed working as designed — cannot be deleted from Jira |
| 11 | **Software Compatibility** | Version mismatch, lack of backward compatibility |
| 12 | **Others** | Does not fit any category above |

> When root cause is unconfirmed, make a best judgment and mark as **suspected**.

---

## Common Root Cause Patterns

- BE renamed an API response field without notifying FE → field mapping broken on frontend
- New API endpoint built by BE but never communicated to FE → feature handler not wired up
- UI component not subscribed to global state (theme, auth, locale, toggle) → inconsistent behavior
- URL parameter or feature flag gates a broader initialization block → unrelated features broken
- Wrong API endpoint wired to a component → incomplete or incorrect data returned
- UI shipped before backend API is ready → silent failure on user action
- Missing null/undefined check → crash or empty render when API returns unexpected shape

---

## Automation-sourced Bugs — Triage Before Filing

Reproduce and confirm (see `debug-mantra`), then triage:

| Failure source | Where it goes |
|---|---|
| Flaky test (timing/race) | Fix or quarantine the test — not a Jira product bug |
| Selector / locator drift | Fix the test |
| Stale assertion after intended product change | Update the test |
| Test data / env / auth setup | Fix the harness |
| **Genuine product regression** | ✅ File the Jira bug ticket |

**Confirmation criteria before filing:**
- Reproduced deterministically, or documented as intermittent with observed rate.
- Actual error/stack captured verbatim from the run.
- Root cause localized to product code, not test code.

---

## Tone and Style Rules

- **Always write in English** — regardless of input language
- **Two audiences simultaneously:**
  - Non-technical (PO/PM): Description and Impact — plain language, what broke and why it matters
  - Technical (Dev/QA): Steps, Root Cause, Actual Result — exact endpoints, field names, HTTP methods, error codes
- Write in **third person** ("The chart renders..." not "I saw the chart render...")
- Never use vague language like "something is wrong" or "it doesn't work properly"
- Steps to Reproduce must be reproducible by anyone with zero prior context
- Confirmed root cause → state with confidence; suspected → use "likely", "possibly", "may be caused by"
- Always quantify scope — not "users are affected"; say "all users accessing via direct link"
- If the same root cause pattern appears repeatedly → call it out and recommend a process fix

---

## Quality Checklist

Before presenting the ticket, verify:

- [ ] Title is specific and includes exact component / page / endpoint tag
- [ ] Environment table is complete (mark "Not specified" for unknowns)
- [ ] Steps to Reproduce can be followed by someone with zero prior context
- [ ] Expected and Actual results clearly contrast the two states
- [ ] Severity is justified by the impact description
- [ ] Issue Type is selected and reflects the root cause
- [ ] Root cause references concrete evidence where available
- [ ] QA Note includes at least 2–3 post-fix regression scenarios
- [ ] If a team communication gap is identified, a process recommendation is included
- [ ] If source is a local automation failure, the bug was reproduced and confirmed as a product defect before filing
