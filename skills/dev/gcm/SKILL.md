---
name: gcm
description: Use when the user asks for Conventional Commit wording, wants to commit current changes, needs a commit split, or invokes gcm.
---

# gcm — git commit message generator

Generates Conventional Commit messages from the diff. **Emits copy-paste text only — never runs `git add`/`commit`/`push`.**

Out of scope: amend, rebase, hook fixes. Wording and staging plans only.

## Workflow

1. **Read the diff** (read-only): `git status --short`, `git diff --staged`, `git diff`. Note which files are already staged — respect existing staging, don't silently override it.
2. **Single concern or many?** Group changed files by meaning. Type must be one of the commitlint `config-conventional` set: `build` `chore` `ci` `docs` `feat` `fix` `perf` `refactor` `revert` `style` `test`. One concern → one commit; multiple → split plan.
3. **Mixed-hunk files**: one file mixing concerns can't be split with `git add <file>` and requires `git add -p`. Interactive commands cannot be pasted into a batch and must never be run by this skill. When any file contains mixed concerns, read [REFERENCE.md](REFERENCE.md#interactive-staging) before producing output; it defines the required hunk-by-hunk walkthrough and accounting rule.
4. **Secret/PII check (heuristic)**: scan for long digit runs (card/national IDs) and `key=`/`token`/`secret`/`password` patterns. On a hit, warn `Diff may contain a secret/PII — review before committing` and never echo the literal value.
5. **Commitlint validate**: before presenting a message, pipe the drafted header (and body, via `--edit`) through the repo's commitlint config, e.g. `echo "<header>" | npx commitlint`. If it fails, fix the wording and re-check — don't hand the user a message that would fail the commit hook. If no commitlint config exists in the repo, skip this step silently.

## Output format

English, Conventional Commits (commitlint `config-conventional`), subject + body bullets when the change spans multiple files. Enforce:

- **Every line ≤ 100 chars** — the whole message: the `type(scope): subject` header and each body/footer line. Tighten wording, push detail to bullets, or wrap long bullets across lines; never exceed.
- **Subject** lowercase start (no sentence/start/pascal/upper case), **no trailing period**.
- **Type** lowercase, from the set above.
- **Blank line** before body and before footer; **subject and type never empty**.

Full rule table (levels, breaking-change syntax) in [`REFERENCE.md`](REFERENCE.md).

Emit runnable lines only — the `git commit -m` args *are* the message, so don't also print a separate message block. Each `-m` = one paragraph/bullet; use full `git commit -m`, not an alias.

```
git add path/to/file.ts
git commit -m "fix: handle null card ID in auth middleware" -m "- guard undefined debCardId before hashing" -m "- add fallback when CON_CODE is missing"
```

### Split plan (multiple concerns)

Numbered, **sequential** — run in order. Emit as a plain code block so it copy-pastes cleanly (no blockquote):

```
# 1.
git add auth/*.ts
git commit -m "feat(auth): ..." -m "..."

# 2.
git add tests/*.spec.ts
git commit -m "test: ..." -m "..."
```

If a file is already staged that doesn't belong to step 1, say so — the user resets it first.

## Always end with

`Run tests/typecheck before committing` (no commits with failing tests or type errors).
