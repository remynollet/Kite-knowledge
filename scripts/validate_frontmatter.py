#!/usr/bin/env python3
"""validate_frontmatter.py — Validate entity frontmatter against schemas."""

import argparse
import re
import sys
from pathlib import Path

import yaml


SCHEMA_DIR = Path(__file__).parent / "schemas"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def load_schema(entity_type: str) -> dict | None:
    schema_path = SCHEMA_DIR / f"{entity_type}.yaml"
    if not schema_path.exists():
        return None
    with schema_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_frontmatter(content: str) -> dict | None:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None
    return yaml.safe_load(match.group(1))


def validate_file(filepath: Path) -> list[str]:
    """Return list of error strings. Empty list = valid.
    Returns None if the file has no frontmatter (navigation/index page — skipped).
    """
    errors = []
    content = filepath.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)

    if fm is None:
        # No frontmatter — navigation/index page, not an entity file. Skip.
        return []

    # If frontmatter exists but has no type field, skip (not an entity file)
    entity_type = fm.get("type")
    if not entity_type:
        return []

    # schema
    schema = load_schema(entity_type)
    if schema is None:
        return [f"{filepath}: Unknown entity type: '{entity_type}' (no schema found)"]

    required_fields = schema.get("fields", {})

    # field validation
    for field_name, field_def in required_fields.items():
        is_required = field_def.get("required", False)
        expected_type = field_def.get("type")
        allowed = field_def.get("allowed_values")

        if field_name not in fm:
            if is_required:
                errors.append(f"{filepath}: Missing required field: {field_name}")
            continue

        value = fm[field_name]

        if value is None and is_required:
            # null is allowed at schema level for optional text;
            # extended checks (docs/ restriction) handled below
            pass
        elif value is not None:
            # type check
            type_map = {"string": str, "bool": bool, "list": list}
            expected_py = type_map.get(expected_type)
            if expected_py and not isinstance(value, expected_py):
                errors.append(
                    f"{filepath}: Invalid type for field '{field_name}': "
                    f"expected {expected_type}, got {type(value).__name__}"
                )
            # allowed values check
            if allowed and value not in allowed:
                errors.append(
                    f"{filepath}: Invalid value for '{field_name}': "
                    f"'{value}' not in {allowed}"
                )

    # id must match filename slug
    slug = filepath.stem
    if fm.get("id") != slug:
        errors.append(
            f"{filepath}: id mismatch: frontmatter id='{fm.get('id')}' "
            f"but filename slug='{slug}'"
        )

    # extended checks for files inside docs/ directory
    resolved = filepath.resolve()
    if "docs" in resolved.parts:
        if not fm.get("reviewer"):
            errors.append(f"{filepath}: reviewer must not be null in docs/")
        if not fm.get("review_date"):
            errors.append(f"{filepath}: review_date must not be null in docs/")

    # source_verified must be bool (not null, not string)
    sv = fm.get("source_verified")
    if sv is not None and not isinstance(sv, bool):
        errors.append(
            f"{filepath}: source_verified must be a boolean (true/false), got {type(sv).__name__}"
        )

    # tags must contain at least one value matching the entity type (Story 5.5)
    tags = fm.get("tags")
    if isinstance(tags, list):
        if entity_type not in tags:
            errors.append(
                f"{filepath}: tags must contain at least one value matching the entity type "
                f"(expected '{entity_type}' in tags, got {tags})"
            )

    return errors


def collect_md_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".md" else []
    return list(path.rglob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate entity frontmatter against schemas."
    )
    parser.add_argument(
        "path",
        help="Path to a single .md file or a directory to validate recursively.",
    )
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"ERROR: Path not found: {target}")
        return 1

    files = collect_md_files(target)
    if not files:
        print(f"No .md files found in: {target}")
        return 0

    all_errors: list[str] = []
    for filepath in sorted(files):
        errors = validate_file(filepath)
        all_errors.extend(errors)

    if all_errors:
        for err in all_errors:
            print(err)
        return 1

    print(f"{len(files)} file(s) validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
