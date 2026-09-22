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


if __name__ == "__main__":
    unittest.main()
