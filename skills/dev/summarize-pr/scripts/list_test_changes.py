"""List the tests a pull request adds and removes, read from its unified diff.

Usage: python3 list_test_changes.py <full.diff>

Prints one tab-separated row per test: <added|removed> <path> <line> <name>.
The line is the head-commit line for an added test and the base line for a
removed test. A name that is removed in one place and added in another (a test
that moves, also into another file) is left out: its behavior did not change.
A renamed test shows as one removed row and one added row; the summary decides
whether the new test replaces the old one.
"""

import re
import sys

TEST_FILE = re.compile(
    r"([._](test|spec)\.[cm]?[jt]sx?$)|(_test\.go$)|((^|/)test_[^/]*\.py$)|(_test\.py$)"
)
JS_MODIFIERS = r"(?:\.(?:only|skip|fixme|fail|failing|slow|todo|concurrent))*"
TEST_NAME = (
    re.compile(r"(?:^|[^\w.$])(?:it|test)" + JS_MODIFIERS + r"\(\s*([\"'`])(?P<name>.*?)\1"),
    re.compile(r"^func (?P<name>Test\w+)\("),
    re.compile(r"^\s*(?:async\s+)?def (?P<name>test_\w+)\("),
)
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)")


def test_name(line: str) -> str | None:
    for pattern in TEST_NAME:
        match = pattern.search(line)
        if match:
            return match.group("name")
    return None


def file_path(line: str) -> str | None:
    """Return the path of a '--- a/x' or '+++ b/x' header, None for /dev/null."""
    path = line[4:].strip()
    if path == "/dev/null":
        return None
    return path[2:] if path[:2] in ("a/", "b/") else path


def test_changes(diff: str) -> list[tuple[str, str, int, str]]:
    removed: list[tuple[str, str, int, str]] = []
    added: list[tuple[str, str, int, str]] = []
    old_path = new_path = None
    old_line = new_line = 0
    in_hunk = False

    for line in diff.splitlines():
        if line.startswith("diff --git "):
            old_path = new_path = None
            in_hunk = False
            continue
        if not in_hunk and line.startswith("--- "):
            old_path = file_path(line)
            continue
        if not in_hunk and line.startswith("+++ "):
            new_path = file_path(line)
            continue
        hunk = HUNK.match(line)
        if hunk:
            in_hunk = True
            old_line, new_line = int(hunk.group(1)), int(hunk.group(2))
            continue
        if not in_hunk:
            continue

        marker, code = line[:1], line[1:]
        if marker == "-":
            name = test_name(code)
            if name and old_path and TEST_FILE.search(old_path):
                removed.append(("removed", old_path, old_line, name))
            old_line += 1
        elif marker == "+":
            name = test_name(code)
            if name and new_path and TEST_FILE.search(new_path):
                added.append(("added", new_path, new_line, name))
            new_line += 1
        elif marker == " ":
            old_line += 1
            new_line += 1

    removed_names = {row[3] for row in removed}
    added_names = {row[3] for row in added}
    moved = removed_names & added_names
    rows = [row for row in removed + added if row[3] not in moved]
    return list(dict.fromkeys(rows))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 list_test_changes.py <full.diff>", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as handle:
        rows = test_changes(handle.read())
    for status, path, line, name in rows:
        print(f"{status}\t{path}\t{line}\t{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
