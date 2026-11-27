from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/testing/probe/SKILL.md"
SCRIPT = ROOT / "skills/testing/probe/scripts/list_tbd.py"

OUTLINE = """# Payments API
## Validation Cases
- POST /payments
  - Headers
    - content-type
      - Content-Type mismatch @TBD
        - Sample input: Content-Type=text/plain
          - HTTP Status TBD
          - error code tbc
  - Request body
    - amount
      - Omit field
        - Sample input: body without amount
          - HTTP Status 400
## Coverage Gaps
- @TBD forks
  - Content-Type mismatch — HTTP status TBD
"""


def run(*paths):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, paths)],
        capture_output=True,
        text=True,
        check=False,
    )


class ListTbdTest(unittest.TestCase):
    def test_lists_open_cases_with_branch_path_and_skips_coverage_gaps(self):
        with TemporaryDirectory() as directory:
            outline = Path(directory) / "payments.md"
            outline.write_text(OUTLINE, encoding="utf-8")

            result = run(outline)

            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(len(lines), 3, lines)
            self.assertEqual(
                lines[1],
                f"{outline}:8: Payments API > Validation Cases > POST /payments > Headers "
                "> content-type > Content-Type mismatch @TBD "
                "> Sample input: Content-Type=text/plain > HTTP Status TBD",
            )
            self.assertTrue(lines[2].endswith("> error code tbc"))
            self.assertNotIn("Coverage Gaps", result.stdout)

    def test_exits_one_when_no_open_cases_remain(self):
        with TemporaryDirectory() as directory:
            outline = Path(directory) / "done.md"
            outline.write_text("# API\n## Validation Cases\n- HTTP Status 400\n", encoding="utf-8")

            result = run(outline)

            self.assertEqual(result.returncode, 1)
            self.assertIn("No TBD or TBC cases found", result.stderr)

    def test_reports_unreadable_file(self):
        result = run(ROOT / "missing-outline.md")

        self.assertEqual(result.returncode, 2)
        self.assertIn("Error:", result.stderr)


class ProbeContractTest(unittest.TestCase):
    def test_description_is_trigger_focused(self):
        text = SKILL.read_text(encoding="utf-8")
        description = text.split("description:", 1)[1].splitlines()[0]
        self.assertIn("Use when", description)
        self.assertIn("/probe", description)

    def test_entrypoint_keeps_source_order_and_live_call_guards(self):
        entrypoint = SKILL.read_text(encoding="utf-8").split("---", 2)[2]
        order = ("**Code first.**", "**Live call.**", "**Both.**")
        positions = [entrypoint.index(item) for item in order]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "**observed behavior**, not a requirement",
            "`@observed`",
            "Never call production.",
            "**Run a control call first.**",
            "**Change exactly one thing**",
            "**Ask before a call that can change state you cannot undo**",
            "**Redact**",
            "Stay read-only toward the service repository.",
            "never pick one",
            "`cited` (code) or `verified` (live call)",
            "**Still TBD**",
            "**Conflicts**",
            "**For the design owner**",
        ):
            self.assertIn(fragment, entrypoint)


if __name__ == "__main__":
    unittest.main()
