#!/usr/bin/env python3
"""check_links.py — Check for broken internal Markdown links."""

import argparse
import re
import sys
from pathlib import Path

import yaml

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)#][^)]*)\)")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _extract_frontmatter(content: str) -> dict:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}



def check_links(directory: Path, root: Path) -> list[tuple]:
    """Return list of (file, line_num, broken_path) tuples."""
    broken = []
    for md_file in sorted(directory.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for match in LINK_RE.finditer(line):
                target = match.group(2)
                # Skip external links and anchor-only links
                if target.startswith(("http://", "https://", "#")):
                    continue
                # Strip any fragment from path
                target_path = target.split("#")[0]
                if not target_path:
                    continue
                # Resolve relative to the md file's directory
                resolved = (md_file.parent / target_path).resolve()
                if not resolved.exists():
                    broken.append((md_file, line_num, target))
        # Check related: frontmatter links
        # related: paths are relative to docs/ root (schema convention),
        # but also try resolving relative to the file's directory for backward compat.
        fm = _extract_frontmatter(content)
        for related_path in fm.get("related", []) or []:
            if not isinstance(related_path, str):
                continue
            # Try docs-root-relative first (canonical convention per schema)
            docs_root = root / "docs"
            resolved_from_root = (docs_root / related_path).resolve()
            resolved_from_file = (md_file.parent / related_path).resolve()
            if not resolved_from_root.exists() and not resolved_from_file.exists():
                broken.append((md_file, "frontmatter:related", related_path))
    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for broken internal Markdown links.")
    parser.add_argument("directory", help="Directory to scan for .md files.")
    args = parser.parse_args()

    root = Path(__file__).parent.parent  # project root
    directory = Path(args.directory)

    if not directory.exists():
        print(f"ERROR: Directory not found: {directory}")
        return 1

    broken = check_links(directory, root)

    if broken:
        for f, line_num, path in broken:
            print(f"{f}:{line_num}: broken link → {path}")
        print(f"\nTotal broken links: {len(broken)}")
        return 1

    print(f"OK: No broken internal links found in {directory}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
