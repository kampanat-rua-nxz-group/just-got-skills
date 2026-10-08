#!/usr/bin/env python3
"""md2xmind - Convert a use-case Markdown outline to an XMind file (2020+ JSON format).

Stdlib only. Produces content.json + metadata.json — native XMind 2020+ / 26.x
format with full note support.

Outline conventions:
    # Title            root topic (first heading only)
    ## / ### Heading   branch topics (heading depth = tree depth)
    - Topic text       topic; nesting via 2-space indentation
    > note text        attaches a plain note to the preceding topic
    **text**           emphasis in Markdown only (plain XMind title)
    [!]                legacy exclamation marker
    [P1]..[P3]         priority marker token in a title (stripped)
    @label             label token in a title (stripped)

Usage:
    python3 md2xmind.py outline.md -o output.xmind
"""

import argparse
import json
import re
import sys
import uuid
import zipfile

MARKER_RE = re.compile(r"\[P([1-9])\]")
LABEL_RE = re.compile(r"@([\w-]+)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_RE = re.compile(r"^(\s*)-\s+(.*)$")
NOTE_RE = re.compile(r"^\s*>\s?(.*)$")
SPACE_RE = re.compile(r"\s{2,}")
BREAK_RE = re.compile(r"\s*<br>\s*")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


class Topic:
    __slots__ = ("title", "note_lines", "markers", "labels", "children")

    def __init__(self, title):
        self.title = title
        self.note_lines = []
        self.markers = []
        self.labels = []
        self.children = []

    @classmethod
    def from_text(cls, text):
        """Build a Topic from raw title text, extracting [Pn] and @label tokens."""
        markers = []
        if "[P" in text:
            markers = [f"priority-{m}" for m in MARKER_RE.findall(text)]
            text = MARKER_RE.sub("", text)
        if "[!]" in text:
            markers.append("symbol-exclam")
            text = text.replace("[!]", "")
        labels = []
        if "@" in text:
            labels = LABEL_RE.findall(text)
            text = LABEL_RE.sub("", text)
        text = BOLD_RE.sub(r"\1", text)
        title = SPACE_RE.sub(" ", text).strip()
        # <br> token → real newline (multi-line topic titles)
        if "<br>" in title:
            title = BREAK_RE.sub("\n", title)
        if not title:
            raise ValueError(f"Topic with empty title after token stripping: {text!r}")
        topic = cls(title)
        topic.markers = markers
        topic.labels = labels
        return topic


def parse_outline(text):
    """Parse Markdown outline into a root Topic. Raises ValueError on bad input."""
    root = None
    # Stack of (depth, topic); headings use depth 0..5, bullets nest below them.
    stack = []
    last_topic = None
    in_frontmatter = False
    # Bullets anchor to the most recent heading, not to the previous bullet —
    # otherwise same-indent siblings chain as children.
    bullet_base = 1

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if lineno == 1 and line == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue
        if not line.strip():
            continue

        note = NOTE_RE.match(line)
        if note:
            if last_topic is None:
                raise ValueError(f"Line {lineno}: note with no preceding topic")
            last_topic.note_lines.append(note.group(1))
            continue

        heading = HEADING_RE.match(line)
        if heading:
            depth = len(heading.group(1)) - 1
            topic = Topic.from_text(heading.group(2))
            if depth == 0:
                if root is not None:
                    raise ValueError(f"Line {lineno}: multiple '#' root headings")
                root = topic
                stack = [(0, root)]
            else:
                if root is None:
                    raise ValueError(f"Line {lineno}: heading before '#' root")
                while stack and stack[-1][0] >= depth:
                    stack.pop()
                if not stack:
                    raise ValueError(f"Line {lineno}: heading depth skips levels")
                stack[-1][1].children.append(topic)
                stack.append((depth, topic))
            bullet_base = depth + 1
            last_topic = topic
            continue

        bullet = BULLET_RE.match(line)
        if bullet:
            if root is None:
                raise ValueError(f"Line {lineno}: bullet before '#' root heading")
            indent = len(bullet.group(1).replace("\t", "  "))
            depth = bullet_base + indent // 2
            topic = Topic.from_text(bullet.group(2))
            # Re-anchor: pop bullet levels deeper than this one.
            while stack and stack[-1][0] >= depth:
                stack.pop()
            if not stack:
                raise ValueError(f"Line {lineno}: bullet indentation out of range")
            stack[-1][1].children.append(topic)
            stack.append((depth, topic))
            last_topic = topic
            continue

        raise ValueError(f"Line {lineno}: unrecognized outline line: {line!r}")

    if root is None:
        raise ValueError("Outline has no '#' root heading")
    return root


def new_id():
    return str(uuid.uuid4())


def topic_to_dict(topic):
    d = {
        "id": new_id(),
        "class": "topic",
        "title": topic.title,
    }
    if topic.note_lines:
        d["notes"] = {"plain": {"content": "\n".join(topic.note_lines)}}
    if topic.markers:
        d["markers"] = [{"markerId": m} for m in topic.markers]
    if topic.labels:
        d["labels"] = topic.labels
    if topic.children:
        d["children"] = {"attached": [topic_to_dict(c) for c in topic.children]}
    return d


def build_content_json(root):
    root_dict = topic_to_dict(root)
    root_dict["structureClass"] = "org.xmind.ui.logic.right"
    sheet = {
        "id": new_id(),
        "revisionId": new_id(),
        "class": "sheet",
        "title": "Sheet 1",
        "topicOverlapping": "overlap",
        "extensions": [
            {
                "provider": "org.xmind.ui.skeleton.structure.style",
                "content": {"centralTopic": "org.xmind.ui.logic.right"},
            }
        ],
        "rootTopic": root_dict,
    }
    return json.dumps([sheet], ensure_ascii=False, separators=(",", ":"))


METADATA_JSON = json.dumps({
    "dataStructureVersion": "2",
    "creator": {
        "name": "md2xmind",
        "version": "2.0.0",
        "platform": "python",
    },
    "layoutEngineVersion": "3",
})

MANIFEST_JSON = json.dumps({
    "file-entries": {
        "content.json": {},
        "metadata.json": {},
    }
})


def write_xmind(content_json, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", content_json)
        zf.writestr("metadata.json", METADATA_JSON)
        zf.writestr("manifest.json", MANIFEST_JSON)


def main():
    description = (__doc__ or "Convert a Markdown outline to an XMind file.").splitlines()[0]
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("outline", help="Markdown outline file")
    parser.add_argument("-o", "--output", required=True, help="Output .xmind path")
    args = parser.parse_args()

    try:
        with open(args.outline, encoding="utf-8") as fh:
            root = parse_outline(fh.read())
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    content = build_content_json(root)
    try:
        write_xmind(content, args.output)
    except OSError as exc:
        print(f"Error writing {args.output}: {exc}", file=sys.stderr)
        sys.exit(1)

    def count(t):
        return 1 + sum(count(c) for c in t.children)

    print(f"Created: {args.output} ({count(root)} topics)")


if __name__ == "__main__":
    main()
