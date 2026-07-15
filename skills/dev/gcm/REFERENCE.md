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
