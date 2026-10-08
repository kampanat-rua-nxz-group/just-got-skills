---
name: usecase-map
description: Use when the user asks for a QA use-case map, test-case mind map, scenario coverage, or validation and business-flow coverage for a feature, user story, or API specification.
argument-hint: "[feature description, user story, or spec]"
---

# Use Case Map

Turn feature requirements into a QA use-case mind map: the agent writes a Markdown outline, then `scripts/md2xmind.py` renders it to `.xmind`.

## Workflow

1. **Gather context** — read the feature description, user story, acceptance criteria, spec, and design doc, including error codes, messages, and limits. Ask only when ambiguity prevents mapping; handle undocumented values as described below.
2. **Build the map** using the taxonomy below. End every scenario with expected-result leaves; bold scenario conditions that need attention in the Markdown outline.
3. **Review coverage** and populate Coverage Gaps from the completed trees.
4. **Save the outline** as plain Markdown at `docs/testcases/<feature>-usecase-map.md` in the project repo. Create the directory if needed; omit frontmatter.
5. **Render** the `.xmind` beside the outline. Resolve `<skill-dir>` to the directory containing this loaded `SKILL.md`:
   ```bash
   python3 <skill-dir>/scripts/md2xmind.py docs/testcases/<feature>-usecase-map.md \
     -o "docs/testcases/<Feature Name>.xmind"
   ```
   Use the platform opener when desktop access is available (`open` on macOS, `xdg-open` on Linux); otherwise report the generated path.

Outline = source of truth. Treat `.xmind` as a disposable rendering. Before regenerating, copy any direct `.xmind` edits back into the outline.

## Taxonomy (five branches, fixed order)

Use the API or feature group as the root and `##` for each branch.

### 1. Validation Cases

Build an input matrix under each endpoint. Use these sub-branches **in order**, omitting those that do not apply:

1. **Method** → `invalid method` → HTTP 405
2. **Path/Endpoint** → `invalid path` → HTTP 404
3. **Headers** → one node **per header** → `Omit field`, `Empty/whitespace`, mismatch/wrong value
4. **Request body** (when present) → one node **per field** → omit, empty, format, boundary, type mismatch
5. **Query parameters** → one node **per parameter** → omit, empty/whitespace, format, boundary, type mismatch
6. **Path parameters** → one node **per parameter** → applicable format, boundary, type mismatch cases

Group query cases as endpoint → Query parameters → parameter name → case; keep each parameter’s cases together, including on non-GET endpoints.

Every validation case includes a `Sample input:` child with concrete request data before its expected-result leaves. Supply representative values for each relevant equivalence class: omitted, empty (`?limit=`), whitespace (`?limit=%20`), malformed, wrong type, and boundaries just below/at/above documented limits. Distinguish omission from the literal string `null`. Keep other inputs valid; split samples into separate cases when expected outcomes differ. Use safe synthetic values; if a limit or fixture is unknown, identify the missing prerequisite in Open Questions / Notes and mark the affected case `@TBD` rather than inventing it.

For Method and Path/Endpoint cases, use the [default routing error bodies](REFERENCE.md#default-routing-errors).

Cover all schema validation here. Business Scenarios assumes valid input and covers subsequent decisions.

### 2. Business Scenarios (gated decision tree)

Build one decision tree per endpoint. At each gate, label the passing branch with the condition that was met (for example, `Authenticated`, `Amount within allowed range`, or `Balance sufficient`) and nest the next gate beneath it. Place failure conditions as siblings, each ending in error-result leaves. Attach success-result leaves directly beneath the final passing condition; the route to success should read as a sequence of met conditions. Record the schema-valid input assumption under Open Questions / Notes, scoped to the endpoint.

**Gate order** — record each skipped gate and its reason under Open Questions / Notes; an unexplained omission is a coverage gap:

1. **Service reachable?** → fail `@edge`
2. **Dependencies available?** → fail `@edge` — one gate per dependency
3. **Authenticated?** → fail `@security` — record a skip if public endpoint
4. **Authorized?** → fail `@security` — record a skip if no roles/ownership
5. **Business rules** (limits, allowed state/transition) → fail per rule
6. **Resource/state** (balance, existence, idempotency) → fail per check

After the last applicable gate, write the successful HTTP status and response assertions as children of the final passing condition.

For flows spanning multiple endpoints, add a `## Journey: <name>` tree with sequential calls as gates.

### 3. Cross-cutting (Security & Edge)

Cover concerns outside the decision path or spanning multiple points. Keep authentication and authorization in gates 3–4, and infrastructure failures in gates 1–2.

- **Security** — injection, oversized payload, info leakage, rate limiting
- **Edge Cases** — concurrency/races, timeout ambiguity, unicode, null bytes, boundary timing

### 4. Open Questions / Notes

Use a visible `## Open Questions / Notes` parent with ordinary bullet children for unresolved questions, source/spec references, assumptions, skipped-gate reasons, and `Prep:`/`Steps:`. Group entries by endpoint and name the affected parameter or scenario so readers can locate it without per-node note references. Keep sample inputs and expected results in their cases. Do not attach blockquote notes (`>`) or note-reference markers to individual nodes.

### 5. Coverage Gaps

Place this branch last. List every:

- **`@TBD` / `TBD` forks** — forks with undocumented values
- **Skipped gates** — gates recorded in Open Questions / Notes
- **Continuation with no fail fork** — passing branches without failure siblings

## Expected results are leaf topics, not notes

Write each expected assertion from the design doc as a separate leaf under its scenario:

```markdown
- amount < minimum required
  - HTTP Status 400
  - error code LB_API_AMT_001
  - message "amount below minimum"
- amount within allowed range
  - HTTP Status 200
  - <key success-response assertions>
```

Use `TBD` for undocumented result fields and tag the affected fork `@TBD`. If the code is known but the message is not, only the message becomes `TBD`.

Omit `UC-V1`-style ID prefixes.

## Automation labels

- `@mock-only` — requires fault injection; name the harness in `Prep:` under Open Questions / Notes
- `@nondeterministic` — trigger cannot be forced; record the invariant and repeat strategy under Open Questions / Notes
- `@manual` — unsafe or impossible to automate
- `@TBD` — behavior is undefined; write the test and mark it skipped until the contract is defined

## Outline conventions

For format examples, read the [annotated example](REFERENCE.md#full-annotated-example). For rendering errors or XMind compatibility, read the [operational notes](REFERENCE.md#notes).

- `#` root (one only), `##` branches, `-` bullets with 2-space indent
- `**text**` → highlight a scenario condition in Markdown; XMind titles remain plain text. `[P1]`–`[P3]` → priority (optional); `@label` → label
- `<br>` inside title → line break (prefer separate siblings)
- `[pos]`/`[neg]` prefix for positive/negative variants nested under their scenario
