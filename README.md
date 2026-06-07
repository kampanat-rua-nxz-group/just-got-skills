# just got skills

A growing, shareable collection of [Claude Code](https://claude.com/claude-code) **agent skills** authored by Kampanat — QA-lead tooling for test automation, bug reporting, and whatever else proves useful along the way.

More skills get added over time; the two below are the starting set.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| [`spec-hawk`](skills/spec-hawk/SKILL.md) | `/spec-hawk` | Severity-tagged QA review of Playwright + TypeScript automation specs (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`/`NIT`) with `file:line` citations and fix snippets. |
| [`create-bug-ticket`](skills/create-bug-ticket/SKILL.md) | "file a bug", "write a defect" | Turns any QA input (screenshot, API response, DevTools output, automation failure) into a developer-ready Jira bug ticket. |

## Install

### Recommended — `skills` CLI

The [`skills`](https://www.npmjs.com/package/skills) CLI installs straight from this repo:

```bash
npx skills add <you>/just-got-skills           # interactive: pick scope + skills
npx skills add <you>/just-got-skills -l        # list available skills, install nothing
npx skills add <you>/just-got-skills --all     # all skills, all agents, no prompts
npx skills add <you>/just-got-skills --skill spec-hawk -a claude-code -g  # one skill, global
```

`-g` installs globally (user-level); omit it to install into the current project.
Update later with `npx skills update`.

### Manual — clone + symlink

```bash
git clone <this-repo-url> ~/just-got-skills
ln -s ~/just-got-skills/skills/spec-hawk          ~/.claude/skills/spec-hawk
ln -s ~/just-got-skills/skills/create-bug-ticket  ~/.claude/skills/create-bug-ticket
```

`git pull` in `~/just-got-skills` then updates both skills in place.

### Manual — copy into a project

```bash
cp -R skills/create-bug-ticket  /path/to/project/.claude/skills/
```

Restart Claude Code (or start a new session) so the skills are picked up.

## Dependencies

These skills reference a couple of external pieces. Install them too, or the skill will fall back / ask:

- **`spec-hawk`** spawns the `automation-qa-reviewer` subagent. If that agent isn't installed, spec-hawk falls back to applying the checklist inline.
- **`create-bug-ticket`** invokes the `debug-mantra` skill when triaging automation failures. Without it, that step is skipped — the rest of the workflow still runs.

## Conventions

Each skill lives in `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`). Supporting docs sit alongside as `REFERENCE.md`. This layout matches the common Claude Code skill marketplaces (e.g. `mattpocock/skills`, `vercel-labs/skills`).
