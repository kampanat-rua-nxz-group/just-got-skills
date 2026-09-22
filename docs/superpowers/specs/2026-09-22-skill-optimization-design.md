# Compatibility-First Skill Optimization Design

## Purpose

Improve every skill in this repository while preserving its observable behavior, output format, scope, and safety boundaries. The optimized skills should invoke more reliably, load less irrelevant context, use runtime-neutral language where possible, and be easier to validate and maintain.

## Scope

This pass covers all five skills and their supporting files:

- `skills/dev/draft-pr`
- `skills/dev/gcm`
- `skills/testing/create-bug-ticket`
- `skills/testing/spec-hawk`
- `skills/testing/usecase-map`
- `agents/automation-qa-reviewer.md`
- Repository documentation and validation added specifically for these skills

The work may reorganize instructions between `SKILL.md` and existing or new reference files. It may add deterministic validation scripts or fixtures. It must not add new user-facing capabilities or change existing output contracts.

## Compatibility Contracts

### draft-pr

- Remains read-only.
- Produces one fenced `bash` block per requested branch.
- Each block contains a ready-to-run `gh pr create` command.
- Keeps Conventional-Commit-style titles, `## Summary`, and `## Test plan`.
- Detects the base branch and uses repository-discovered verification commands.

### gcm

- Remains read-only and emits commands for the user to run.
- Preserves Conventional Commit validation, the 100-character line limit, secret/PII redaction, split plans, and interactive staging walkthroughs.
- Preserves runnable `git add` and `git commit -m` output and the final reminder to run tests/type checking.

### create-bug-ticket

- Continues to produce English, developer-ready Jira tickets from the same evidence types.
- Preserves automation-failure triage before ticket creation.
- Preserves the ten-section ticket structure, environment and severity tables, regression-oriented QA note, and evidence handling.
- Continues to stop when an automation failure is a test or harness problem rather than a confirmed product defect.

### spec-hawk

- Remains a read-only Playwright and TypeScript automation review.
- Preserves repository-convention discovery, all nine checklist areas, severity-tagged findings, `file:line` citations, fix snippets for serious findings, and the existing report structure.
- Preserves the dedicated reviewer path and an inline fallback when that reviewer is unavailable.
- Does not apply fixes or run tests.

### usecase-map

- Continues to create a Markdown outline and adjacent `.xmind` rendering under `docs/testcases/`.
- Preserves the four branches, their fixed order, gated business trees, expected-result leaves, coverage-gap analysis, labels, notes, and source-of-truth relationship.
- Preserves the current XMind 2020+ archive format and command-line interface of `md2xmind.py`.
- Continues to open the rendered file when the environment supports it.

## Design

### Invocation and entrypoints

Each `description` will become a compact context pointer: it will state the requests and conditions that should activate the skill without summarizing the workflow. Existing trigger coverage will be retained, including explicit command names and common user phrases.

Each `SKILL.md` will keep the steps and constraints needed on every invocation. Conditional examples, detailed schemas, convention tables, and uncommon branches will live in referenced files with explicit instructions describing when to read them. This reduces entrypoint sprawl without hiding mandatory behavior.

### Runtime portability

Instructions will name capabilities rather than one runtime's tool labels where the behavior is portable. Runtime-specific setup will be documented as a conditional branch. Existing Claude Code installation and reviewer support will remain functional; Codex and other agents will not be directed to unavailable `Agent`, `Glob`, or `Grep` interfaces when equivalent capabilities exist.

The dedicated `automation-qa-reviewer` definition remains supported. Its mirrored checklist must remain behaviorally identical to Spec Hawk's fallback. Validation will detect drift rather than relying on a prose reminder alone.

### Predictable execution

Workflow steps will end in checkable completion criteria. Output structures will be expressed positively as contracts. Hard safety boundaries such as read-only operation and secret redaction will remain explicit.

Repeated guidance will have one authoritative location wherever packaging permits. When two independently installed artifacts must contain the same behavior, their synchronization will be enforced by validation.

### Supporting resources

Existing reference files remain the home for detailed rules. New reference files are allowed only when a branch-specific body of guidance materially reduces the corresponding `SKILL.md` and has a clear context pointer.

The XMind converter remains standard-library-only. Tests may import it directly or execute its CLI, but production behavior and archive structure remain unchanged.

## Error Handling

- Missing repository information continues to produce an explicit unknown, unverified step, or focused question according to the current skill contract.
- Missing optional reviewer support triggers Spec Hawk's inline fallback.
- Invalid use-case outlines continue to fail with a line-specific error.
- Missing platform support for opening an XMind file does not invalidate a successfully generated artifact; the skill reports the saved path.
- Validation failures identify the exact skill and violated invariant and return a nonzero status.

## Validation Strategy

Because behavioral subagent testing was not requested, validation will be deterministic and local:

1. Capture baseline contracts from the current files and encode them as structural checks.
2. Validate every skill's YAML frontmatter, folder/name match, local references, and absence of scaffold placeholders.
3. Check that each preserved output contract remains present after refactoring.
4. Check Spec Hawk's reviewer and fallback checklist for synchronized headings and severity definitions.
5. Compile `md2xmind.py` and run representative valid and invalid outline fixtures.
6. Inspect generated `.xmind` archives for required entries, topic hierarchy, notes, markers, and labels.
7. Run repository-wide link, wording, and size checks, treating size as a signal rather than a pass/fail target when essential instructions justify it.
8. Review the final diff skill by skill against the compatibility contracts above.

The bundled `quick_validate.py` validator will be used if its PyYAML dependency is available. The repository's own validation must not depend on third-party Python packages unless they are already declared by the repository.

## Non-Goals

- Changing any user-facing output format
- Adding Jira, GitHub, Git, or XMind mutations beyond the current contracts
- Replacing the existing QA taxonomies or severity model
- Changing the XMind CLI or file format
- Broadening Spec Hawk beyond Playwright and TypeScript automation
- Introducing runtime dependencies solely for validation

## Success Criteria

- All five skills satisfy their compatibility contracts.
- Descriptions retain existing trigger coverage while carrying less workflow detail.
- Every conditional reference is reachable through a clear context pointer.
- Runtime-specific instructions are isolated to the runtime that needs them.
- Mirrored Spec Hawk content cannot drift unnoticed.
- The XMind renderer passes valid, invalid, and archive-structure checks.
- Repository validation passes with only the Python standard library and available shell tools.
- The final diff contains no unrelated changes.
