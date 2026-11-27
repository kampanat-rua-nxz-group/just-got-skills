---
name: usecase
description: Use when the user asks for a QA use-case map, test-case mind map, scenario coverage, or validation and business-flow coverage for a feature, user story, or API specification.
argument-hint: "[feature description, user story, or spec]"
---

# Use Case Map

Turn feature requirements into a QA use-case mind map: the agent writes a Markdown outline, then `scripts/md2xmind.py` renders it to `.xmind`.

## Workflow

1. **Gather context** — read the feature description, user story, acceptance criteria, spec, and design doc, including error codes, messages, and limits. Ask only when ambiguity prevents mapping; handle undocumented values as described below.
2. **Build the map** using the taxonomy below. Put expected-result leaves under each sample input/data test; bold scenario conditions that need attention in the Markdown outline.
3. **Review coverage** and populate Coverage Gaps from the completed trees. Before saving, check each Business Scenarios and Journey tree against the nesting rule in section 2: no `continue` leaf, no run of gate siblings at one indent, and every gate's passing branch contains the next gate. Also check Journeys: none runs deeper than about 10 levels, a long one is split by phase and numbered, each piece ends on a pointer to the next, and each piece is itself a chain, not one gate over a flat list of outcomes. Fix any tree that fails.
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

Every validation case includes a `Sample input:` child with concrete request data. Nest that input's expected-result leaves beneath it. Supply representative values for each relevant equivalence class: omitted, empty (`?limit=`), whitespace (`?limit=%20`), malformed, wrong type, and boundaries just below/at/above documented limits. Distinguish omission from the literal string `null`. Keep other inputs valid; split samples into separate cases when expected outcomes differ. Use safe synthetic values; if a limit or fixture is unknown, identify the missing prerequisite in Open Questions / Notes and mark the affected case `@TBD` rather than inventing it.

For Method and Path/Endpoint cases, use the [default routing error bodies](REFERENCE.md#default-routing-errors).

Cover all schema validation here. Business Scenarios assumes valid input and covers subsequent decisions.

### 2. Business Scenarios (gated decision tree)

Build one decision tree per endpoint. At each gate, label the passing branch with the condition that was met (for example, `Authenticated`, `Amount within allowed range`, or `Balance sufficient`) and nest the next gate beneath it. Place failure conditions as siblings. Under each terminal failure or success condition, add a `Sample data test:` child with a concrete fixture or trigger, then nest its expected-result leaves beneath it. The route to success should read as a sequence of met conditions. Record the schema-valid input assumption under Open Questions / Notes, scoped to the endpoint.

**Gate order** — record each skipped gate and its reason under Open Questions / Notes; an unexplained omission is a coverage gap:

1. **Service reachable?** → fail `@edge`
2. **Dependencies available?** → fail `@edge` — one gate per dependency
3. **Authenticated?** → fail `@security` — record a skip if public endpoint
4. **Authorized?** → fail `@security` — record a skip if no roles/ownership
5. **Business rules** (limits, allowed state/transition) → fail per rule
6. **Resource/state** (balance, existence, idempotency) → fail per check

After the last applicable gate, add the success sample data test beneath the final passing condition and nest the successful HTTP status and response assertions beneath that sample.

**Nest the chain; never list the gates flat.** Each gate is a node whose children are its failure conditions plus exactly one passing branch. The next gate sits inside that passing branch, so the success path gets one level deeper per gate and reads top to bottom as a story. A gate's passing branch is always a node of its own. A `→ continue` or `continue` leaf is not a passing branch, and a row of gate siblings at one indent level is the flat shape this section forbids, however it is labelled.

Wrong, flat. The reader must rebuild the order in their head:

```markdown
- Submit withdrawal
  - Authenticated?
    - Invalid key
      - HTTP Status 401
    - authenticated → continue
  - Amount ≥ minimum?
    - Below minimum
      - HTTP Status 400
    - meets minimum → continue
  - Balance sufficient?
    - Insufficient
      - HTTP Status 400
    - sufficient → Success
```

Right, nested. Each passing branch holds the next gate:

```markdown
- Submit withdrawal
  - Authenticated?
    - Invalid key
      - HTTP Status 401
    - Authenticated
      - Amount ≥ minimum?
        - Below minimum
          - HTTP Status 400
        - Amount meets minimum
          - Balance sufficient?
            - Insufficient
              - HTTP Status 400
            - Balance sufficient → Success
              - HTTP Status 200
```

The same rule applies inside a Journey and inside a state machine such as a worker or checker. Where a state offers alternatives rather than an order (for example the row's status), list the states as siblings, then nest each state's own checks inside it. When a map already in the repo has a flat Business Scenarios section, restructure it to this shape rather than copying its style.

For flows spanning multiple endpoints, add a `## Journey: <name>` tree with sequential calls as gates, nested the same way.

**Split a long Journey by phase, and keep each piece a chain.** A tree that runs deeper than about 10 levels, or that a reader cannot hold on one screen, is split into numbered Journeys at the natural phase boundaries of the flow (for example Claim, Prepare, Send, Proof). Splitting shortens the tree. It does not replace the chain.

- Name the pieces in order: `Journey: <flow> (1 of 4) — <phase>`. Add a note under each title saying where it starts (`Starts from a claimed row (Journey 1)`) and where it ends.
- End each piece on a leaf that points to the next one (`Committed → continues in Journey 3 (Send)`), so the sequence survives across trees. A pointer leaf at a phase boundary is allowed. It is the only place a `continue`-style leaf is.
- Inside each piece, apply the nesting rule again. Put the failure and alternative outcomes of one step as siblings under that step, and nest every follow-on step inside the branch it follows. Do not leave a piece as one gate with a flat list of outcomes, each ending in a one-line result.

Wrong, split but flat. Journey 3 lists outcomes and nothing follows from any of them:

```markdown
- Journey: Worker (3 of 4) — Send
  - Send result?
    - Accepted
    - Underpriced
    - Insufficient funds
    - Timeout
```

Right, split and chained. Each outcome carries what happens next:

```markdown
- Journey: Worker (3 of 4) — Send
  - Send result?
    - Not accepted
      - Insufficient funds
        - Hold and alert
        - Wallet funded → next re-send accepted
    - Timeout (ambiguous) → Journey 4 proof
    - Accepted
      - Does the checker see a mined attempt?
        - Not yet: re-send, then Journey 4
        - Mined → CONFIRMING (checker journey)
```

When a gate offers alternatives of one decision, list them as siblings. When one step leads to another, nest.

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

## Expected results are children of sample input/data tests

Write each expected assertion from the design doc as a separate leaf under its sample input/data test:

```markdown
- amount < minimum required
  - Sample data test: amount below documented minimum
    - HTTP Status 400
    - error code LB_API_AMT_001
    - message "amount below minimum"
- amount within allowed range
  - Sample data test: valid amount and sufficient balance
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
