---
name: "draft-pr"
description: Use when the user asks to draft, write, or improve a pull request title or description from a branch diff, including the /draft-pr trigger.
model: sonnet
---

# draft-pr — pull request title & description generator

Create a Conventional-Commit-style pull request title and description from a branch diff. **Read-only — never run `git commit`, `git add`, `git push`, or `gh pr create`.**

## Workflow

1. **Detect the base branch.** Complete this step when a base is identified; ask the user only if none of these yields one:
   - **Named parent.** If the user names a parent PR or branch ("stacked on #15", "based on X"), use it: `gh pr view <n> --json headRefName,baseRefName`, `git fetch origin <headRefName>`, base = `<headRefName>`, compare against `origin/<headRefName>`.
   - **Stacked-parent probe.** Otherwise, before falling back to `main`, check whether HEAD sits on another open PR: `gh pr list --state open --json number,headRefName,headRefOid`; keep each PR whose `headRefOid` is an ancestor of HEAD (`git merge-base --is-ancestor <oid> HEAD`) and is not HEAD itself, and pick the one with the fewest commits in `git rev-list --count <oid>..HEAD`. Say which PR you stacked on.
   - **Default.** Try `main`, then `master` — `git show-ref --verify --quiet refs/heads/main || git show-ref --verify --quiet refs/heads/master` — or check the remote default with `git remote show origin`.
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
6. **Draft the description** from the template chosen in step 3. For a stacked PR (step 1 picked a parent PR), open the body with `Stacked on #<n>. Retarget to <parent's base> after #<n> merges.`
   - **Repo template:** keep its headings, order, and checklists. Replace each HTML-comment prompt and placeholder with branch content; tick a checkbox only when the diff or a step-4 command proves it. Put summary-style content (what changed **and why**) and step-4 verification in the sections closest to them. Write `N/A` in a section the branch does not touch. Complete this step when every template section is filled or marked `N/A`.
   - **Skill template:** complete this step when the body includes:
     - `## Summary` — bullet points; each states what changed **and why**, inferred from commit messages and code intent, not just a restatement of the diff stat
     - `## Test plan` — checklist (`- [ ]`) of concrete verification steps using the repo's real commands from step 4

7. **Verify the checklists.** Before showing the draft, check every checklist item in the body: the `## Test plan` items and any checklist from the repo template. Run each item that a local, read-only command can check, from the repo root. Tick `- [x]` only when the command ran in this session and its output shows a pass. Read the output, not only the exit code: a secret scan that hits only docs quoting the scan command exits as a failure and reads as a pass, so word that ticked item to say what the pass means. Leave `- [ ]` on every item you did not run: ones that need an app or a deployed environment, and commands that write files or change git state. A failed check stays `- [ ]` and goes to the user with its output. Never show the draft before this step ends. Complete this step when every checklist item is either ticked with run evidence or unticked with a stated reason.

## Output format

Output the PR details, not a `gh pr create` command. The user pastes each field into the PR form by hand. Show the draft only after steps 7 and 8 are done. Use this layout, in this order:

1. A details list, one line each: `Base: <detected base>`, `Head: <branch>`, `Draft: yes` (only when the user asked for a draft), `Assignee: me` (omit only if the user said not to), `Reviewers: <logins or none>`. For a stacked PR, add `Stacked on: #<n>`.
2. The title, alone in a fenced block with no language tag. Name the field on the line above the block ("Title").
3. The body, alone in a fenced block with no language tag, after a line naming the field ("Description"). Make the fence longer than any backtick run inside the body (use four backticks when the body holds a code fence). The body follows the template chosen in step 3. Checklist items carry the state step 7 left them in.
4. A verification note after the blocks: one line per unticked checklist item, starting `Not verified:` and naming the reason, and one line per failed check with its output. Write `All checklist items verified` when none apply. Nothing else.

Skill-template example:

````
Base: main
Head: feature/my-branch
Assignee: me
Reviewers: login1, login2

Title
```
type(scope): subject
```

Description
```
## Summary
- ...

## Test plan
- [x] `<repo command>` passes (ran in this session)
- [ ] <item not run> (needs a deployed environment)
```

Not verified: <item not run>, needs a deployed environment.
````

When drafting for multiple branches in one request, emit one such set per branch, in the order the branches were given, each headed by its branch name.

## Failure handling

- If a base cannot be detected, ask the user which branch to compare before drafting.
- If no test/build command is discoverable in `package.json`, README, or CI, say so explicitly and mark fallback verification steps as unverified.
