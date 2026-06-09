# Just Got Skills

A growing, shareable collection of [Claude Code](https://claude.com/claude-code) **agent skills** authored by Kampanat — QA-lead tooling for test automation, bug reporting, and whatever else proves useful along the way.

More skills get added over time; the two below are the starting set.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| [`spec-hawk`](skills/spec-hawk/SKILL.md) | `/spec-hawk` | Severity-tagged QA review of Playwright + TypeScript automation specs (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`/`NIT`) with `file:line` citations and fix snippets. |
| [`create-bug-ticket`](skills/create-bug-ticket/SKILL.md) | "file a bug", "write a defect" | Turns any QA input (screenshot, API response, DevTools output, automation failure) into a developer-ready Jira bug ticket. |
| [`gcm`](skills/gcm/SKILL.md) | `/gcm`, "commit message" | Generates Conventional Commit messages from the working-tree diff, detects mixed concerns and emits a numbered split-commit plan, and warns on likely secrets/PII. Copy-paste text only — never runs git. |

## Install

> **This is a private repo.** The bare `owner/repo` shorthand resolves over
> unauthenticated HTTPS and will 404 for teammates. Use an SSH git URL, or set
> `GITHUB_TOKEN`, so the `skills` CLI can authenticate.

### Recommended — `skills` CLI (private repo)

The [`skills`](https://www.npmjs.com/package/skills) CLI accepts a full git URL.
For a private repo, use the SSH form (works for anyone with GitHub SSH keys set up):

```bash
SKILLS_REPO=git@github.com:kampanat-rua-nxz-group/just-got-skills.git
npx skills add "$SKILLS_REPO"            # interactive: pick scope + skills
npx skills add "$SKILLS_REPO" -l         # list available skills, install nothing
npx skills add "$SKILLS_REPO" --all      # all skills, all agents, no prompts
npx skills add "$SKILLS_REPO" --skill spec-hawk -a claude-code -g  # one skill, global
```

Or authenticate over HTTPS with a token (uses `GITHUB_TOKEN` or your `gh` CLI auth):

```bash
GITHUB_TOKEN=ghp_xxx npx skills add kampanat-rua-nxz-group/just-got-skills
```

`-g` installs globally (user-level); omit it to install into the current project.

> **Heads-up:** `npx skills check` / `npx skills update` currently skip skills
> installed from private repos (empty `skillFolderHash`,
> [vercel-labs/skills#162](https://github.com/vercel-labs/skills/issues/162)), so
> auto-updates won't work yet. To stay current, use the clone + symlink route below
> and `git pull`.

### Manual — clone + symlink (best for staying updated)

```bash
git clone git@github.com:kampanat-rua-nxz-group/just-got-skills.git ~/just-got-skills
ln -s ~/just-got-skills/skills/spec-hawk          ~/.claude/skills/spec-hawk
ln -s ~/just-got-skills/skills/create-bug-ticket  ~/.claude/skills/create-bug-ticket
ln -s ~/just-got-skills/skills/gcm                ~/.claude/skills/gcm
```

`git pull` in `~/just-got-skills` then updates all three skills in place.

### Manual — copy into a project

```bash
cp -R skills/create-bug-ticket  /path/to/project/.claude/skills/
```

Restart Claude Code (or start a new session) so the skills are picked up.

## Dependencies

### `spec-hawk` needs its agent

`spec-hawk` is a thin trigger — the actual review engine is the `automation-qa-reviewer` **subagent**, bundled here at [`agents/automation-qa-reviewer.md`](agents/automation-qa-reviewer.md). The `skills` CLI installs skills, **not** agents, so copy the agent manually after installing the skill:

```bash
# global (all projects)
cp agents/automation-qa-reviewer.md ~/.claude/agents/

# or per-project
cp agents/automation-qa-reviewer.md /path/to/project/.claude/agents/
```

Both the skill and the agent are **repo-agnostic**: they discover your repo's own folder layout, tag scheme, shared package, and config conventions at review time rather than assuming a fixed structure. If the agent isn't installed, `spec-hawk` runs the same checklist inline as a fallback — the agent just gives cleaner, isolated results.

### `create-bug-ticket`

Self-contained (`SKILL.md` + `REFERENCE.md`). It invokes the public [`debug-mantra`](https://github.com/thananon/9arm-skills) skill when triaging automation failures; without it, that one step is skipped and the rest of the workflow still runs.

## Conventions

Each skill lives in `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`). Supporting docs sit alongside as `REFERENCE.md`. This layout matches the common Claude Code skill marketplaces (e.g. `mattpocock/skills`, `vercel-labs/skills`).
