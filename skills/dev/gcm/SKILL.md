---
name: gcm
description: Generate Conventional Commit messages from the working-tree diff, flag when changes mix concerns, and emit a split-commit plan as copy-paste text. Use for commit-message wording, splitting a commit, "commit this", or the "gcm" trigger.
---

# gcm — git commit message generator

Generates Conventional Commit messages from the diff. **Emits copy-paste text only — never runs `git add`/`commit`/`push`.**

Out of scope: amend, rebase, hook fixes. Wording and staging plans only.

## Workflow

1. **Read the diff** (read-only): `git status --short`, `git diff --staged`, `git diff`. Note which files are already staged — respect existing staging, don't silently override it.
2. **Single concern or many?** Group changed files by meaning. Type must be one of the commitlint `config-conventional` set: `build` `chore` `ci` `docs` `feat` `fix` `perf` `refactor` `revert` `style` `test`. One concern → one commit; multiple → split plan.
3. **Mixed-hunk files**: one file mixing concerns can't be split with `git add <file>`. Don't just name `git add -p` and move on — emit the step-by-step walkthrough below for that file's scope, then leave the commit to the user.
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

## Interactive staging — `git add -p` / `git commit -p`

Interactive commands can't be pasted into a batch and can't be piped: they prompt per hunk. So
**never fold `git add -p` or `git commit -p` into a paste-and-run block, and never run one.**
Instead, break that scope into numbered steps and hand the user the answer for each prompt — the
commit itself stays theirs to run.

If the user asks for `git commit -p`, split it: `git add -p <file>` (walkthrough below) → verify →
plain `git commit -m`. `commit -p` bundles staging and committing into one prompt session, which
makes the hunk answers impossible to state up front.

Emit one line per hunk **in the order `git add -p` presents them**: hunk number, `file:line`
range, a one-line description, and the key to press.

```
# 1a. you run this — answer each prompt as listed
git add -p src/auth.ts
#   hunk 1  src/auth.ts:12-28   guard undefined debCardId        → y
#   hunk 2  src/auth.ts:40-44   rename local in the test helper  → n
#   hunk 3  src/auth.ts:71-95   two concerns in one hunk         → s, then y n

# 1b. verify what got staged
git diff --staged

# 1c.
git commit -m "fix(auth): guard null card ID before hashing" -m "- ..."
```

Rules for the walkthrough:

- Keys: `y` stage, `n` skip, `s` split further, `e` manual edit, `q` quit. List them in prompt
  order, one entry per hunk — no gaps, or the user loses their place.
- After `s`, spell out the answers for each resulting sub-hunk (`s, then y n`).
- If a hunk still mixes concerns after `s`, say `e` and describe which lines to keep.
- Always put `git diff --staged` between the last `add -p` and the `commit`.
- Every skipped hunk must reappear in a later numbered step — never leave one unaccounted for.

## Always end with

`Run tests/typecheck before committing` (no commits with failing tests or type errors).
