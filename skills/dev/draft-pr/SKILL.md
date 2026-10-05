---
name: draft-pr
description: Use when the user asks to draft, write, or improve a pull request title or description from a branch diff, including the /draft-pr trigger.
---

# draft-pr — pull request title & description generator

Create a Conventional-Commit-style pull request title and description from a branch diff. **Read-only — never run `git commit`, `git add`, `git push`, or `gh pr create`.**

## Workflow

1. **Detect the base branch.** Try `main`, then `master` — `git show-ref --verify --quiet refs/heads/main || git show-ref --verify --quiet refs/heads/master` — or check the remote default with `git remote show origin`. Complete this step when a base is identified; ask the user only if neither exists and no upstream default is configured.
2. **Gather branch intent** (read-only):
   - `git log <base>..HEAD --oneline` — commit history for this branch
   - `git diff <base>...HEAD --stat` — files touched, at a glance
   - For files that materially shape intent (new services, migrations, config, non-trivial logic), read their full diffs; don't dump an entire large diff blindly.
   Complete this step when the branch's primary change and any secondary concerns are clear.
3. **Choose the body template.** Read `.github/PULL_REQUEST_TEMPLATE.md` from the branch being drafted: `git show <branch>:.github/PULL_REQUEST_TEMPLATE.md`. Complete this step when one template is chosen:
   - File exists → **repo template**.
   - File absent → **skill template** (step 6).
4. **Discover repository verification.** Check `package.json` scripts, README "Commands"/"Usage" sections, or CI config (`.github/workflows/*.yml`) for the actual test, typecheck, and migration commands. Complete this step with repository-derived commands only; never invent generic commands.
5. **Draft the title.** Use Conventional Commit format (`type(scope): subject`), imperative mood, and no more than 70 characters. Complete this step when the title represents the dominant branch concern; if concerns are mixed, reserve the secondary ones for the summary.
6. **Draft the description** from the template chosen in step 3.
   - **Repo template:** keep its headings, order, and checklists. Replace each HTML-comment prompt and placeholder with branch content; tick a checkbox only when the diff or a step-4 command proves it. Put summary-style content (what changed **and why**) and step-4 verification in the sections closest to them. Write `N/A` in a section the branch does not touch. Complete this step when every template section is filled or marked `N/A`.
   - **Skill template:** complete this step when the body includes:
     - `## Summary` — bullet points; each states what changed **and why**, inferred from commit messages and code intent, not just a restatement of the diff stat
     - `## Test plan` — checklist (`- [ ]`) of concrete verification steps using the repo's real commands from step 4

## Output format

One fenced `bash` block containing a ready-to-run `gh pr create` command, nothing else. Use `--base <detected base>` and `--head <current branch>` (only include `--head` when drafting for a branch other than the one already checked out), title via `--title`, and body via `--body "$(cat <<'EOF' ... EOF)"` so multi-line markdown survives shell quoting untouched. The body follows the template chosen in step 3; the example shows the skill template:

```bash
gh pr create --base main --head feature/my-branch \
  --title "type(scope): subject" \
  --body "$(cat <<'EOF'
## Summary
- ...

## Test plan
- [ ] ...
EOF
)"
```

When drafting for multiple branches in one request, emit one such block per branch, each in its own fenced code block, in the order the branches were given.

## Failure handling

- If a base cannot be detected, ask the user which branch to compare before drafting.
- If no test/build command is discoverable in `package.json`, README, or CI, say so explicitly and mark fallback verification steps as unverified.
