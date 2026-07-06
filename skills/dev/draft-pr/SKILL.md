---
name: draft-pr
description: Generate a Conventional-Commit-style PR title and a description (Summary + Test plan) from the diff between the current branch and its base branch. Use when the user asks for "PR title and description", "pull request description", wants to "draft a PR", "write PR description", or invokes /draft-pr.
---

# draft-pr — pull request title & description generator

Generates a PR title + description from the branch diff. **Read-only — never runs `git commit`, `git add`, `git push`, or `gh pr create`.** Emits copy-paste text for the user to paste into `gh pr create --title ... --body ...` or the PR web UI.

## Workflow

1. **Detect the base branch**: try `main`, fall back to `master` — `git show-ref --verify --quiet refs/heads/main || git show-ref --verify --quiet refs/heads/master`, or check the remote's default via `git remote show origin`. Ask the user only if neither exists and no upstream default is configured.
2. **Gather the diff** (read-only):
   - `git log <base>..HEAD --oneline` — commit history for this branch
   - `git diff <base>...HEAD --stat` — files touched, at a glance
   - For files that materially shape intent (new services, migrations, config, non-trivial logic), read the full diff of those specific files — don't dump the entire diff blindly on large branches.
3. **Infer the test plan from the repo itself**: check `package.json` scripts, README "Commands"/"Usage" sections, or CI config (`.github/workflows/*.yml`) for the actual test/typecheck/migration commands. Don't invent generic commands that aren't in the repo.
4. **Draft the title**: Conventional Commit format (`type(scope): subject`), under 70 characters, imperative mood, matching the dominant concern of the branch (if the branch mixes concerns, title the largest/primary one and note the others in the summary).
5. **Draft the description**:
   - `## Summary` — bullet points; each states what changed **and why**, inferred from commit messages and code intent, not just a restatement of the diff stat
   - `## Test plan` — checklist (`- [ ]`) of concrete verification steps using the repo's real commands from step 3

## Output format

Two fenced blocks, nothing else:

**Title:**
```
type(scope): subject
```

**Description:**
```markdown
## Summary
- ...

## Test plan
- [ ] ...
```

## Never
- Never run `git commit`, `git add`, `git push`, or `gh pr create`
- Never invent test/build commands not found in the repo's `package.json`, README, or CI config — if none are discoverable, say so explicitly and mark any fallback steps as unverified
