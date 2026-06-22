---
name: gcm
description: Generate Conventional Commit messages from the working-tree diff, detect when changes mix multiple concerns, and emit a split-commit plan as copy-paste text. Use when the user asks for a commit message, says "write a commit message", "what should this commit say", "commit this", "gcm", or wants help wording or splitting a commit.
---

# gcm — git commit message generator

Generates Conventional Commit messages from the diff. **Emits copy-paste text only — never runs `git add`, `git commit`, or `git push`** (project hook hard-blocks them; the skill respects that by design).

## Workflow

1. **Read the diff** (read-only): `git status --short`, `git diff --staged`, `git diff`.
   Note which files are already staged — the plan must respect existing staging, not silently override it.
2. **Decide: single concern or many?** Group changed files by meaning (Conventional Commit type/scope: `feat`/`fix`/`docs`/`chore`/`test`/`perf`/`refactor`). One concern → one commit. Multiple → split plan.
3. **Mixed-hunk files**: if one file mixes concerns (e.g. feature + bugfix in the same file), you can't split it with `git add <file>`. Flag it and suggest `git add -p <file>`, stating which hunks belong to which commit.
4. **Secret/PII check (best-effort)**: scan the diff for long digit runs (13-digit card / national IDs), `key=`/`token`/`secret`/`password` patterns. If anything looks sensitive, warn `Diff may contain a secret/PII — review before committing` and never put the literal value in the message. This is a heuristic, not a guaranteed scanner.

## Output format

All messages in **English**, Conventional Commits, subject + body bullets when the change spans multiple files.

For each commit, emit two things:

**(A)** Human-readable message in a code block:
```
fix: handle null card ID in auth middleware

- guard against undefined debCardId before hashing
- add fallback when CON_CODE is missing
```

**(B)** Two runnable lines (text — user copies & runs them separately):
```
git add path/to/file.ts
git commit -m "fix: handle null card ID in auth middleware" -m "- guard against undefined debCardId before hashing" -m "- add fallback when CON_CODE is missing"
```
Each `-m` = one paragraph/bullet. Use full `git commit -m`, not an alias.

### Split plan (multiple concerns)

Present **numbered, sequential** steps — must run in order:

> **1.**
> `git add auth/*.ts`
> `git commit -m "feat(auth): ..." -m "..."`
>
> **2.**
> `git add tests/*.spec.ts`
> `git commit -m "test: ..." -m "..."`
>
> **3.**
> `git add docs/*.md`
> `git commit -m "docs: ..."`

If a file is already staged that doesn't belong to step 1, call it out so the user can `git reset` it first.

## Always end with

A one-line reminder: `Run tests/typecheck before committing` (project rule: no commits with failing tests or type errors).
