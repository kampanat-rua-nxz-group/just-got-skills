# Compatibility-First Skill Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize all five skills for reliable invocation, lower context load, portability, and maintainability without changing their outputs or behavior.

**Architecture:** Keep each `SKILL.md` as the compact execution entrypoint, move branch-specific detail into clearly routed references, and protect every observable contract with standard-library validation. Treat the duplicated Spec Hawk review contract as packaged duplication: retain both installable copies but make drift a test failure.

**Tech Stack:** Markdown, Python 3 standard library, `unittest`, Git

**Spec:** `docs/superpowers/specs/2026-09-22-skill-optimization-design.md`

## Global Constraints

- Preserve every compatibility contract in the approved spec.
- Keep validation dependency-free; PyYAML is not available in the current environment.
- Keep every skill read/write boundary unchanged.
- Preserve `md2xmind.py`'s command-line interface and XMind 2020+ archive format.
- Keep the dedicated `automation-qa-reviewer` and Spec Hawk's inline fallback behaviorally identical.
- Make only repository-scoped changes; do not modify installed copies under `~/.agents`, `~/.claude`, or `~/.codex`.

## Review Focus

- A shortened description must retain every current trigger branch; `test_skill_contracts.py` pins the distinctive phrases and accepted request categories.
- Moving guidance into a reference must not make it unreachable; `test_skill_repository.py` resolves every local Markdown link and requires explicit routing text.
- Spec Hawk's reviewer and fallback can silently diverge; `test_spec_hawk_contract_is_synchronized` compares their marked shared sections byte-for-byte.
- XMind rendering can preserve exit status while corrupting hierarchy or metadata; `test_md2xmind.py` inspects the archive and parsed topic tree.
- Runtime-neutral wording can accidentally remove Claude Code support; contract tests require both capability-neutral execution and the existing Claude reviewer installation path.

---

### Task 1: Add dependency-free repository validation

**Files:**

- Create: `scripts/validate_skills.py`
- Create: `tests/test_skill_repository.py`

**Interfaces:**

- Consumes: skill folders under `skills/*/*`, Markdown links, YAML frontmatter limited to fields used by this repository.
- Produces: `validate_repository(root: Path) -> list[str]`; CLI exits `0` with `Validated 5 skills` or exits `1` after printing one error per line.

- [ ] **Step 1: Write failing validator unit tests**

Create `tests/test_skill_repository.py` with temporary repositories that cover valid skills, a folder/name mismatch, a missing local Markdown link, unfinished scaffold markers, and a malformed frontmatter boundary. Include one integration assertion that discovers all five current skills:

```python
from pathlib import Path
import tempfile
import unittest

from scripts.validate_skills import validate_repository


ROOT = Path(__file__).resolve().parents[1]


class SkillRepositoryValidationTest(unittest.TestCase):
    def write_skill(self, root: Path, folder: str, body: str) -> Path:
        skill_dir = root / "skills" / "testing" / folder
        skill_dir.mkdir(parents=True)
        path = skill_dir / "SKILL.md"
        path.write_text(body, encoding="utf-8")
        return path

    def test_accepts_valid_skill_and_local_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "example-skill",
                "---\nname: example-skill\ndescription: Use when reviewing examples.\n---\n"
                "Read [the reference](REFERENCE.md) when exact rules are needed.\n",
            )
            (root / "skills/testing/example-skill/REFERENCE.md").write_text(
                "# Reference\n", encoding="utf-8"
            )
            self.assertEqual([], validate_repository(root))

    def test_reports_name_link_frontmatter_and_scaffold_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "wrong-folder",
                "---\nname: other-name\ndescription: Use when testing.\n---\n"
                "Read [missing](REFERENCE.md).\n" + "TO" + "DO: replace scaffold.\n",
            )
            errors = "\n".join(validate_repository(root))
            self.assertIn("folder/name mismatch", errors)
            self.assertIn("missing local link", errors)
            self.assertIn("unfinished scaffold", errors)

    def test_current_repository_has_five_discoverable_skills(self):
        skill_files = sorted(ROOT.glob("skills/*/*/SKILL.md"))
        self.assertEqual(5, len(skill_files))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the validator tests to verify RED**

Run: `python3 -m unittest tests.test_skill_repository -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.validate_skills'`.

- [ ] **Step 3: Implement the minimal validator**

Create `scripts/validate_skills.py` using only `argparse`, `pathlib`, `re`, and `sys`:

```python
#!/usr/bin/env python3
"""Validate every skill package in this repository."""

import argparse
from pathlib import Path
import re
import sys


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
UNFINISHED_MARKERS = ("TO" + "DO", "implement " + "later", "fill in " + "details")


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Return the simple scalar/folded fields used by this repository."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter boundary")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter boundary") from exc

    fields: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        if not line or line.startswith((" ", "\t")) or ":" not in line:
            index += 1
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"\'')
        if value in {">", "|"}:
            folded: list[str] = []
            index += 1
            while index < end and (
                not lines[index] or lines[index].startswith((" ", "\t"))
            ):
                folded.append(lines[index].strip())
                index += 1
            fields[key] = " ".join(part for part in folded if part)
            continue
        fields[key] = value
        index += 1
    return fields


def local_markdown_links(path: Path) -> list[str]:
    """Return relative Markdown link targets, excluding URLs and anchors."""
    links: list[str] = []
    for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
        target = target.strip().strip("<>").split("#", 1)[0]
        if target and "://" not in target and not target.startswith("mailto:"):
            links.append(target)
    return links


def validate_skill(skill_file: Path) -> list[str]:
    """Check frontmatter, folder/name agreement, links, and scaffold markers."""
    errors: list[str] = []
    relative = skill_file.as_posix()
    try:
        fields = parse_frontmatter(skill_file)
    except ValueError as exc:
        return [f"{relative}: {exc}"]

    name = fields.get("name", "")
    description = fields.get("description", "")
    if name != skill_file.parent.name:
        errors.append(
            f"{relative}: folder/name mismatch "
            f"({skill_file.parent.name!r} != {name!r})"
        )
    if not description:
        errors.append(f"{relative}: missing description")

    for target in local_markdown_links(skill_file):
        if not (skill_file.parent / target).exists():
            errors.append(f"{relative}: missing local link {target}")

    text = skill_file.read_text(encoding="utf-8")
    for marker in UNFINISHED_MARKERS:
        if marker in text:
            errors.append(f"{relative}: unfinished scaffold marker {marker!r}")
    return errors


def validate_repository(root: Path) -> list[str]:
    """Return sorted validation errors for every skills/*/*/SKILL.md."""
    errors: list[str] = []
    for skill_file in sorted(root.glob("skills/*/*/SKILL.md")):
        errors.extend(validate_skill(skill_file))
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate_repository(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    count = len(list(root.glob("skills/*/*/SKILL.md")))
    print(f"Validated {count} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The parser supports single-line values and the folded `description: >` form already used by `create-bug-ticket`. The unfinished-marker set deliberately excludes the undefined-value token used as valid domain output by `usecase-map`.

- [ ] **Step 4: Run the validator tests to verify GREEN**

Run: `python3 -m unittest tests.test_skill_repository -v`

Expected: PASS, 3 tests.

- [ ] **Step 5: Run the validator against the repository**

Run: `python3 scripts/validate_skills.py .`

Expected: `Validated 5 skills`.

- [ ] **Step 6: Commit the validator foundation**

```bash
git add scripts/validate_skills.py tests/test_skill_repository.py
git commit -m "test: add dependency-free skill validation"
```

### Task 2: Optimize draft-pr and gcm without changing generated commands

**Files:**

- Create: `tests/test_skill_contracts.py`
- Modify: `skills/dev/draft-pr/SKILL.md`
- Modify: `skills/dev/gcm/SKILL.md`
- Modify: `skills/dev/gcm/REFERENCE.md`

**Interfaces:**

- Consumes: repository Git state and repository-discovered test/commitlint configuration.
- Produces: the existing fenced `gh pr create` command contract and existing runnable `git add`/`git commit -m` plans.

- [ ] **Step 1: Write failing contract tests for both dev skills**

Create `tests/test_skill_contracts.py` with helpers `frontmatter(path)`, `body(path)`, and `assert_contains_all(text, fragments)`. Add tests that require:

```python
DRAFT_PR_CONTRACT = (
    "gh pr create",
    "## Summary",
    "## Test plan",
    "--base",
    "--title",
    "--body",
    "git log",
    "git diff",
)

GCM_CONTRACT = (
    "git status --short",
    "git diff --staged",
    "git commit -m",
    "git add -p",
    "git diff --staged",
    "Diff may contain a secret/PII",
    "Run tests/typecheck before committing",
)
```

Also assert that both descriptions begin with `Use when`, contain trigger conditions, and omit output mechanics such as `Summary + Test plan`, `split-commit plan`, and `copy-paste text`.

- [ ] **Step 2: Run the dev-skill contract tests to verify RED**

Run: `python3 -m unittest tests.test_skill_contracts.DevSkillContractTest -v`

Expected: FAIL because both descriptions currently summarize output mechanics.

- [ ] **Step 3: Refactor draft-pr's entrypoint**

Change the description to:

```yaml
description: Use when the user asks to draft, write, or improve a pull request title or description from a branch diff, including the /draft-pr trigger.
```

Rewrite the body into: purpose/read-only boundary, five ordered steps with completion criteria, output contract, and failure handling. Preserve the exact fenced `gh pr create` example, multi-branch rule, base detection behavior, 70-character title bound, and repository-derived test plan.

- [ ] **Step 4: Refactor gcm with progressive disclosure**

Change the description to:

```yaml
description: Use when the user asks for Conventional Commit wording, wants to commit current changes, needs a commit split, or invokes gcm.
```

Keep diff inspection, concern grouping, secret scanning, commitlint verification, output form, and the final reminder in `SKILL.md`. Move the detailed prompt-by-prompt `git add -p` walkthrough and key table into `REFERENCE.md` under `## Interactive staging`, replacing it in `SKILL.md` with this mandatory pointer:

```markdown
When any file contains mixed concerns, read [REFERENCE.md](REFERENCE.md#interactive-staging) before producing output; it defines the required hunk-by-hunk walkthrough and accounting rule.
```

Retain the full conventional rule table in `REFERENCE.md` as its existing single source of truth.

- [ ] **Step 5: Run focused and repository validation**

Run:

```bash
python3 -m unittest tests.test_skill_contracts.DevSkillContractTest -v
python3 scripts/validate_skills.py .
```

Expected: both commands PASS; validator reports `Validated 5 skills`.

- [ ] **Step 6: Commit the dev skill optimization**

```bash
git add tests/test_skill_contracts.py skills/dev/draft-pr/SKILL.md skills/dev/gcm/SKILL.md skills/dev/gcm/REFERENCE.md
git commit -m "docs(dev): optimize commit and PR skills"
```

### Task 3: Optimize create-bug-ticket while preserving the Jira template

**Files:**

- Modify: `tests/test_skill_contracts.py`
- Modify: `skills/testing/create-bug-ticket/SKILL.md`
- Modify: `skills/testing/create-bug-ticket/REFERENCE.md`

**Interfaces:**

- Consumes: text, screenshot-derived facts, API responses, DevTools output, or automation failures.
- Produces: the same ten-section English Jira ticket or a stop decision for a non-product automation failure.

- [ ] **Step 1: Add a failing bug-ticket contract test**

Require the description to begin with `Use when` and retain the five evidence/request branches: bug report, Jira ticket, screenshot/evidence, API or DevTools output, and automation/monitoring failure. Require the body/reference union to contain all ten section names, `debug-mantra`, the test-failure stop conditions, FE/BE environment tables, four severity levels, and the quality checklist.

- [ ] **Step 2: Run the focused test to verify RED**

Run: `python3 -m unittest tests.test_skill_contracts.BugTicketContractTest -v`

Expected: FAIL because the current description mixes capability and trigger wording instead of acting as a compact trigger pointer.

- [ ] **Step 3: Refactor the entrypoint and reference**

Use this description:

```yaml
description: Use when the user wants to document or file a defect from QA evidence such as text, screenshots, API responses, DevTools output, automation failures, or production monitoring.
```

Keep source classification, automation confirmation, missing-information rules, and the ten output sections in `SKILL.md`. Replace negative stylistic phrasing with the positive ticket contract where doing so does not weaken a hard guardrail. Consolidate severity selection, issue types, environment tables, tone, and the final checklist in `REFERENCE.md`, with explicit pointers from the steps that need each section.

- [ ] **Step 4: Run focused and repository validation**

Run:

```bash
python3 -m unittest tests.test_skill_contracts.BugTicketContractTest -v
python3 scripts/validate_skills.py .
```

Expected: PASS.

- [ ] **Step 5: Commit the bug-ticket optimization**

```bash
git add tests/test_skill_contracts.py skills/testing/create-bug-ticket/SKILL.md skills/testing/create-bug-ticket/REFERENCE.md
git commit -m "docs(testing): optimize bug ticket skill"
```

### Task 4: Make Spec Hawk portable and enforce reviewer/fallback synchronization

**Files:**

- Modify: `tests/test_skill_contracts.py`
- Modify: `skills/testing/spec-hawk/SKILL.md`
- Modify: `skills/testing/spec-hawk/CHECKLIST.md`
- Modify: `agents/automation-qa-reviewer.md`

**Interfaces:**

- Consumes: one named Playwright/TypeScript file, folder, or diff description plus repository conventions.
- Produces: the existing severity report; dedicated reviewer execution when available, otherwise the same checklist inline.

- [ ] **Step 1: Add failing portability and synchronization tests**

Add `SpecHawkContractTest` that asserts:

```python
SHARED_START = "<!-- BEGIN SHARED REVIEW CONTRACT -->"
SHARED_END = "<!-- END SHARED REVIEW CONTRACT -->"
CHECKS = tuple(f"### {number}." for number in range(1, 10))
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "NIT")
```

Extract the text between the markers from `CHECKLIST.md` and `automation-qa-reviewer.md` and require exact equality. Require `SKILL.md` to say nine checklist areas, retain the reviewer and inline branches, and use capability-neutral wording for file search/read operations. Require the Claude installation path to remain documented.

- [ ] **Step 2: Run the Spec Hawk tests to verify RED**

Run: `python3 -m unittest tests.test_skill_contracts.SpecHawkContractTest -v`

Expected: FAIL because there are no synchronization markers, the documents differ, and `SKILL.md` still says eight checklist areas.

- [ ] **Step 3: Establish one marked shared review contract**

In `CHECKLIST.md`, place the markers around discovery, checklist items 1–9, severity definitions, and output format. Copy that exact marked section into `agents/automation-qa-reviewer.md`. Keep agent-only frontmatter, tool restrictions, and final behavioral rules outside the markers.

- [ ] **Step 4: Refactor Spec Hawk's entrypoint**

Use this description:

```yaml
description: Use when reviewing or auditing Playwright and TypeScript automation specs, tests, services, models, helpers, or utilities, including pre-PR checks and the /spec-hawk trigger.
```

Keep four steps: resolve target, select dedicated reviewer or inline fallback, return the report unchanged, and offer the existing next actions. Describe reviewer invocation by capability first; put the Claude Code `automation-qa-reviewer` installation and `Agent`-tool details in a clearly labeled conditional setup section. Change “8-point checklist” to “nine-area checklist.”

- [ ] **Step 5: Run focused and repository validation**

Run:

```bash
python3 -m unittest tests.test_skill_contracts.SpecHawkContractTest -v
python3 scripts/validate_skills.py .
```

Expected: PASS and exact shared-section equality.

- [ ] **Step 6: Commit the Spec Hawk optimization**

```bash
git add tests/test_skill_contracts.py skills/testing/spec-hawk/SKILL.md skills/testing/spec-hawk/CHECKLIST.md agents/automation-qa-reviewer.md
git commit -m "docs(spec-hawk): enforce portable synchronized review"
```

### Task 5: Protect the XMind renderer and optimize usecase-map

**Files:**

- Create: `tests/test_md2xmind.py`
- Modify: `tests/test_skill_contracts.py`
- Modify: `skills/testing/usecase-map/SKILL.md`
- Modify: `skills/testing/usecase-map/REFERENCE.md`
- Verify unchanged behavior: `skills/testing/usecase-map/scripts/md2xmind.py`

**Interfaces:**

- Consumes: Markdown with headings, two-space bullet nesting, notes, priorities, `[!]`, and labels.
- Produces: an XMind archive with `content.json`, `metadata.json`, and `manifest.json`; CLI errors retain line numbers.

- [ ] **Step 1: Write renderer characterization tests**

Create `tests/test_md2xmind.py` that imports the script via `importlib.util.spec_from_file_location`. Cover:

```python
VALID_OUTLINE = """# Payments [!]
## Validation Cases
- POST /payments @security
  > contract note
  - valid request [P1]
    - HTTP Status 200
## Business Scenarios
- service available
## Cross-cutting (Security & Edge)
- oversized payload
## Coverage Gaps
- none
"""
```

Assert one root, four root children in fixed order, same-indent siblings, note content, `symbol-exclam`, `priority-1`, and the `security` label. Write an archive in `TemporaryDirectory` and assert its three filenames and JSON metadata. Add invalid cases for a note before a topic, multiple roots, and unrecognized text; each must raise `ValueError` containing `Line <number>` where applicable. These characterize current behavior without tightening the accepted outline grammar.

- [ ] **Step 2: Run renderer tests to establish GREEN characterization**

Run: `python3 -m unittest tests.test_md2xmind -v`

Expected: PASS against the unchanged renderer. If a test fails because it describes behavior the current script does not provide, correct the test to the approved compatibility contract rather than changing production code.

- [ ] **Step 3: Add a failing usecase-map skill contract test**

Require all four branch headings in order, the seven gate concepts, coverage-gap categories, labels, output locations, renderer command, source-of-truth rule, and conditional open behavior. Require the description to contain trigger conditions without workflow/output mechanics and require runtime-neutral authoring language.

- [ ] **Step 4: Run the skill contract test to verify RED**

Run: `python3 -m unittest tests.test_skill_contracts.UsecaseMapContractTest -v`

Expected: FAIL because the description summarizes output mechanics and the body names Claude as the author.

- [ ] **Step 5: Refactor the usecase-map documentation**

Use this description:

```yaml
description: Use when the user asks for a QA use-case map, test-case mind map, scenario coverage, or validation and business-flow coverage for a feature, user story, or API specification.
```

Keep the five-step workflow, four-branch taxonomy, gate order, expected-result leaf rule, labels, and outline conventions in `SKILL.md` because every invocation needs them. Move the annotated example and file-format compatibility notes to `REFERENCE.md`. Replace Claude-specific authoring language with `the agent`. Make opening conditional: use the platform opener when desktop access is available; otherwise report the generated path. The Markdown and `.xmind` locations stay unchanged.

- [ ] **Step 6: Run focused validation**

Run:

```bash
python3 -m unittest tests.test_md2xmind -v
python3 -m unittest tests.test_skill_contracts.UsecaseMapContractTest -v
python3 scripts/validate_skills.py .
```

Expected: PASS; renderer file remains behaviorally unchanged.

- [ ] **Step 7: Commit the use-case map optimization**

```bash
git add tests/test_md2xmind.py tests/test_skill_contracts.py skills/testing/usecase-map/SKILL.md skills/testing/usecase-map/REFERENCE.md
git commit -m "docs(usecase-map): optimize portable map workflow"
```

### Task 6: Document validation and run the compatibility gate

**Files:**

- Modify: `README.md`
- Modify: `tests/test_skill_contracts.py`

**Interfaces:**

- Consumes: the complete optimized repository.
- Produces: one documented validation command and a final compatibility result for all five skills.

- [ ] **Step 1: Add the final repository contract test**

Add `RepositoryContractTest` that checks the README lists all five skills, documents `python3 scripts/validate_skills.py .` and `python3 -m unittest discover -s tests -v`, retains the private-repository install warning, and retains the Claude reviewer installation command.

- [ ] **Step 2: Run the README contract test to verify RED**

Run: `python3 -m unittest tests.test_skill_contracts.RepositoryContractTest -v`

Expected: FAIL because the validation commands are not documented yet.

- [ ] **Step 3: Update README portability and validation guidance**

Keep the current install instructions and five-skill catalog. Change the opening sentence from Claude-only to agent-skill wording, retain Claude Code as a supported runtime, and add:

````markdown
## Validate

```bash
python3 scripts/validate_skills.py .
python3 -m unittest discover -s tests -v
```
````

Explain that the first command checks skill packaging and links while the second protects behavior contracts and the XMind renderer.

- [ ] **Step 4: Run all validation**

Run:

```bash
python3 scripts/validate_skills.py .
python3 -m unittest discover -s tests -v
python3 -m py_compile skills/testing/usecase-map/scripts/md2xmind.py
git diff --check
```

Expected: validator reports `Validated 5 skills`; all tests PASS; compilation and diff checks exit `0`. Move any generated `__pycache__` outside the worktree before checking status.

- [ ] **Step 5: Review the diff against every compatibility contract**

Run:

```bash
git diff 66f7fa1 --stat
git diff 66f7fa1 -- skills agents README.md scripts tests
git status --short
```

Confirm every file belongs to the approved scope, every trigger branch remains represented, all five output contracts are pinned by tests, and no generated artifacts are present.

- [ ] **Step 6: Commit the repository documentation**

```bash
git add README.md tests/test_skill_contracts.py
git commit -m "docs: add skill repository validation guide"
```

- [ ] **Step 7: Run the post-commit verification gate**

Run:

```bash
python3 scripts/validate_skills.py .
python3 -m unittest discover -s tests -v
git status --short
```

Expected: validator and tests PASS; working tree is clean.
