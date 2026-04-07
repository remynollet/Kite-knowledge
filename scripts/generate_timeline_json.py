#!/usr/bin/env python3
"""generate_timeline_json.py — Generate TimelineJS JSON from entity frontmatter."""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

# Reuse frontmatter regex from validate_frontmatter.py
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def extract_frontmatter(content: str) -> dict | None:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def parse_year(date_str: str | int | None) -> int | None:
    if date_str is None:
        return None
    if isinstance(date_str, int):
        return date_str
    # Extract the first 4-digit number (year)
    match = re.search(r"(\d{4})", str(date_str))
    if match:
        return int(match.group(1))
    return None


def generate_event(filepath: Path, fm: dict, base_url: str) -> dict | None:
    """Transform frontmatter into a TimelineJS event object."""
    title = fm.get("title")
    summary = fm.get("summary", "")
    date_val = fm.get("date_range") or fm.get("date")
    image = fm.get("image")
    
    year = parse_year(date_val)
    if year is None:
        return None

    # Construct the relative URL for the "Read more" link
    # Assuming the site root is the project root, and docs/ is the source
    # We want the path relative to docs/ without the .md extension
    rel_path = filepath.relative_to(filepath.parents[len(filepath.parts) - filepath.parts.index("docs") - 1])
    # strip 'docs/' prefix and '.md' suffix
    web_path = str(rel_path.with_suffix('')).replace("\\", "/")
    # If the file is index.md, we want the directory path
    if web_path.endswith("/index"):
        web_path = web_path[:-5]
    elif web_path == "index":
        web_path = ""
        
    full_url = f"{base_url.rstrip('/')}/{web_path}"

    event = {
        "start_date": {
            "year": str(year)
        },
        "text": {
            "headline": title,
            "text": f"<p>{summary}</p><p><a href='{full_url}'>Read more</a></p>"
        }
    }

    if image and image != "TODO: URL d'une image":
        event["media"] = {
            "url": image
        }

    return event


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate TimelineJS JSON from entity frontmatter."
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to the documentation directory (default: docs)",
    )
    parser.add_argument(
        "--output",
        default="docs/assets/data/timeline.json",
        help="Path to the output JSON file (default: docs/assets/data/timeline.json)",
    )
    parser.add_argument(
        "--base-url",
        default="https://remynollet.github.io/Kite-knowledge",
        help="Base URL for the site (default: project site_url)",
    )
    args = parser.parse_args()

    docs_path = Path(args.docs_dir)
    output_path = Path(args.output)

    if not docs_path.exists():
        print(f"ERROR: Docs directory not found: {docs_path}")
        return 1

    events = []
    
    # Recursively find all .md files
    for filepath in sorted(docs_path.rglob("*.md")):
        # Skip hidden files and temporary files
        if filepath.name.startswith(".") or "staging" in filepath.parts:
            continue
            
        content = filepath.read_text(encoding="utf-8")
        fm = extract_frontmatter(content)
        
        if fm is None:
            continue
            
        # Filter: ai_status must be validated (unless we are in dev/test?)
        # For Phase 2, we only want validated content in the public timeline
        if fm.get("ai_status") != "validated":
            continue
            
        event = generate_event(filepath, fm, args.base_url)
        if event:
            events.append(event)
        else:
            # Optionally log missing dates for timeline-eligible types
            if fm.get("type") in ["timeline", "model", "person"]:
                print(f"Warning: Skipping {filepath} - No valid date found in frontmatter.")

    timeline_json = {
        "title": {
            "text": {
                "headline": "Kite History: 1850 - Present",
                "text": "<p>A visual journey through the evolution of kite technology and culture.</p>"
            }
        },
        "events": events
    }

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(timeline_json, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {len(events)} events in {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
