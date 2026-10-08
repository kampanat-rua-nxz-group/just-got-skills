from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DRAFT_PR = ROOT / "skills/dev/draft-pr/SKILL.md"
GCM = ROOT / "skills/dev/gcm/SKILL.md"
GCM_REFERENCE = ROOT / "skills/dev/gcm/REFERENCE.md"
JIRA_STORY_TASK = ROOT / "skills/dev/create-jira-story-task/SKILL.md"
BUG_TICKET = ROOT / "skills/testing/create-bug-ticket/SKILL.md"
BUG_TICKET_REFERENCE = ROOT / "skills/testing/create-bug-ticket/REFERENCE.md"
USECASE_MAP = ROOT / "skills/testing/usecase-map/SKILL.md"

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

DRAFT_PR_TEMPLATE_CONTRACT = (
    ".github/PULL_REQUEST_TEMPLATE.md",
    "git show <branch>:.github/PULL_REQUEST_TEMPLATE.md",
    "**repo template**",
    "**skill template**",
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

GCM_INTERACTIVE_STAGING_CONTRACT = (
    "#   hunk 1  src/auth.ts:12-28   guard undefined debCardId        → y",
    "#   hunk 2  src/auth.ts:40-44   rename local in the test helper  → n",
    "#   hunk 3  src/auth.ts:71-95   two concerns in one hunk         → s, then y n",
    "If a hunk still mixes concerns after `s`, say `e` and describe which lines to keep.",
    "# 1b. verify what got staged",
    "git diff --staged",
    "Every skipped hunk must reappear in a later numbered step",
)

BUG_TICKET_DESCRIPTION = (
    "Use when the user wants to document or file a defect from QA evidence "
    "such as text, screenshots, API responses, DevTools output, automation "
    "failures, or production monitoring."
)

BUG_TICKET_SECTIONS = (
    "Title",
    "Environment",
    "Description",
    "Steps to Reproduce",
    "Expected Result",
    "Actual Result",
    "Impact / Severity",
    "Root Cause",
    "Attachments",
    "QA Note",
)

BUG_TICKET_STOP_GUARD = (
    "Flaky / selector / test-data / stale-assertion failures are test fixes — say so and stop",
)

BUG_TICKET_REFERENCE_CONTRACT = (
    "FE Bug",
    "BE Bug",
    "Critical / High / Medium / Low",
    "## Quality Checklist",
)

BUG_TICKET_REFERENCE_ONLY_MATERIAL = (
    "| **Environment** | Staging / Production / Development / UAT |",
    "| **Critical** | System crash, data loss, security issue, complete feature outage blocking all users |",
    "| 1 | **Environment / Configuration** |",
    "- Write in English for two audiences:",
    "- [ ] Title is specific and includes exact component / page / endpoint tag",
)

BUG_TICKET_REFERENCE_LINKS = (
    "[Automation-sourced Bugs](REFERENCE.md#automation-sourced-bugs--triage-before-filing)",
    "[Environment Tables](REFERENCE.md#environment-tables)",
    "[Severity Selection](REFERENCE.md#severity-selection)",
    "[Issue Type Definitions](REFERENCE.md#issue-type-definitions)",
    "[Tone Contract](REFERENCE.md#tone-contract)",
    "[Quality Checklist](REFERENCE.md#quality-checklist)",
)

USECASE_REFERENCE_LINKS = (
    "[annotated example](REFERENCE.md#full-annotated-example)",
    "[operational notes](REFERENCE.md#notes)",
)

README_PRIVATE_ACCESS_CONTRACT = (
    "SKILLS_REPO=git@github.com:kampanat-rua-nxz-group/just-got-skills.git",
    "GITHUB_TOKEN=ghp_xxx npx skills add kampanat-rua-nxz-group/just-got-skills",
)


def frontmatter(path: Path) -> dict[str, str]:
    """Return scalar fields from a skill's YAML frontmatter."""
    lines = path.read_text(encoding="utf-8").splitlines()
    end = lines.index("---", 1)
    return {
        key: value.strip()
        for key, value in (
            line.split(":", 1) for line in lines[1:end] if ":" in line
        )
    }


def body(path: Path) -> str:
    """Return the Markdown body following a skill's frontmatter."""
    text = path.read_text(encoding="utf-8")
    return text.split("---", 2)[2]


def assert_contains_all(text: str, fragments: tuple[str, ...]) -> None:
    """Raise a useful assertion for each missing contract fragment."""
    for fragment in fragments:
        if fragment not in text:
            raise AssertionError(f"missing required fragment: {fragment!r}")


class DevSkillContractTest(unittest.TestCase):
    def test_draft_pr_preserves_command_contract(self):
        assert_contains_all(body(DRAFT_PR), DRAFT_PR_CONTRACT)

    def test_draft_pr_prefers_repository_pr_template(self):
        assert_contains_all(body(DRAFT_PR), DRAFT_PR_TEMPLATE_CONTRACT)

    def test_gcm_preserves_command_contract(self):
        assert_contains_all(body(GCM), GCM_CONTRACT)

    def test_gcm_interactive_staging_reference_preserves_guided_accounting(self):
        reference = GCM_REFERENCE.read_text(encoding="utf-8")

        assert_contains_all(reference, GCM_INTERACTIVE_STAGING_CONTRACT)
        prompt_order = [
            reference.index(fragment)
            for fragment in GCM_INTERACTIVE_STAGING_CONTRACT[:3]
        ]
        self.assertEqual(prompt_order, sorted(prompt_order))
        staged_verification = reference.index("# 1b. verify what got staged")
        staged_diff = reference.index("git diff --staged", staged_verification)
        commit = reference.index("git commit -m \"fix(auth): guard missing card ID\"")
        self.assertLess(staged_verification, staged_diff)
        self.assertLess(staged_diff, commit)

    def test_descriptions_are_trigger_focused_not_output_focused(self):
        for path in (DRAFT_PR, GCM):
            description = frontmatter(path)["description"]
            self.assertTrue(description.startswith("Use when"))
            self.assertIn("user asks", description)
            self.assertTrue("trigger" in description or "invokes" in description)
            self.assertNotIn("Summary + Test plan", description)
            self.assertNotIn("split-commit plan", description)
            self.assertNotIn("copy-paste text", description)


class JiraStoryTaskContractTest(unittest.TestCase):
    REQUIRED_FIELDS = (
        "## Title",
        "## Description",
        "## Background",
        "## Business Rules",
        "## User Story / Details",
        "## Acceptance Criteria",
    )
    OPTIONAL_FIELDS = (
        "## Impact",
        "## Dependencies",
        "## Notes",
        "## Open Questions",
        "## Test Scenarios",
    )

    def setUp(self):
        self.assertTrue(JIRA_STORY_TASK.exists(), "Jira Story/Task skill is missing")

    def test_description_routes_non_defect_jira_work(self):
        description = frontmatter(JIRA_STORY_TASK)["description"]
        self.assertTrue(description.startswith("Use when"))
        self.assertIn("Jira", description)
        self.assertIn("Story", description)
        self.assertIn("Task", description)

    def test_skill_preserves_required_and_optional_field_contract(self):
        entrypoint = body(JIRA_STORY_TASK)
        assert_contains_all(entrypoint, self.REQUIRED_FIELDS)
        assert_contains_all(entrypoint, self.OPTIONAL_FIELDS)
        fields = self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS
        positions = [entrypoint.index(field) for field in fields]
        self.assertEqual(positions, sorted(positions))

    def test_skill_classifies_work_and_routes_defects(self):
        entrypoint = body(JIRA_STORY_TASK)
        assert_contains_all(entrypoint, (
            "Story",
            "Task",
            "create-bug-ticket",
            "TBD",
            "copy-ready",
        ))


class BugTicketContractTest(unittest.TestCase):
    def test_description_is_a_compact_evidence_trigger(self):
        self.assertEqual(frontmatter(BUG_TICKET)["description"], BUG_TICKET_DESCRIPTION)

    def test_skill_keeps_ticket_skeleton_and_automation_stop_guard(self):
        entrypoint = body(BUG_TICKET)

        assert_contains_all(entrypoint, BUG_TICKET_SECTIONS)
        assert_contains_all(entrypoint, BUG_TICKET_STOP_GUARD)
        for fragment in BUG_TICKET_REFERENCE_ONLY_MATERIAL:
            self.assertNotIn(fragment, entrypoint)

    def test_reference_keeps_environment_severity_issue_type_tone_and_checklist(self):
        reference = BUG_TICKET_REFERENCE.read_text(encoding="utf-8")

        assert_contains_all(reference, BUG_TICKET_REFERENCE_CONTRACT)
        assert_contains_all(reference, BUG_TICKET_REFERENCE_ONLY_MATERIAL)

    def test_entrypoint_links_each_routed_reference_section(self):
        assert_contains_all(body(BUG_TICKET), BUG_TICKET_REFERENCE_LINKS)


class UsecaseMapContractTest(unittest.TestCase):
    DESCRIPTION = (
        "Use when the user asks for a QA use-case map, test-case mind map, "
        "scenario coverage, or validation and business-flow coverage for a "
        "feature, user story, or API specification."
    )
    BRANCHES = (
        "### 1. Validation Cases",
        "### 2. Business Scenarios (gated decision tree)",
        "### 3. Cross-cutting (Security & Edge)",
        "### 4. Open Questions / Notes",
        "### 5. Coverage Gaps",
    )
    GATES = (
        "Service reachable?",
        "Dependencies available?",
        "Authenticated?",
        "Authorized?",
        "Business rules",
        "Resource/state",
    )
    COVERAGE_GAPS = (
        "`@TBD` / `TBD` forks",
        "Skipped gates",
        "Continuation with no fail fork",
    )
    LABELS = (
        "`@mock-only`",
        "`@nondeterministic`",
        "`@manual`",
        "`@TBD`",
    )

    def test_description_is_trigger_focused_and_runtime_neutral(self):
        description = frontmatter(USECASE_MAP)["description"]
        self.assertEqual(description, self.DESCRIPTION)
        self.assertNotIn("Markdown outline", description)
        self.assertNotIn(".xmind", description)

    def test_workflow_preserves_taxonomy_gates_and_portable_rendering(self):
        entrypoint = body(USECASE_MAP)

        positions = [entrypoint.index(branch) for branch in self.BRANCHES]
        self.assertEqual(positions, sorted(positions))
        assert_contains_all(entrypoint, self.GATES)
        assert_contains_all(entrypoint, self.COVERAGE_GAPS)
        assert_contains_all(entrypoint, self.LABELS)
        assert_contains_all(entrypoint, (
            "docs/testcases/<feature>-usecase-map.md",
            '"docs/testcases/<Feature Name>.xmind"',
            "python3 <skill-dir>/scripts/md2xmind.py",
            "Outline = source of truth.",
            "platform opener when desktop access is available",
            "report the generated path",
            "the agent",
        ))
        self.assertNotIn("Claude", entrypoint)

    def test_entrypoint_links_annotated_example_and_operational_notes(self):
        assert_contains_all(body(USECASE_MAP), USECASE_REFERENCE_LINKS)

    def test_business_success_result_is_a_leaf_of_the_final_passing_condition(self):
        entrypoint = body(USECASE_MAP)
        reference = (ROOT / "skills/testing/usecase-map/REFERENCE.md").read_text(encoding="utf-8")
        self.assertNotIn("- → Success", entrypoint)
        self.assertNotIn("- → Success", reference)
        self.assertIn("- Balance sufficient\n            - HTTP Status 200", reference)

    def test_outline_highlights_scenario_conditions_with_markdown_bold(self):
        entrypoint = body(USECASE_MAP)
        reference = (ROOT / "skills/testing/usecase-map/REFERENCE.md").read_text(encoding="utf-8")
        self.assertIn("`**text**` → highlight a scenario condition", entrypoint)
        self.assertIn("- **Insufficient balance**", reference)
        self.assertNotIn("[!]", entrypoint)
        self.assertNotIn("[!]", reference)


class SpecHawkContractTest(unittest.TestCase):
    SKILL = ROOT / "skills/testing/spec-hawk/SKILL.md"
    CHECKLIST = ROOT / "skills/testing/spec-hawk/CHECKLIST.md"
    REVIEWER = ROOT / "agents/automation-qa-reviewer.md"
    SHARED_START = "<!-- BEGIN SHARED REVIEW CONTRACT -->"
    SHARED_END = "<!-- END SHARED REVIEW CONTRACT -->"
    CHECKS = tuple(f"### {number}." for number in range(1, 10))
    SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "NIT")

    def shared_contract(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count(self.SHARED_START), 1, path)
        self.assertEqual(text.count(self.SHARED_END), 1, path)
        start = text.index(self.SHARED_START) + len(self.SHARED_START)
        end = text.index(self.SHARED_END)
        self.assertLess(start, end, path)
        return text[start:end]

    def test_reviewer_and_fallback_contracts_are_exactly_equal(self):
        self.assertEqual(
            self.shared_contract(self.CHECKLIST),
            self.shared_contract(self.REVIEWER),
        )

    def test_shared_contract_retains_all_checks_and_report(self):
        for path in (self.CHECKLIST, self.REVIEWER):
            with self.subTest(path=path):
                contract = self.shared_contract(path)
                self.assertEqual(
                    tuple(
                        " ".join(line.split()[:2])
                        for line in contract.splitlines()
                        if line.startswith("### ") and line[4:5].isdigit()
                    ),
                    self.CHECKS,
                )
                assert_contains_all(contract, (
                    "## Discovery before review", "## Severity definitions",
                    "## Output format", "[checklist #N]", "**<file>:<line>**",
                    "```ts", "Omit any severity section that has no findings.",
                ))
                for severity in self.SEVERITIES:
                    assert_contains_all(contract, (
                        f"| **{severity}** |", f"### {severity}",
                    ))

    def test_description_is_trigger_focused(self):
        self.assertEqual(frontmatter(self.SKILL)["description"], (
            "Use when reviewing or auditing Playwright and TypeScript automation "
            "specs, tests, services, models, helpers, or utilities, including "
            "pre-PR checks and the /spec-hawk trigger."
        ))

    def test_entrypoint_retains_nine_areas_and_both_review_branches(self):
        entrypoint = body(self.SKILL)
        assert_contains_all(entrypoint, (
            "nine-area checklist", "dedicated reviewer", "inline fallback",
            "automation-qa-reviewer", "CHECKLIST.md", "read-only",
            "verbatim", "no findings", "Apply the HIGH/CRITICAL fixes?",
            "Review another file?", "Open a PR?",
        ))
        self.assertEqual(entrypoint.count("### Step "), 4)
        self.assertNotIn("8-point", entrypoint)

    def test_review_instructions_use_portable_file_operations(self):
        for path in (self.SKILL, self.CHECKLIST):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                for tool in ("`Glob`", "`Grep`", "`Read`"):
                    self.assertNotIn(tool, text)

    def test_claude_setup_is_conditional_and_preserves_installation_paths(self):
        entrypoint = body(self.SKILL)
        setup_heading = "## Conditional setup: Claude Code"
        self.assertIn(setup_heading, entrypoint)
        portable, setup = entrypoint.split(setup_heading, 1)
        self.assertNotIn("`Agent`", portable)
        assert_contains_all(setup, (
            "agents/automation-qa-reviewer.md", "~/.claude/agents/",
            "<project>/.claude/agents/", "`Agent`",
            'subagent_type: "automation-qa-reviewer"',
        ))


class RepositoryContractTest(unittest.TestCase):
    README = ROOT / "README.md"
    SKILL_LINKS = (
        "[spec-hawk](./skills/testing/spec-hawk/SKILL.md)",
        "[usecase-map](./skills/testing/usecase-map/SKILL.md)",
        "[create-bug-ticket](./skills/testing/create-bug-ticket/SKILL.md)",
        "[gcm](./skills/dev/gcm/SKILL.md)",
        "[draft-pr](./skills/dev/draft-pr/SKILL.md)",
        "[create-jira-story-task](./skills/dev/create-jira-story-task/SKILL.md)",
    )

    def test_readme_documents_catalog_installation_and_validation(self):
        readme = self.README.read_text(encoding="utf-8")
        reference = readme.split("## Reference", 1)[1]
        assert_contains_all(reference, self.SKILL_LINKS)
        assert_contains_all(readme, (
            "python3 scripts/validate_skills.py .",
            "python3 -m unittest discover -s tests -v",
            "Private repo.",
            "cp agents/automation-qa-reviewer.md ~/.claude/agents/",
            *README_PRIVATE_ACCESS_CONTRACT,
        ))


if __name__ == "__main__":
    unittest.main()
