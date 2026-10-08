# Just Got Skills — Agent Instructions

This repository contains reusable, runtime-neutral agent skills maintained by Got.Kampanat.

## Structure

- `skills/testing/` — QA skills
- `skills/dev/` — development workflow skills
- `agents/` — optional role prompts
- `scripts/` and `tests/` — repository validation and skill support

## Skill conventions

- Each skill lives in its own directory and has a `SKILL.md` with YAML `name` and `description` frontmatter.
- Keep skills portable across compatible agent runtimes. Treat platform-specific commands or tools as optional capabilities, not prerequisites, unless the skill is explicitly platform-specific.
- Update the catalog in `README.md` when adding a skill.
- Keep the entrypoint concise; put substantial optional detail in a linked reference.
- Do not modify tests merely to make a change pass. Update contracts only when the intended repository behavior changes.
