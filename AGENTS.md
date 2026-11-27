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
- Name skills with one lowercase word (`bug`, `impact`, `tdd`). The folder name and frontmatter `name` must match.
- Refer to another skill as "invoke `name`" or "the `name` skill". The validator fails when that skill is not in this repository, so a skill never depends on one a user cannot install from here.

## Writing a skill

- When in doubt, delete. Keep only prose that changes what the agent does.
- Tell the agent what to do. Give the reason only when the rule is confusing without one.
- Delegate to another skill or a reference file instead of restating it.
- When the same mistake recurs, encode the rule as a validator check, a script check, or a contract test. Add more prose only when the rule needs judgment, and then show an example of the failure.

## Behavior every skill should keep

- **Check the real thing.** Run the test, read the actual response, inspect the diff. "It compiles", a cached result, or a report that something passed is not proof. When a check fails, suspect how you checked before you suspect the system.
- **Label each claim by its source.** Mark it as verified (ran or observed), cited (`file:line` or a document section), inferred, or `TBD`. Never present an inference as a requirement.
- **Do not hand the user a check the agent can run.** Ask the user only for facts the agent cannot observe.
- **Proceed on reversible work.** Ask before irreversible or outward-facing actions: pushing, filing tickets, sending messages, or deleting data.
- **Write for a tired reader.** Use the plain word, one name per thing, and the number instead of an adverb. No filler, no AI vocabulary (crucial, delve, leverage, robust), and no chatbot openers or closers.
