import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/testing/usecase/scripts/md2xmind.py"
SPEC = importlib.util.spec_from_file_location("md2xmind", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
md2xmind = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(md2xmind)


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


class Md2XmindTest(unittest.TestCase):
    def test_parse_outline_preserves_topics_notes_and_markers(self):
        root = md2xmind.parse_outline(VALID_OUTLINE)

        self.assertEqual(root.title, "Payments")
        self.assertEqual([marker for marker in root.markers], ["symbol-exclam"])
        self.assertEqual(
            [topic.title for topic in root.children],
            [
                "Validation Cases",
                "Business Scenarios",
                "Cross-cutting (Security & Edge)",
                "Coverage Gaps",
            ],
        )

        endpoint = root.children[0].children[0]
        self.assertEqual(endpoint.title, "POST /payments")
        self.assertEqual(endpoint.labels, ["security"])
        self.assertEqual(endpoint.note_lines, ["contract note"])
        self.assertEqual(endpoint.children[0].markers, ["priority-1"])
        self.assertEqual(endpoint.children[0].children[0].title, "HTTP Status 200")

    def test_same_indent_bullets_are_siblings(self):
        root = md2xmind.parse_outline("""# Root
## Branch
- first
- second
""")

        self.assertEqual(
            [topic.title for topic in root.children[0].children],
            ["first", "second"],
        )

    def test_markdown_bold_highlights_outline_only(self):
        root = md2xmind.parse_outline("""# Transfers
## Business Scenarios
- **Balance insufficient**
  - HTTP Status 422
""")

        scenario = root.children[0].children[0]
        self.assertEqual(scenario.title, "Balance insufficient")
        self.assertEqual(scenario.markers, [])
        content = json.loads(md2xmind.build_content_json(root))
        rendered = content[0]["rootTopic"]["children"]["attached"][0]["children"]["attached"][0]
        self.assertEqual(rendered["title"], "Balance insufficient")
        self.assertNotIn("markers", rendered)

    def test_write_xmind_serializes_native_archive_content(self):
        root = md2xmind.parse_outline(VALID_OUTLINE)
        content = md2xmind.build_content_json(root)

        with TemporaryDirectory() as directory:
            archive = Path(directory) / "payments.xmind"
            md2xmind.write_xmind(content, archive)
            with zipfile.ZipFile(archive) as zf:
                self.assertEqual(
                    set(zf.namelist()),
                    {"content.json", "metadata.json", "manifest.json"},
                )
                serialized = json.loads(zf.read("content.json"))
                self.assertEqual(len(serialized), 1)
                root_topic = serialized[0]["rootTopic"]
                self.assertEqual(root_topic["title"], "Payments")
                self.assertEqual(
                    root_topic["markers"], [{"markerId": "symbol-exclam"}]
                )
                branches = root_topic["children"]["attached"]
                self.assertEqual(
                    [branch["title"] for branch in branches],
                    [
                        "Validation Cases",
                        "Business Scenarios",
                        "Cross-cutting (Security & Edge)",
                        "Coverage Gaps",
                    ],
                )
                endpoint = branches[0]["children"]["attached"][0]
                self.assertEqual(endpoint["title"], "POST /payments")
                self.assertEqual(endpoint["labels"], ["security"])
                self.assertEqual(
                    endpoint["notes"], {"plain": {"content": "contract note"}}
                )
                valid_request = endpoint["children"]["attached"][0]
                self.assertEqual(
                    valid_request["markers"], [{"markerId": "priority-1"}]
                )
                self.assertEqual(
                    valid_request["children"]["attached"][0]["title"],
                    "HTTP Status 200",
                )
                self.assertEqual(
                    json.loads(zf.read("metadata.json")),
                    {
                        "dataStructureVersion": "2",
                        "creator": {
                            "name": "md2xmind",
                            "version": "2.0.0",
                            "platform": "python",
                        },
                        "layoutEngineVersion": "3",
                    },
                )

    def test_cli_renders_valid_outline(self):
        with TemporaryDirectory() as directory:
            directory_path = Path(directory)
            outline = directory_path / "payments.md"
            archive = directory_path / "payments.xmind"
            outline.write_text(VALID_OUTLINE, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(outline), "-o", str(archive)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(archive.is_file())
            self.assertIn(f"Created: {archive} (11 topics)", result.stdout)

    def test_cli_rejects_invalid_outline_with_line_specific_error(self):
        with TemporaryDirectory() as directory:
            directory_path = Path(directory)
            outline = directory_path / "invalid.md"
            archive = directory_path / "invalid.xmind"
            outline.write_text("# Root\nplain text\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(outline), "-o", str(archive)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error: Line 2: unrecognized outline line", result.stderr)
            self.assertFalse(archive.exists())

    def test_parse_outline_rejects_note_before_topic_with_line_number(self):
        with self.assertRaisesRegex(ValueError, r"Line 1"):
            md2xmind.parse_outline("> orphan note\n# Root\n")

    def test_parse_outline_rejects_multiple_roots_with_line_number(self):
        with self.assertRaisesRegex(ValueError, r"Line 2"):
            md2xmind.parse_outline("# First\n# Second\n")

    def test_parse_outline_rejects_unrecognized_text_with_line_number(self):
        with self.assertRaisesRegex(ValueError, r"Line 2"):
            md2xmind.parse_outline("# Root\nplain text\n")

    FLAT_SCENARIOS = """# Withdrawals
## Business Scenarios
- Submit withdrawal
  - Authenticated?
    - Invalid key
      - HTTP Status 401
    - authenticated → continue
  - Balance sufficient?
    - Insufficient
      - HTTP Status 400
    - Balance sufficient → Success
      - HTTP Status 200
## Open Questions / Notes
- Is the minimum per currency?
- Who owns the fee table?
"""

    NESTED_SCENARIOS = """# Withdrawals
## Business Scenarios
- Submit withdrawal
  - Authenticated?
    - Invalid key
      - HTTP Status 401
    - Authenticated
      - Balance sufficient?
        - Insufficient
          - HTTP Status 400
        - Balance sufficient → Success
          - HTTP Status 200
## Journey: Withdraw (1 of 2) — Submit
- Submitted
  - Committed → continues in Journey 2 (Send)
"""

    def test_lint_flags_flat_gates_and_continue_leaves_only_in_scenario_trees(self):
        problems = md2xmind.lint_outline(md2xmind.parse_outline(self.FLAT_SCENARIOS))

        self.assertEqual(len(problems), 2, problems)
        self.assertIn("gates listed flat", problems[0])
        self.assertIn("'continue' leaf", problems[1])

    def test_lint_accepts_nested_chain_and_journey_pointer_leaf(self):
        root = md2xmind.parse_outline(self.NESTED_SCENARIOS)

        self.assertEqual(md2xmind.lint_outline(root), [])

    def test_lint_flags_journey_deeper_than_limit(self):
        lines = ["# Flow", "## Journey: Long"]
        lines += [f"{'  ' * level}- step {level}" for level in range(12)]
        problems = md2xmind.lint_outline(md2xmind.parse_outline("\n".join(lines)))

        self.assertEqual(len(problems), 1, problems)
        self.assertIn("12 levels deep", problems[0])

    def test_cli_check_fails_on_flat_outline_without_writing(self):
        with TemporaryDirectory() as directory:
            outline = Path(directory) / "flat.md"
            outline.write_text(self.FLAT_SCENARIOS, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(outline), "--check"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Nesting: Business Scenarios > Submit withdrawal", result.stderr)
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["flat.md"])


if __name__ == "__main__":
    unittest.main()
