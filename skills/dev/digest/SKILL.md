---
name: digest
description: Use when the user asks to summarize a pull request into the Obsidian vault, write or update a PR review note, or invokes /digest.
argument-hint: "[PR number, URL or branch; default: the PR of the current branch]"
---

# digest — PR summary note for the vault

Write one Markdown note that gives a QA lead the direction of a pull request without reading all of its code: what changed and why, the contracts between the moving parts, what the tests now prove, and where the risk sits. The note lives in the Obsidian vault next to the project it belongs to.

**Read-only toward GitHub and git.** Never edit, comment on, approve or merge the PR, and never run `git add`, `git commit` or `git push`. The only file you write is the vault note (plus scratch files).

`<skill>` below is the folder of this file.

## Steps

1. **Gather.** From the PR's repo, run `bash <skill>/scripts/gather.sh <scratch>/<repo>-<pr> [<pr>]`. It writes `pr.json`, `description.md`, `files.tsv`, `full.diff`, `threads.json`, `test-changes.tsv` and `linked-prs.tsv`, and prints the budget, the open human review threads and the removed tests. Done when it exits 0.
2. **Find the note.** Vault root: `$SUMMARIZE_PR_VAULT` when set, else the vault the workspace instructions name, else ask. Project folder: the one folder whose `_index.md` frontmatter has `project: <repo name>` (`grep -rl --include=_index.md "^project: <repo>$" <vault>`); when none has the key, the one folder named exactly after the repo (`find <vault> -type d -name <repo> -not -path '*/.*'`). Follow the vault's own schema file (its `CLAUDE.md` or naming conventions) where it differs from the template. The note is `<project folder>/prs/YYYY-MM-DD-pr-<n>-<title-slug>.md`, dated today. If a `*-pr-<n>-*.md` note already exists there, update it in place (see [Updating a note](REFERENCE.md#updating-a-note)). Ask the user when no folder or several folders match, or when `prs/` does not exist yet. Done when one path is confirmed.
3. **Read.** Read `description.md`, `threads.json` and `full.diff`, then the changed code at the head commit (`git show "${sha}:<path>"`; braces matter in zsh) until you can name the contracts, the moving parts and the hot paths. For each new file, find the old code it replaces. Done when every file in `files.tsv` is either placed in the story or consciously left out.
4. **Verify tests.** For each test you will list, read its full body at the head commit and compare its name with its assertions (see [Tests](REFERENCE.md#tests)). Every `removed` row in `test-changes.tsv` goes in the note, or is named in the `replaces` of the test that took its place. Done when each listed test is checked against its body.
5. **Write** the note from the [note template](REFERENCE.md#note-template), following [Content rules](REFERENCE.md#content-rules). Shown changed lines stay within 20% of the PR's additions + deletions.
6. **Check.** Run `python3 <skill>/scripts/check_note.py <note> <scratch>/<repo>-<pr>/pr.json <scratch>/<repo>-<pr>/test-changes.tsv`. Fix every `error:` line and run it again. Then walk the [pre-flight list](REFERENCE.md#pre-flight) against the note. Done when the script exits 0 and every pre-flight item holds.
7. **Report.** Give the user the note path, the `shown N / budget M` line, and any test whose code name misrepresents what it checks, so the author can rename it.

## Data safety

The note sits in a synced vault. Copy code only as shortened snippets. Replace secrets, keys, mnemonics, connection strings, customer data, wallet addresses and internal hostnames with placeholders such as `[API_KEY]` or `[WALLET_ADDRESS]`. If the diff itself contains a live credential, stop and tell the user to rotate it; leave it out of the note.
