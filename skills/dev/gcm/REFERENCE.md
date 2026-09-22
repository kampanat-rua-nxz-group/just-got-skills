# gcm — Reference

Full commit-convention rule set that `gcm` enforces, mirroring
[`@commitlint/config-conventional`](https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/config-conventional).
The SKILL.md summarizes these; this file is the authoritative detail.

Commit message shape:

```
type(scope): subject

body

footer
```

---

## Type

| Rule | Level | Value |
|---|---|---|
| `type-enum` | error | `build` `chore` `ci` `docs` `feat` `fix` `perf` `refactor` `revert` `style` `test` |
| `type-case` | error | lower-case |
| `type-empty` | error | must not be empty |

## Subject

| Rule | Level | Value |
|---|---|---|
| `subject-case` | error | not `sentence-case`, `start-case`, `pascal-case`, `upper-case` |
| `subject-empty` | error | must not be empty |
| `subject-full-stop` | error | must not end with `.` |

## Header (`type(scope): subject`)

| Rule | Level | Value |
|---|---|---|
| `header-max-length` | error | ≤ 100 chars |

## Body

| Rule | Level | Value |
|---|---|---|
| `body-leading-blank` | warning | blank line between header and body |
| `body-max-line-length` | error | each line ≤ 100 chars |

## Footer

| Rule | Level | Value |
|---|---|---|
| `footer-leading-blank` | warning | blank line between body and footer |
| `footer-max-line-length` | error | each line ≤ 100 chars |

---

## Notes

- **error** rules fail the commit (non-zero exit); **warning** rules print but pass.
- Scope is optional and unconstrained by `config-conventional` (no `scope-enum`);
  keep it short and lowercase by convention.
- Breaking changes: mark with `!` after type/scope (`feat!:`, `feat(api)!:`) or a
  `BREAKING CHANGE:` footer.

---

## Interactive staging

Interactive commands can't be pasted into a batch and can't be piped. Never fold `git add -p` or
`git commit -p` into a paste-and-run block, and never run one. Break that scope into numbered
steps and give the user the answer for each prompt; the commit stays theirs to run.

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

| Key | Meaning |
|---|---|
| `y` | stage the hunk |
| `n` | skip the hunk |
| `s` | split the hunk further |
| `e` | manually edit the hunk |
| `q` | quit interactive staging |

Walkthrough rules:

- List keys in prompt order, one entry per hunk — no gaps, or the user loses their place.
- After `s`, spell out the answers for each resulting sub-hunk (`s, then y n`).
- If a hunk still mixes concerns after `s`, say `e` and describe which lines to keep.
- Always put `git diff --staged` between the last `add -p` and the `commit`.
- Every skipped hunk must reappear in a later numbered step — never leave one unaccounted for.
