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

    def test_accepts_valid_skill_and_local_reference_heading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "example",
                "---\nname: example\ndescription: Use when reviewing examples.\n---\n"
                "Read [the exact rules](REFERENCE.md#exact-rules) when needed.\n",
            )
            (root / "skills/testing/example/REFERENCE.md").write_text(
                "# Reference\n\n## Exact Rules\n", encoding="utf-8"
            )
            self.assertEqual([], validate_repository(root))

    def test_reports_missing_local_link_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "example",
                "---\nname: example\ndescription: Use when reviewing examples.\n---\n"
                "Read [the reference](MISSING.md#exact-rules).\n",
            )

            errors = "\n".join(validate_repository(root))

            self.assertIn("missing local link MISSING.md#exact-rules", errors)

    def test_reports_missing_local_heading_fragment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "example",
                "---\nname: example\ndescription: Use when reviewing examples.\n---\n"
                "Read [the reference](REFERENCE.md#missing-rules).\n",
            )
            (root / "skills/testing/example/REFERENCE.md").write_text(
                "# Reference\n\n## Exact Rules\n", encoding="utf-8"
            )

            errors = "\n".join(validate_repository(root))

            self.assertIn("missing local heading REFERENCE.md#missing-rules", errors)

    def test_reports_name_link_frontmatter_and_scaffold_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "wrongfolder",
                "---\nname: other-name\ndescription: Use when testing.\n---\n"
                "Read [missing](REFERENCE.md).\n" + "TO" + "DO: replace scaffold.\n",
            )
            errors = "\n".join(validate_repository(root))
            self.assertIn("folder/name mismatch", errors)
            self.assertIn("missing local link", errors)
            self.assertIn("unfinished scaffold", errors)

    def test_rejects_missing_frontmatter_closing_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "example",
                "---\nname: example\ndescription: Use when reviewing examples.\n"
                "Body without a closing boundary.\n",
            )
            errors = "\n".join(validate_repository(root))
            self.assertIn("missing closing frontmatter boundary", errors)

    def test_reports_invoked_skill_missing_from_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                "example",
                "---\nname: example\ndescription: Use when reviewing examples.\n---\n"
                "Invoke `missing-skill`, then apply the `example` skill.\n",
            )

            errors = "\n".join(validate_repository(root))

            self.assertIn("unknown skill reference 'missing-skill'", errors)
            self.assertNotIn("'example'", errors)

    def test_reports_multiword_and_reserved_skill_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("two-words", "bug"):
                self.write_skill(
                    root,
                    folder,
                    f"---\nname: {folder}\ndescription: Use when testing names.\n---\n",
                )

            errors = "\n".join(validate_repository(root))

            self.assertIn("skill name 'two-words' is not one lowercase word", errors)
            self.assertIn("skill name 'bug' is a runtime command or bundled skill", errors)

    def test_current_repository_has_ten_discoverable_skills(self):
        skill_files = sorted(ROOT.glob("skills/*/*/SKILL.md"))
        self.assertEqual(10, len(skill_files))


if __name__ == "__main__":
    unittest.main()
