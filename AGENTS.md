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
- Name each skill by the rules in [Naming a skill](#naming-a-skill). The folder name and frontmatter `name` must match.
- Refer to another skill as "invoke `name`" or "the `name` skill". The validator fails when that skill is not in this repository, so a skill never depends on one a user cannot install from here.

## Naming a skill

The name is the handle a user types after `/`. The description carries the meaning.

1. **Use one lowercase word.** Letters and digits only, no hyphen: `defect`, `impact`, `tdd`. The validator enforces this.
2. **Name what the skill hands back or does.**
   - It produces an artifact: use the artifact's noun, such as `defect`, `story`, `pr`, or `digest`. Do not add a verb such as `create-`, `draft-`, or `to-`.
   - It runs a practice: use the term a QA engineer or developer says out loud, such as `tdd`, `impact`, or `scenario`.
   - Use a nickname such as `copigot` only when the plain word is taken or too generic. The description must then say what the skill does.
3. **Prefer a standard term to an invented one.** Use an abbreviation only when people in the field know it, such as `tdd`, `pr`, or `qa`, or when it mirrors a command the maintainer already types: `gcm` follows `gc -m`.
4. **Never take a reserved name.** [`scripts/reserved_skill_names.txt`](scripts/reserved_skill_names.txt) lists runtime commands and bundled skills, such as `bug`, `recap`, `review`, and `init`. The runtime runs its own command first, so a skill with a reserved name is never reached by its trigger. The validator enforces this. Refresh the list when a runtime adds commands.
5. **Reuse a name from another skill set only for the same job.** Users may install poteto's pstack or mattpocock/skills next to this repo. `tdd` and `pr` match their jobs there. Never give one of their names to a different job.
6. **Keep the category folder out of the name.** `testing/` and `dev/` group skills. They are not part of the handle.
7. **Keep author and brand names out**, except in a future router or setup skill for this repo.
8. **Treat a rename as a breaking change.** Rename only for a collision or a misleading name. In the same commit, update the README catalog and symlink commands, the tests, and every "invoke `name`" reference.

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
