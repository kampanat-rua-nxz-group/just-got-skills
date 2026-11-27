#!/usr/bin/env python3
"""List the TBD, TBC, and @TBD lines in Markdown outlines with their branch path.

Usage:
    python3 list_tbd.py outline.md [more.md ...]

Prints one line per open case:
    outline.md:42: Root > Validation Cases > POST /x > limit > Sample input: ... > TBD
Exits 0 when it finds open cases, 1 when it finds none, 2 on a read error.
"""

import re
import sys

OPEN_RE = re.compile(r"\bTB[DC]\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_RE = re.compile(r"^(\s*)-\s+(.*)$")


def open_cases(text):
    """Yield (line number, path) for each line that marks an open case."""
    # Stack of (depth, title). Headings use depth 0..5, bullets nest below them.
    stack = []
    bullet_base = 1
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        heading = HEADING_RE.match(line)
        bullet = BULLET_RE.match(line)
        if heading:
            depth = len(heading.group(1)) - 1
            title = heading.group(2).strip()
            bullet_base = depth + 1
        elif bullet:
            depth = bullet_base + len(bullet.group(1).replace("\t", "  ")) // 2
            title = bullet.group(2).strip()
        else:
            continue
        while stack and stack[-1][0] >= depth:
            stack.pop()
        stack.append((depth, title))
        # Coverage Gaps only repeats open cases listed elsewhere in the outline.
        in_gaps = len(stack) > 1 and stack[1][1].startswith("Coverage Gaps")
        if OPEN_RE.search(title) and not in_gaps:
            yield lineno, " > ".join(t for _, t in stack)


def main(paths):
    if not paths:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    found = 0
    for path in paths:
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except OSError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        for lineno, case_path in open_cases(text):
            print(f"{path}:{lineno}: {case_path}")
            found += 1
    if not found:
        print("No TBD or TBC cases found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
