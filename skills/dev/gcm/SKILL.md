---
name: gcm
description: Generate Conventional Commit messages from the working-tree diff, flag when changes mix concerns, and emit a split-commit plan as copy-paste text. Use for commit-message wording, splitting a commit, "commit this", or the "gcm" trigger.
---

# gcm — git commit message generator

Generates Conventional Commit messages from the diff. **Emits copy-paste text only — never runs `git add`/`commit`/`push`.**

Out of scope: amend, rebase, `git add -p` execution, hook fixes. Wording and staging plans only.

## Workflow

1. **Read the diff** (read-only): `git status --short`, `git diff --staged`, `git diff`. Note which files are already staged — respect existing staging, don't silently override it.
2. **Single concern or many?** Group changed files by meaning. Type must be one of the commitlint `config-conventional` set: `build` `chore` `ci` `docs` `feat` `fix` `perf` `refactor` `revert` `style` `test`. One concern → one commit; multiple → split plan.
3. **Mixed-hunk files**: one file mixing concerns can't be split with `git add <file>`. Flag it, suggest `git add -p <file>`, and state which hunks go to which commit.
4. **Secret/PII check (heuristic)**: scan for long digit runs (card/national IDs) and `key=`/`token`/`secret`/`password` patterns. On a hit, warn `Diff may contain a secret/PII — review before committing` and never echo the literal value.

## Output format

English, Conventional Commits (commitlint `config-conventional`), subject + body bullets when the change spans multiple files. Enforce:

- **Header ≤ 100 chars** — the whole `type(scope): subject` line. Tighten wording or push detail to bullets, never exceed.
- **Subject** lowercase start (no sentence/start/pascal/upper case), **no trailing period**.
- **Type** lowercase, from the set above.
- **Body/footer lines ≤ 100 chars each** — wrap long bullets across lines.
- **Blank line** before body and before footer; **subject and type never empty**.

Full rule table (levels, breaking-change syntax) in [`REFERENCE.md`](REFERENCE.md).

Emit runnable lines only — the `git commit -m` args *are* the message, so don't also print a separate message block. Each `-m` = one paragraph/bullet; use full `git commit -m`, not an alias.

```
git add path/to/file.ts
git commit -m "fix: handle null card ID in auth middleware" -m "- guard undefined debCardId before hashing" -m "- add fallback when CON_CODE is missing"
```

### Split plan (multiple concerns)

Numbered, **sequential** — run in order:

> **1.** `git add auth/*.ts`
> `git commit -m "feat(auth): ..." -m "..."`
>
> **2.** `git add tests/*.spec.ts`
> `git commit -m "test: ..." -m "..."`

If a file is already staged that doesn't belong to step 1, say so — the user resets it first.

## Always end with

`Run tests/typecheck before committing` (no commits with failing tests or type errors).
