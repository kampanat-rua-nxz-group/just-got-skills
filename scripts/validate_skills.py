#!/usr/bin/env python3
"""Validate every skill package in this repository."""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
UNFINISHED_MARKERS = ("TO" + "DO", "implement " + "later", "fill in " + "details")


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Return the simple scalar/folded fields used by this repository."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter boundary")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter boundary") from exc

    fields: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        if not line or line.startswith((" ", "\t")) or ":" not in line:
            index += 1
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"\'')
        if value in {">", "|"}:
            folded: list[str] = []
            index += 1
            while index < end and (
                not lines[index] or lines[index].startswith((" ", "\t"))
            ):
                folded.append(lines[index].strip())
                index += 1
            fields[key] = " ".join(part for part in folded if part)
            continue
        fields[key] = value
        index += 1
    return fields


def local_markdown_links(path: Path) -> list[tuple[str, str, str]]:
    """Return local link paths, heading fragments, and their source targets."""
    links: list[tuple[str, str, str]] = []
    for source_target in LINK_RE.findall(path.read_text(encoding="utf-8")):
        source_target = source_target.strip().strip("<>")
        if "://" in source_target or source_target.startswith("mailto:"):
            continue
        target, separator, fragment = source_target.partition("#")
        if target or separator:
            links.append((target, unquote(fragment), source_target))
    return links


def markdown_heading_anchors(path: Path) -> set[str]:
    """Return GitHub-style anchors for ATX headings outside fenced code blocks."""
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    in_fence = False

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading = HEADING_RE.match(line)
        if not heading:
            continue
        slug = re.sub(r"[^\w\s-]", "", heading.group(1).lower())
        slug = re.sub(r"\s", "-", slug).strip("-")
        if not slug:
            continue
        occurrence = seen.get(slug, 0)
        seen[slug] = occurrence + 1
        anchors.add(slug if occurrence == 0 else f"{slug}-{occurrence}")

    return anchors


def validate_skill(skill_file: Path) -> list[str]:
    """Check frontmatter, folder/name agreement, links, and scaffold markers."""
    errors: list[str] = []
    relative = skill_file.as_posix()
    try:
        fields = parse_frontmatter(skill_file)
    except ValueError as exc:
        return [f"{relative}: {exc}"]

    name = fields.get("name", "")
    description = fields.get("description", "")
    if name != skill_file.parent.name:
        errors.append(
            f"{relative}: folder/name mismatch "
            f"({skill_file.parent.name!r} != {name!r})"
        )
    if not description:
        errors.append(f"{relative}: missing description")

    for target, fragment, source_target in local_markdown_links(skill_file):
        target_file = skill_file if not target else skill_file.parent / target
        if not target_file.exists():
            errors.append(f"{relative}: missing local link {source_target}")
        elif fragment and fragment.lower() not in markdown_heading_anchors(target_file):
            errors.append(f"{relative}: missing local heading {source_target}")

    text = skill_file.read_text(encoding="utf-8")
    for marker in UNFINISHED_MARKERS:
        if marker in text:
            errors.append(f"{relative}: unfinished scaffold marker {marker!r}")
    return errors


def validate_repository(root: Path) -> list[str]:
    """Return sorted validation errors for every skills/*/*/SKILL.md."""
    errors: list[str] = []
    for skill_file in sorted(root.glob("skills/*/*/SKILL.md")):
        errors.extend(validate_skill(skill_file))
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate_repository(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    count = len(list(root.glob("skills/*/*/SKILL.md")))
    print(f"Validated {count} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
