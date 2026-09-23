# Just Got Skills

Agent skills for compatible runtimes, including [Claude Code](https://claude.com/claude-code) — QA-lead tooling by Got.Kampanat for everyday QA life.

## Layout

Skills live under `skills/`, grouped by use:

- `testing/` — QA craft: spec review, test design, defect reporting
- `dev/` — everyday dev workflow

Each skill is its own directory containing a `SKILL.md` (YAML frontmatter — `name` and `description`) plus any bundled scripts or reference files.

## Install

> **Private repo.** The bare `owner/repo` shorthand resolves over unauthenticated HTTPS and 404s for teammates. Use the SSH git URL, or set `GITHUB_TOKEN`, so the `skills` CLI can authenticate.

### With `npx skills` (recommended)

```bash
SKILLS_REPO=git@github.com:kampanat-rua-nxz-group/just-got-skills.git
npx skills add "$SKILLS_REPO"          # interactive: pick scope + skills
npx skills add "$SKILLS_REPO" -l       # list available skills, install nothing
npx skills add "$SKILLS_REPO" --all    # all skills, all agents, no prompts
```

Over HTTPS instead: `GITHUB_TOKEN=ghp_xxx npx skills add kampanat-rua-nxz-group/just-got-skills`.

> `npx skills check` / `update` skip private-repo skills ([skills#162](https://github.com/vercel-labs/skills/issues/162)) — use the symlink route below to stay current.

### Alternative — clone + symlink (auto-updatable)

```bash
git clone git@github.com:kampanat-rua-nxz-group/just-got-skills.git ~/just-got-skills
ln -s ~/just-got-skills/skills/testing/spec-hawk         ~/.claude/skills/spec-hawk
ln -s ~/just-got-skills/skills/testing/usecase-map       ~/.claude/skills/usecase-map
ln -s ~/just-got-skills/skills/testing/create-bug-ticket ~/.claude/skills/create-bug-ticket
ln -s ~/just-got-skills/skills/dev/gcm                   ~/.claude/skills/gcm
ln -s ~/just-got-skills/skills/dev/draft-pr              ~/.claude/skills/draft-pr
ln -s ~/just-got-skills/skills/dev/create-jira-story-task ~/.claude/skills/create-jira-story-task
```

`git pull` in `~/just-got-skills` then updates every linked skill in place.

> **`spec-hawk` also needs its subagent** — the `skills` CLI installs skills, not agents:
> ```bash
> cp agents/automation-qa-reviewer.md ~/.claude/agents/
> ```
> Without it, `spec-hawk` falls back to running the same checklist inline (the full checklist ships with the skill as `CHECKLIST.md`).

## Reference

### Testing

- **[spec-hawk](./skills/testing/spec-hawk/SKILL.md)** — Severity-tagged QA review of Playwright + TypeScript automation specs (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`/`NIT`) with `file:line` citations and fix snippets. `/spec-hawk`.
- **[usecase-map](./skills/testing/usecase-map/SKILL.md)** — QA use-case mind map (`.xmind`) from a feature, user story, or API spec: Validation, Business Scenarios, Security & Edge, Coverage Gaps. Saves a Markdown outline to the repo's `docs/testcases/` and renders the `.xmind` next to it; needs Python 3. `/usecase-map`.
- **[create-bug-ticket](./skills/testing/create-bug-ticket/SKILL.md)** — Turn any QA input (screenshot, API response, DevTools output, automation failure) into a developer-ready Jira bug ticket.

### Dev

- **[gcm](./skills/dev/gcm/SKILL.md)** — Conventional Commit messages from the working-tree diff; detects mixed concerns and emits a split-commit plan, warns on likely secrets/PII. Copy-paste text only, never runs git. `/gcm`.
- **[draft-pr](./skills/dev/draft-pr/SKILL.md)** — PR title + description (Summary, Test plan) from the diff between the current branch and its base branch, using the repo's real test commands. Copy-paste text only, never runs git or `gh pr create`. `/draft-pr`.
- **[create-jira-story-task](./skills/dev/create-jira-story-task/SKILL.md)** — Copy-ready non-defect Jira Stories and Tasks with required requirements fields, testable acceptance criteria, and explicit unresolved questions.

## Validate

```bash
python3 scripts/validate_skills.py .
python3 -m unittest discover -s tests -v
```

The first command checks skill packaging and links. The second protects behavior contracts and the XMind renderer.
