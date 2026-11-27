import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/dev/recap"
SCRIPTS = SKILL_DIR / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DIFF = """diff --git a/tests/orders.spec.ts b/tests/orders.spec.ts
index 1111111..2222222 100644
--- a/tests/orders.spec.ts
+++ b/tests/orders.spec.ts
@@ -10,6 +10,6 @@ test.describe("orders", () => {
 \tconst base = 1
-\ttest("rejects an empty cart", async () => {
+\ttest("rejects a cart with no items", async () => {
 \t\texpect(1).toBe(1)
 \t})
-\ttest.skip('keeps the old total', async () => {})
+\ttest("applies the discount once", async () => {})
diff --git a/tests/moved_test.go b/tests/moved_test.go
deleted file mode 100644
--- a/tests/moved_test.go
+++ /dev/null
@@ -1,3 +0,0 @@
-package tests
-
-func TestUpsertAlias(t *testing.T) {
diff --git a/pkg/alias_test.go b/pkg/alias_test.go
new file mode 100644
--- /dev/null
+++ b/pkg/alias_test.go
@@ -0,0 +1,3 @@
+package pkg
+
+func TestUpsertAlias(t *testing.T) {
diff --git a/src/orders.ts b/src/orders.ts
--- a/src/orders.ts
+++ b/src/orders.ts
@@ -1,2 +1,2 @@
-test("not a test file", () => {})
+const total = 1
"""


class ListTestChangesTest(unittest.TestCase):
    def setUp(self):
        self.module = load("list_test_changes")

    def test_lists_removed_and_added_tests_with_lines(self):
        rows = self.module.test_changes(DIFF)
        self.assertIn(("removed", "tests/orders.spec.ts", 11, "rejects an empty cart"), rows)
        self.assertIn(("removed", "tests/orders.spec.ts", 14, "keeps the old total"), rows)
        self.assertIn(("added", "tests/orders.spec.ts", 11, "rejects a cart with no items"), rows)
        self.assertIn(("added", "tests/orders.spec.ts", 14, "applies the discount once"), rows)

    def test_a_test_that_moves_between_files_is_neither_added_nor_removed(self):
        names = {row[3] for row in self.module.test_changes(DIFF)}
        self.assertNotIn("TestUpsertAlias", names)

    def test_ignores_test_calls_outside_test_files(self):
        names = {row[3] for row in self.module.test_changes(DIFF)}
        self.assertNotIn("not a test file", names)

    def test_cli_prints_tab_separated_rows(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "full.diff"
            path.write_text(DIFF, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-I", str(SCRIPTS / "list_test_changes.py"), str(path)],
                capture_output=True, text=True, check=True,
            )
        self.assertIn("removed\ttests/orders.spec.ts\t11\trejects an empty cart", result.stdout)


GOOD_NOTE = """---
type: summary
project: example-service
summary: "Cart checks move to the order service."
source: "https://github.com/acme/shop/pull/42"
pr: 42
head_sha: abc123
status: active
pr_state: open
updated: 2026-01-01
tier: 3
tags:
  - example-service
  - pr-summary
---

# Move cart checks to the order service

## What changed

```diff
 export function placeOrder(cart: Cart) {
-\tvalidateCart(cart)
+\tassertCartHasItems(cart)
 }
```

## Tests

- [added] tests/orders.spec.ts:11 rejects a cart with no items
- [removed] tests/orders.spec.ts:14 keeps the old total

## My notes

"""

PR = {"additions": 30, "deletions": 10, "headRefOid": "abc123"}


class CheckNoteTest(unittest.TestCase):
    def setUp(self):
        self.module = load("check_note")

    def check(self, note: str, pr: dict = PR, tests: str | None = None):
        return self.module.check(note, pr, tests)

    def test_accepts_a_note_inside_the_budget(self):
        errors, shown, budget = self.check(GOOD_NOTE)
        self.assertEqual([], errors)
        self.assertEqual(4, shown)
        self.assertEqual(8, budget)

    def test_reports_a_note_over_the_budget(self):
        errors, _, _ = self.check(GOOD_NOTE, {**PR, "additions": 10, "deletions": 0})
        self.assertTrue(any("budget" in error for error in errors), errors)

    def test_reports_a_stale_head_sha(self):
        errors, _, _ = self.check(GOOD_NOTE, {**PR, "headRefOid": "def456"})
        self.assertTrue(any("head_sha" in error for error in errors), errors)

    def test_reports_missing_frontmatter_key_and_user_section(self):
        note = GOOD_NOTE.replace("pr: 42\n", "").replace("## My notes", "## Notes")
        errors, _, _ = self.check(note)
        self.assertIn("missing frontmatter key pr", errors)
        self.assertTrue(any("## My notes" in error for error in errors), errors)
        note = GOOD_NOTE.replace("tier: 3\n", "").replace("pr_state: open\n", "")
        errors, _, _ = self.check(note)
        self.assertIn("missing frontmatter key tier", errors)
        self.assertIn("missing frontmatter key pr_state", errors)

    def test_reports_import_lines_and_long_lines_in_diffs(self):
        long_line = "+\tconst x = " + "a" * 100 + "\n"
        note = GOOD_NOTE.replace("```diff\n", "```diff\n+import { x } from \"y\"\n" + long_line)
        errors, _, _ = self.check(note, {**PR, "additions": 300})
        self.assertTrue(any("import" in error for error in errors), errors)
        self.assertTrue(any("100 columns" in error for error in errors), errors)

    def test_reports_a_removed_test_the_note_leaves_out(self):
        tests = "removed\ttests/orders.spec.ts\t20\tcharges shipping twice\n"
        errors, _, _ = self.check(GOOD_NOTE, PR, tests)
        self.assertTrue(any("charges shipping twice" in error for error in errors), errors)

    def test_reports_secret_shaped_text(self):
        key = "AKIA" + "ABCDEFGHIJKLMNOP"
        note = GOOD_NOTE.replace("## My notes", f"token {key}\n\n## My notes")
        errors, _, _ = self.check(note)
        self.assertTrue(any("secret" in error for error in errors), errors)

    def test_cli_exits_non_zero_on_errors(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "note.md").write_text(GOOD_NOTE, encoding="utf-8")
            (folder / "pr.json").write_text(json.dumps({**PR, "headRefOid": "zzz"}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-I", str(SCRIPTS / "check_note.py"),
                 str(folder / "note.md"), str(folder / "pr.json")],
                capture_output=True, text=True,
            )
        self.assertEqual(1, result.returncode)
        self.assertIn("head_sha", result.stdout)


class SkillContractTest(unittest.TestCase):
    def test_description_is_trigger_focused(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        description = next(line for line in text.splitlines() if line.startswith("description:"))
        self.assertIn("Use when the user asks", description)
        self.assertIn("invokes /recap", description)

    def test_skill_stays_read_only_toward_github_and_git(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never edit, comment on, approve or merge the PR", text)
        for command in ("`git add`", "`git commit`", "`git push`"):
            self.assertIn(command, text)

    def test_skill_runs_its_bundled_scripts(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        for script in ("scripts/gather.sh", "scripts/check_note.py"):
            self.assertIn(script, text)
            self.assertTrue((SKILL_DIR / script).exists(), script)


if __name__ == "__main__":
    unittest.main()
