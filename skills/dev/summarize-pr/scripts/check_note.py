"""Check a summarize-pr vault note against the rules a script can check.

Usage: python3 check_note.py <note.md> <pr.json> [<test-changes.tsv>]

<pr.json> and <test-changes.tsv> are the files gather.sh writes. Prints one
"error:" line per broken rule, then the shown-line count and the budget. Exits
1 when any rule is broken.
"""

import json
import math
import re
import sys

BUDGET_SHARE = 0.20
MAX_COLUMNS = 100
REQUIRED_KEYS = (
    "type", "project", "summary", "source", "pr", "head_sha", "pr_state", "status", "updated", "tier", "tags",
)
USER_SECTION = "## My notes"
TEST_ITEM = re.compile(r"^\s*- \[(added|modified|removed)\]")
IMPORT_LINE = re.compile(r"^\s*(import\s|export\s.*\sfrom\s)")
SECRET_SHAPES = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s:@/]+:[^\s@/]+@"),
)


def split_frontmatter(note: str) -> tuple[dict[str, str], str]:
    lines = note.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}, note
    end = lines.index("---", 1)
    keys = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if match:
            keys[match.group(1)] = match.group(2).strip().strip('"')
    return keys, "\n".join(lines[end + 1:])


def code_blocks(body: str) -> list[tuple[str, list[str]]]:
    """Return (language, lines) for each fenced block."""
    blocks, language, lines = [], None, []
    for line in body.splitlines():
        fence = re.match(r"^\s*(`{3,}|~{3,})\s*(\S*)", line)
        if fence and language is None:
            language, lines = fence.group(2) or "text", []
        elif fence and language is not None:
            blocks.append((language, lines))
            language = None
        elif language is not None:
            lines.append(line)
    return blocks


def section(body: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return match.group(1) if match else ""


def columns(line: str) -> int:
    return len(line.replace("\t", "  "))


def check(note: str, pr: dict, test_changes: str | None = None) -> tuple[list[str], int, int]:
    errors: list[str] = []
    keys, body = split_frontmatter(note)

    for key in REQUIRED_KEYS:
        if key not in keys:
            errors.append(f"missing frontmatter key {key}")
    if keys.get("head_sha") and keys["head_sha"] != pr.get("headRefOid"):
        errors.append(f"head_sha {keys['head_sha']} is not the PR head {pr.get('headRefOid')}; gather again")
    if not re.search(rf"^{re.escape(USER_SECTION)}\s*$", body, re.M):
        errors.append(f"missing the user-owned {USER_SECTION!r} section")
    if "{{" in note:
        errors.append("a {{...}} placeholder is left in the note")

    shown = 0
    for language, lines in code_blocks(body):
        for line in lines:
            is_diff_row = language == "diff" and line[:1] in "+- " and line[:1] != ""
            code = line[1:] if is_diff_row else line
            if columns(code) > MAX_COLUMNS:
                errors.append(f"code line over {MAX_COLUMNS} columns: {code.strip()[:60]}...")
            if language != "diff":
                continue
            if IMPORT_LINE.match(code):
                errors.append(f"import line in a diff: {code.strip()}")
            if line[:1] in "+-" and not line.startswith(("+++", "---")) and code.strip():
                shown += 1

    shown += sum(1 for line in section(body, "## Tests").splitlines() if TEST_ITEM.match(line))
    budget = math.floor((pr.get("additions", 0) + pr.get("deletions", 0)) * BUDGET_SHARE)
    if shown > budget:
        errors.append(f"shown lines {shown} are over the budget {budget} (20% of the PR's changed lines)")

    for row in (test_changes or "").splitlines():
        parts = row.split("\t")
        if len(parts) == 4 and parts[0] == "removed":
            _, path, line, name = parts
            if f"{path}:{line}" not in body:
                errors.append(f"removed test {path}:{line} ({name}) is not in the note")

    for pattern in SECRET_SHAPES:
        if pattern.search(note):
            errors.append(f"secret-shaped text matches {pattern.pattern}; replace it with a placeholder")

    return errors, shown, budget


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print("Usage: python3 check_note.py <note.md> <pr.json> [<test-changes.tsv>]", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as handle:
        note = handle.read()
    with open(sys.argv[2], encoding="utf-8") as handle:
        pr = json.load(handle)
    test_changes = None
    if len(sys.argv) == 4:
        with open(sys.argv[3], encoding="utf-8") as handle:
            test_changes = handle.read()

    errors, shown, budget = check(note, pr, test_changes)
    for error in errors:
        print(f"error: {error}")
    print(f"shown {shown} / budget {budget}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
