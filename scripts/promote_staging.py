#!/usr/bin/env python3
"""promote_staging.py — Validate and promote a staging file to docs/.

Two modes:
  (default)     Validate + physically move file to docs/ (ai_status must be 'validated')
  --to-review   Update ai_status from 'draft' to 'in-review' in-place + print PR instructions
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

MANDATORY_FIELDS = [
    "id", "type", "title", "date_range", "geography", "category",
    "tags", "related", "summary", "ai_status", "source_verified",
]

TYPE_TO_FOLDER = {
    "person": "people",
    "brand": "brands",
    "model": "models",
    "material": "materials",
    "frame": "frames",
    "club": "clubs",
    "pilot": "pilots",
    "team": "teams",
    "timeline": "timeline",
    "festival": "festivals",
    "release": "releases",
}


def read_frontmatter(staging_path: Path) -> tuple[str, dict]:
    """Return (raw_content, parsed_fm). Exits on parse error."""
    content = staging_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        print("ERROR: No frontmatter found in file.")
        sys.exit(1)
    return content, yaml.safe_load(match.group(1))


def cmd_to_review(staging_path: Path) -> int:
    """Transition ai_status: draft → in-review. Validates mandatory fields first."""
    content, fm = read_frontmatter(staging_path)

    # 1. Check mandatory fields
    missing = [f for f in MANDATORY_FIELDS if f not in fm or fm[f] is None]
    # tags and related: must be a list (empty list is OK for related, but tags must be non-empty)
    errors = []
    for field in missing:
        errors.append(f"  - Missing or null mandatory field: '{field}'")
    if isinstance(fm.get("tags"), list) and len(fm["tags"]) == 0:
        errors.append("  - 'tags' must contain at least one value")
    # Ensure at least one source listed (we check the body for a ## Sources section)
    if "## Sources" not in content or content.split("## Sources", 1)[1].strip().startswith("- TODO"):
        errors.append("  - At least one source must be listed under '## Sources' before submitting for review")

    if errors:
        print("ERROR: Cannot submit for review — mandatory checks failed:")
        for e in errors:
            print(e)
        return 1

    if fm.get("ai_status") == "in-review":
        print(f"INFO: {staging_path} is already 'in-review'. No change made.")
        return 0

    if fm.get("ai_status") != "draft":
        print(f"ERROR: ai_status must be 'draft' to transition to 'in-review' (current: '{fm.get('ai_status')}').")
        return 1

    # 2. Rewrite ai_status in file
    new_content = content.replace('ai_status: "draft"', 'ai_status: "in-review"', 1)
    if new_content == content:
        # Try without quotes (YAML may have stored it unquoted)
        new_content = re.sub(r'(ai_status:\s*)draft\b', r'\1in-review', content, count=1)

    staging_path.write_text(new_content, encoding="utf-8")

    entity_type = fm.get("type", "entity")
    slug = staging_path.stem
    folder = TYPE_TO_FOLDER.get(entity_type, f"{entity_type}s")

    print(f"v ai_status updated: draft -> in-review in {staging_path}")
    print()
    print("Next steps to open a review PR:")
    print(f"  1. git add {staging_path}")
    print(f'  2. git commit -m "review: submit {entity_type} {slug} for review"')
    print("  3. git push origin <your-branch>")
    print(f"  4. Open a PR — target branch: main")
    print(f"     The PR should move/rename the file to: docs/{folder}/{slug}.md")
    print("     Use the PR template checklist (.github/PULL_REQUEST_TEMPLATE.md)")
    return 0


def cmd_promote(staging_path: Path) -> int:
    """Validate all promotion criteria, then physically move file to docs/."""
    content, fm = read_frontmatter(staging_path)
    errors = []

    if fm.get("ai_status") != "validated":
        errors.append(f"  - ai_status must be 'validated' (current: '{fm.get('ai_status')}')")
    if not fm.get("reviewer"):
        errors.append("  - reviewer must not be null or empty")
    if fm.get("source_verified") is not True:
        errors.append(f"  - source_verified must be true (current: {fm.get('source_verified')})")

    if errors:
        print("ERROR: Validation failed. File NOT promoted.\nIssues found:")
        for e in errors:
            print(e)
        return 1

    entity_type = fm.get("type")
    slug = staging_path.stem
    folder = TYPE_TO_FOLDER.get(entity_type)
    if not folder:
        print(f"ERROR: Unknown entity type '{entity_type}'.")
        return 1

    root = Path(__file__).parent.parent
    dest_path = root / "docs" / folder / f"{slug}.md"
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staging_path), str(dest_path))

    print(f"v Promoted: {staging_path} -> {dest_path}")
    print()
    print("Next steps to publish:")
    print(f"  1. Review the file at: {dest_path}")
    print("  2. git add .")
    print(f'  3. git commit -m "feat: add {entity_type} {slug}"')
    print("  4. git push origin <your-branch>")
    print("  5. Open a Pull Request targeting main")
    print("  6. CI gate will run — merge only when all checks pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote a staging file to docs/.")
    parser.add_argument("staging_file", help="Path to the staging .md file.")
    parser.add_argument(
        "--to-review",
        action="store_true",
        help="Transition ai_status from 'draft' to 'in-review' (does not move the file).",
    )
    args = parser.parse_args()

    staging_path = Path(args.staging_file)
    if not staging_path.exists():
        print(f"ERROR: File not found: {staging_path}")
        return 1

    if args.to_review:
        return cmd_to_review(staging_path)
    return cmd_promote(staging_path)


if __name__ == "__main__":
    sys.exit(main())



if __name__ == "__main__":
    sys.exit(main())
