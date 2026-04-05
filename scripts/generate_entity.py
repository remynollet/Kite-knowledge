#!/usr/bin/env python3
"""generate_entity.py — Generate a frontmatter-complete AI draft template."""

import argparse
import re
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).parent / "schemas"

TYPE_TO_FOLDER = {
    "person": "people",
    "brand": "brands",
    "model": "models",
    "material": "materials",
    "frame": "frames",
    "club": "clubs",
    "pilot": "pilots",
    "timeline": "timeline",
    "release": "releases",
}

TEMPLATE = """\
---
id: "{slug}"
type: "{type}"
title: "TODO: Full name or title"
date_range: "TODO: e.g., 1959-present"
geography: "TODO: Country or region"
category: "TODO: Role or class (see schema)"
tags:
  - "{type}"
  - "TODO: add more tags"
related: []
summary: "TODO: One-sentence description."
ai_status: "draft"
source_verified: false
reviewer: null
review_date: null
---

# TODO: Full name or title

## Summary

TODO: Expand the one-sentence summary into 2-3 paragraphs.

## Key Facts

| Field | Value |
|---|---|
| Date range | TODO |
| Geography | TODO |
| Category | TODO |

## Historical Context

TODO: Historical narrative, technical details, or chronological context.

## Sources

- TODO: Add primary source references here.
"""


def is_valid_slug(slug: str) -> bool:
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an AI draft entity template.")
    parser.add_argument("--type", required=True, dest="entity_type", help="Entity type (e.g., person, brand, model)")
    parser.add_argument("--slug", required=True, help="Kebab-case slug (e.g., peter-lynn)")
    args = parser.parse_args()

    entity_type = args.entity_type
    slug = args.slug

    if entity_type not in TYPE_TO_FOLDER:
        print(f"ERROR: Unknown entity type '{entity_type}'. Valid types: {list(TYPE_TO_FOLDER)}")
        return 1

    if not is_valid_slug(slug):
        print(f"ERROR: Invalid slug '{slug}'. Must be kebab-case (lowercase letters, digits, hyphens only).")
        return 1

    folder = TYPE_TO_FOLDER[entity_type]
    root = Path(__file__).parent.parent
    output_path = root / "staging" / folder / f"{slug}.md"

    if output_path.exists():
        print(f"ERROR: File already exists: {output_path}. Not overwriting.")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = TEMPLATE.format(slug=slug, type=entity_type)
    output_path.write_text(content, encoding="utf-8")
    print(f"Created: {output_path}")
    print(f"Next: edit {output_path} and fill in all TODO fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
