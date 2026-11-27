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
ln -s ~/just-got-skills/skills/testing/copigot   ~/.claude/skills/copigot
ln -s ~/just-got-skills/skills/testing/questions ~/.claude/skills/questions
ln -s ~/just-got-skills/skills/testing/scenario  ~/.claude/skills/scenario
ln -s ~/just-got-skills/skills/testing/mindmap   ~/.claude/skills/mindmap
ln -s ~/just-got-skills/skills/testing/probe     ~/.claude/skills/probe
ln -s ~/just-got-skills/skills/testing/defect    ~/.claude/skills/defect
ln -s ~/just-got-skills/skills/testing/impact    ~/.claude/skills/impact
ln -s ~/just-got-skills/skills/dev/gcm           ~/.claude/skills/gcm
ln -s ~/just-got-skills/skills/dev/pr            ~/.claude/skills/pr
ln -s ~/just-got-skills/skills/dev/story         ~/.claude/skills/story
ln -s ~/just-got-skills/skills/dev/tldr          ~/.claude/skills/tldr
```

`git pull` in `~/just-got-skills` then updates every linked skill in place.

> **`copigot` also needs its subagent** — the `skills` CLI installs skills, not agents:
> ```bash
> cp agents/automation-qa-reviewer.md ~/.claude/agents/
> ```
> Without it, `copigot` falls back to running the same checklist inline (the full checklist ships with the skill as `CHECKLIST.md`).

## Reference

### Testing

- **[questions](./skills/testing/questions/SKILL.md)** — Review a design, API spec, sequence diagram, or requirements document and return at least two pinpointed questions for its authors. Each question cites the document, section or field, and exact quote, says why it matters for testing, offers answer options, and is ranked Blocking, Important, or Minor. Read-only. `/questions`.
- **[scenario](./skills/testing/scenario/SKILL.md)** — Derive traceable QA scenarios from product designs, API specifications, and sequence diagrams; use independent opinions or debate to examine coverage and ambiguity.
- **[copigot](./skills/testing/copigot/SKILL.md)** — Severity-tagged QA review of Playwright + TypeScript automation specs (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`/`NIT`) with `file:line` citations and fix snippets. `/copigot`.
- **[mindmap](./skills/testing/mindmap/SKILL.md)** — QA use-case mind map (`.xmind`) from a feature, user story, or API spec: Validation, Business Scenarios, Security & Edge, Coverage Gaps. Saves a Markdown outline to the repo's `docs/testcases/` and renders the `.xmind` next to it; needs Python 3. `/mindmap`.
- **[probe](./skills/testing/probe/SKILL.md)** — Fill `TBD`/`TBC` expected results, such as an error status, code, or message, from the service's source code or a real API call on a test environment. Reads the code path first, runs a control call before any probe, cites `file:line` or the environment, and marks each value `@observed` for the design owner to confirm. Needs Python 3. `/probe`.
- **[defect](./skills/testing/defect/SKILL.md)** — Turn any QA input (screenshot, API response, DevTools output, automation failure) into a developer-ready Jira bug ticket.
- **[impact](./skills/testing/impact/SKILL.md)** — What a change, PR, or diff can break outside its own lines. Names the one fact the change is safe because of and proves it by running real code, rates confirmed risks with `file:line`, lists what was cleared, and turns risks into regression checks. Read-only toward the project. `/impact`.

### Dev

- **[gcm](./skills/dev/gcm/SKILL.md)** — Caveman-style Conventional Commit messages from the working-tree diff; detects mixed concerns and emits a split-commit plan, warns on likely secrets/PII. Copy-paste text only, never runs git. `/gcm`.
- **[pr](./skills/dev/pr/SKILL.md)** — PR title + description from the diff between the current branch and its base branch, using the repo's real test commands. Follows the repo's `.github/PULL_REQUEST_TEMPLATE.md` when present, otherwise Summary + Test plan. Copy-paste text only, never runs git or `gh pr create`. `/pr`.
- **[story](./skills/dev/story/SKILL.md)** — Copy-ready non-defect Jira Stories and Tasks with required requirements fields, testable acceptance criteria, and explicit unresolved questions.
- **[tldr](./skills/dev/tldr/SKILL.md)** — Summarizes a pull request into a Markdown note in the project's Obsidian vault folder (`prs/`): the change by system part, shortened diffs within 20% of the PR's changed lines, tests checked against their assertions, removed tests, open human review threads, and a QA focus list. Read-only toward GitHub and git; needs `gh`, `jq` and Python 3. `/tldr`.

## Validate

```bash
python3 scripts/validate_skills.py .
python3 -m unittest discover -s tests -v
```

The first command checks skill packaging, links, references between skills, and the naming rules in `AGENTS.md`. The second protects behavior contracts and the XMind renderer.

## Credits

`impact` is adapted from the `blast-radius` skill in poteto's [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT). The skill-writing and behavior rules in `AGENTS.md` draw on its principles.
