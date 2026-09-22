from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DRAFT_PR = ROOT / "skills/dev/draft-pr/SKILL.md"
GCM = ROOT / "skills/dev/gcm/SKILL.md"
BUG_TICKET = ROOT / "skills/testing/create-bug-ticket/SKILL.md"
BUG_TICKET_REFERENCE = ROOT / "skills/testing/create-bug-ticket/REFERENCE.md"

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

BUG_TICKET_CONTRACT = (
    "Jira bug ticket",
    "debug-mantra",
    "Flaky / selector / test-data / stale-assertion failures are test fixes — say so and stop",
    "FE Bug",
    "BE Bug",
    "Critical / High / Medium / Low",
    "## Quality Checklist",
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

    def test_gcm_preserves_command_contract(self):
        assert_contains_all(body(GCM), GCM_CONTRACT)

    def test_descriptions_are_trigger_focused_not_output_focused(self):
        for path in (DRAFT_PR, GCM):
            description = frontmatter(path)["description"]
            self.assertTrue(description.startswith("Use when"))
            self.assertIn("user asks", description)
            self.assertTrue("trigger" in description or "invokes" in description)
            self.assertNotIn("Summary + Test plan", description)
            self.assertNotIn("split-commit plan", description)
            self.assertNotIn("copy-paste text", description)


class BugTicketContractTest(unittest.TestCase):
    def test_description_is_a_compact_evidence_trigger(self):
        self.assertEqual(frontmatter(BUG_TICKET)["description"], BUG_TICKET_DESCRIPTION)

    def test_jira_template_and_triage_contract_are_preserved(self):
        ticket_contract = body(BUG_TICKET) + BUG_TICKET_REFERENCE.read_text(encoding="utf-8")
        assert_contains_all(ticket_contract, BUG_TICKET_SECTIONS)
        assert_contains_all(ticket_contract, BUG_TICKET_CONTRACT)


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


if __name__ == "__main__":
    unittest.main()
