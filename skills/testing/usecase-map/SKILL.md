---
name: usecase-map
description: Use when the user asks for a QA use-case map, test-case mind map, scenario coverage, or validation and business-flow coverage for a feature, user story, or API specification.
argument-hint: "[feature description, user story, or spec]"
---

# Use Case Map

Feature in → QA use-case mind map out. The workflow has the agent design the Markdown outline; `scripts/md2xmind.py` renders it to `.xmind`.

## Workflow

1. **Gather context** — feature description, user story, acceptance criteria, spec, **plus design doc** (error codes, messages, limits). Undocumented values → `TBD`. Ask only if genuinely unclear.
2. **Design four branches** (taxonomy below). Every scenario ends in expected-result leaf topics. Mark critical-path `[!]`.
3. **Append Coverage Gaps** summary at outline bottom.
4. **Save outline** to the project repo at `docs/testcases/<feature>-usecase-map.md`. Create the directory if it doesn't exist. No frontmatter required — plain Markdown only.
5. **Render and conditionally open** (write `.xmind` next to the outline in `docs/testcases/`, not Downloads). Run the bundled script from this skill's own directory — resolve `<skill-dir>` from wherever this SKILL.md was loaded; do not assume `~/.claude/skills/`:
   ```bash
   python3 <skill-dir>/scripts/md2xmind.py docs/testcases/<feature>-usecase-map.md \
     -o "docs/testcases/<Feature Name>.xmind"
   ```
   Use the platform opener when desktop access is available (`open` on macOS, `xdg-open` on Linux); otherwise report the generated path.

Outline = source of truth. `.xmind` = disposable rendering. If user edits `.xmind` directly, sync outline back first.

## Taxonomy (four branches, fixed order)

Root = API / feature group. `##` for each branch.

### 1. Validation Cases

Per-field input matrix. One node per endpoint. Sub-branches **in order** (omit non-applicable):

1. **Method** → `invalid method` → HTTP 405
2. **Path/Endpoint** → `invalid path` → HTTP 404
3. **Headers** → one node **per header** → `Omit field`, `Empty/whitespace`, mismatch/wrong value
4. **Request body** (POST) → one node **per field** → omit, empty, format, boundary, type mismatch. Expand per field — never combine.
5. **Query/Path parameters** (GET) → scenarios per param

Owns schema-level validation exhaustively. Business Scenarios assumes schema-valid — no repeats.

### 2. Business Scenarios (gated decision tree)

One gated tree per endpoint. Happy path top-down; fail forks terminate at error leaves, one pass branch continues deeper. Put `> assumes: request schema-valid (see [[Validation Cases]])` on tree root.

**Gate order** (skip only with `> skip: <reason>` — silent absence = gap):

1. **Service reachable?** → fail `@edge`
2. **Dependencies available?** → fail `@edge` — one gate per dependency
3. **Authenticated?** → fail `@security` — `> skip:` if public endpoint
4. **Authorized?** → fail `@security` — `> skip:` if no roles/ownership
5. **Business rules** (limits, allowed state/transition) → fail per rule
6. **Resource/state** (balance, existence, idempotency) → fail per check
7. **→ Success**

Pass branch = named positive condition with deeper children. Fail fork = sibling terminating in a return leaf. For multi-endpoint flows add `## Journey: <name>` tree with sequential calls as gates.

### 3. Cross-cutting (Security & Edge)

Off-path, multi-point concerns only (auth/authz = gates 3–4; infra = gates 1–2):

- **Security** — injection, oversized payload, info leakage, rate limiting
- **Edge Cases** — concurrency/races, timeout ambiguity, unicode, null bytes, boundary timing

### 4. Coverage Gaps

Append at outline bottom. The agent authors it by reading the built tree. List:

- **`@blocked-tbd` / `TBD` forks** — every fork with undocumented values
- **Skipped gates** — every `> skip: <reason>` gate
- **Continuation with no fail fork** — pass branch with no failure siblings

## Expected results are leaf topics, not notes

Every scenario ends in sibling-bullet assertions from the design doc:

```markdown
- amount < minimum required
  - HTTP Status 400
  - error code LB_API_AMT_001
  - message "amount below minimum"
- → Success [!]
  - HTTP Status 200
  - <key success-response assertions>
```

Undocumented field → `TBD` per field (e.g. documented code, undocumented message → only `message TBD`). Tag fork `@blocked-tbd`. Notes (`>`) carry spec wikilinks, open questions, `Prep:`/`Steps:` for non-obvious setup. No `UC-V1`-style ID prefixes.

## Automation labels

- `@mock-only` — fault injection needed; note harness in `Prep:`
- `@nondeterministic` — trigger can't be forced; note invariant + repeat strategy
- `@manual` — unsafe or impossible to automate
- `@blocked-tbd` — behavior undefined; write test, mark skipped until dev defines contract

## Outline conventions

> Full [annotated example](REFERENCE.md#full-annotated-example) and [operational notes](REFERENCE.md#notes).

- `#` root (one only), `##` branches, `-` bullets with 2-space indent
- `> text` → note on topic; `[!]` → critical; `[P1]`–`[P3]` → priority (optional); `@label` → label
- `<br>` inside title → line break (prefer separate siblings)
- `[pos]`/`[neg]` prefix for positive/negative variants nested under their scenario
