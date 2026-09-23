---
name: create-jira-story-task
description: Use when the user asks to draft, write, or improve a non-defect Jira Story or Task from requirements, notes, or a feature request.
---

# Create Jira Story or Task

Produce a copy-ready Jira work item whose scope and acceptance criteria can be understood without follow-up. Preserve unknowns instead of inventing requirements.

## Workflow

### 1. Classify the work

- **Story** — delivers an observable user or business outcome.
- **Task** — technical, operational, research, or maintenance work without a standalone user outcome.
- **Defect** — invoke `create-bug-ticket` instead and stop this workflow.

When Story and Task both seem plausible, use Story only when the request names a beneficiary and outcome; otherwise use Task.

### 2. Resolve gaps

Extract supported facts from the request and available artifacts. Ask about a missing fact only when it materially changes scope, a Business Rule, or Acceptance Criteria. For a fact that can safely be decided later, write `TBD` and repeat it under Open Questions. Never silently invent product rules, dependencies, or system behavior.

### 3. Draft the ticket

Always identify the issue type, then use these headings in order. Keep every required heading; include an optional heading only when it has supported content.

## Title

Use an action-oriented summary naming the affected capability or component.

## Description

State what must change, why it is needed, and the intended outcome in 2–4 sentences.

## Background

Explain the current situation, motivating problem, and relevant context.

## Business Rules

List permissions, validations, calculations, constraints, and state transitions as atomic numbered rules. Use `TBD` when a required rule remains unresolved.

## User Story / Details

- Story: `As a <beneficiary>, I want <capability>, so that <outcome>.`
- Task: describe the concrete technical or operational work, affected area, and completion boundary.

## Acceptance Criteria

Write independently testable outcomes. Use Given/When/Then for stateful behavior and concise bullets for static constraints. Cover every stated Business Rule without prescribing an implementation unless the requirement does.

## Impact

Optional. Describe affected users, workflows, systems, or measurable value.

## Dependencies

Optional. Name confirmed teams, systems, decisions, or predecessor work.

## Notes

Optional. Record useful implementation, rollout, analytics, or design context that is not a requirement.

## Open Questions

Optional. List unresolved decisions that are explicitly `TBD` elsewhere in the ticket.

## Test Scenarios

Optional. List high-value happy-path, negative, permission, boundary, and regression scenarios supported by the requirements.

### 4. Quality check

Before presenting the ticket, confirm that all six required headings are present, optional headings are non-empty, rules and criteria are traceable, acceptance criteria are observable, and assumptions are labeled. Return the ticket only; do not create or modify a Jira issue.

## Example

For “export filtered transactions for quarterly reconciliation,” classify it as a Story. State the reconciliation need in Background, access and date-filter constraints in Business Rules, express the user outcome under User Story / Details, make each constraint observable in Acceptance Criteria, and put unresolved export-size and processing-mode decisions in Open Questions with matching `TBD` markers.
