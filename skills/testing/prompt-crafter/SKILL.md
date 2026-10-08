---
name: prompt-crafter
description: Use when turning a testing brief, requirements, or reference data into a structured prompt for an AI provider, including prompts that request an XMind deliverable.
---

# Prompt Crafter

Turn the user's testing brief into one ready-to-send AI prompt. This skill writes prompt text; it does not generate or render local XMind files. Treat the brief as source material: preserve its intent and facts, and do not turn the request to create a prompt into a request for the provider to create a skill.

## XMind output requests

- When the user wants the AI provider's output as XMind, set **Target Output Format** to an editable `.xmind` file and ask for the file as a downloadable or attached deliverable. Make clear that a Markdown outline alone does not meet the requested format.
- Describe a readable topic hierarchy: a root for the feature or API, branches for the major scenario groups, and child topics for scenarios and their expected results. Follow any taxonomy the user supplied; otherwise keep the grouping appropriate to the brief.
- If the provider's environment cannot create or attach `.xmind` files, ask it to state that limitation and provide a structured outline as a fallback. Never describe an outline as an XMind file.

Return only the ready-to-send prompt unless the user asks for analysis or alternatives.

## Workflow

1. **Identify the provider's task.** Extract the action and deliverable the AI provider should perform. Separate that task from instructions about how to prepare the prompt.
2. **Collect the inputs.** Find the system role, target output format, domain knowledge, primary goal, success criteria, constraints, data restrictions, and reference data. Keep source labels and identifiers, including document IDs, versions, commit references, and metrics.
3. **Resolve gaps.** Use explicit reference data to fill obvious template placeholders. When supplied facts conflict or a required detail cannot be inferred safely, preserve the conflict or mark the detail `[NEEDS INPUT: ...]` in the prompt. Ask a focused question only when the missing value prevents a usable prompt.
4. **Write the provider prompt** in the structure below. Make success criteria measurable and describe any required output structure in enough detail to guide the provider. Keep exclusions and data restrictions explicit.
5. **Check fidelity.** Confirm every material input is represented, the requested deliverable is clear, and no unsupported requirement or data has been added.

Keep unresolved input markers inside the prompt so the user can fill them before sending.

## Prompt structure

```markdown
# AI Prompt Specification for [Team or Use]

## 1. Context
- **System Role:** [role]
- **Target Output Format:** [schema, fields, or structure]
- **Domain Knowledge Required:** [domain and scope]
- **Reference Data:** [sources, versions, dates, configuration state, metrics]

## 2. Task Specification
**Primary Goal:**
[Action verb + specific deliverable]

**Success Criteria:**
- [Measurable criterion]
- [Required metrics or values]
- [Successful output characteristics or example, if supplied]

## 3. Constraints & Negative Patterns
**Constraints:**
1. [Required inclusion or exclusion]
2. [Compatibility requirement]

**Data Restrictions:**
- [Allowed sources, API versions, schema versions, or data boundaries]
```

Adapt labels to the user's domain while retaining the three sections and their required information. Do not invent examples, metrics, schema fields, or reference values to make the prompt look complete.

## Example

Input: Test Engineer; Cloud Computing API v3.x; generate cases for `#REQ-ID-12345`; map functional and non-functional requirements to test scenarios with AI model validation; exclude deprecated requirements and endpoints; reference schema v3.7.1, database state `latest_commit_20240115`, and coverage target ≥85%.

Provider prompt:

```markdown
# AI Prompt Specification for Testing Team

## 1. Context
- **System Role:** Test Engineer
- **Target Output Format:** An editable `.xmind` file, attached or provided as a download. Use a root topic for the API, branches for major scenario groups, and child topics for scenarios, expected results, and relevant AI model validation results. A Markdown outline alone is not sufficient; if file attachment is unavailable, state that and provide a structured outline.
- **Domain Knowledge Required:** Cloud Computing API v3.x
- **Reference Data:** Requirements document `#REQ-ID-12345`; schema v3.7.1; database state `latest_commit_20240115`; test coverage target ≥85% of requirements traceable to tests.

## 2. Task Specification
**Primary Goal:**
Generate test scenarios for `#REQ-ID-12345`, mapping its functional and non-functional requirements to scenarios and including AI model validation.

**Success Criteria:**
- Deliver a valid, editable `.xmind` file; a Markdown outline alone does not satisfy the requested format.
- At least 85% of eligible requirements are traceable to one or more test scenarios.
- Each scenario identifies the requirement it covers.
- Use schema v3.7.1 for schema-dependent validation.
- Report the coverage achieved and identify uncovered eligible requirements.

## 3. Constraints & Negative Patterns
**Constraints:**
1. Exclude requirements marked `deprecated` in the supplied system configuration data.
2. Do not reference deprecated API endpoints or versioned interfaces.
3. Maintain compatibility with schema v3.7.1.

**Data Restrictions:**
- Use the requirements document, system configuration, and database state `latest_commit_20240115` as the supplied reference data.
- Apply only schema v3.7.1. If the referenced configuration or database state is unavailable, identify that limitation instead of assuming its contents.
```
