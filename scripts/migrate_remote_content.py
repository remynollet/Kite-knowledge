import os
import re
import requests
import yaml
from pathlib import Path

# Configuration
REMOTE_RAW_BASE = "https://raw.githubusercontent.com/remynollet/RNolletKiteKnowledge/main/content"
STAGING_DIR = Path("Kite-knowledge/staging")

# Mapping: (Remote path, Entity Type, Target Folder)
MIGRATION_LIST = [
    # People / Pilots
    ("communaute/cerf-volistes/alain-lemoine.md", "person", "people"),
    ("communaute/cerf-volistes/birger-garbe-ulzburger.md", "person", "people"),
    ("communaute/cerf-volistes/bruno-berthebaud.md", "person", "people"),
    ("communaute/cerf-volistes/didier-ferment.md", "person", "people"),
    ("communaute/cerf-volistes/guido-maiocchi.md", "person", "people"),
    ("communaute/cerf-volistes/jean-apostolides.md", "person", "people"),
    ("communaute/cerf-volistes/jeremy-dupont.md", "person", "people"),
    ("communaute/cerf-volistes/julien-lahyani.md", "person", "people"),
    ("communaute/cerf-volistes/marc-levesque.md", "person", "people"),
    ("communaute/cerf-volistes/nils-guhl.md", "person", "people"),
    ("communaute/cerf-volistes/olivier-rethore.md", "person", "people"),
    ("communaute/cerf-volistes/pascal-brunel.md", "person", "people"),
    ("communaute/cerf-volistes/peter-lynn.md", "person", "people"),
    ("communaute/cerf-volistes/peter-maternus.md", "person", "people"),
    ("communaute/cerf-volistes/philippe-chatelain.md", "person", "people"),
    ("communaute/cerf-volistes/remy-nollet.md", "person", "people"),
    ("communaute/pilotes/samuel-roger.md", "person", "people"),
    ("communaute/cerf-volistes/steff-ferme.md", "person", "people"),
    ("communaute/pilotes/stephane-ferme.md", "person", "people"),
    ("communaute/cerf-volistes/thierry-bressure.md", "person", "people"),
    ("communaute/cerf-volistes/yasumasa-numata.md", "person", "people"),
    
    # Clubs
    ("communaute/clubs/ailes-du-delire.md", "club", "clubs"),
    ("communaute/clubs/ailes-du-plaisir.md", "club", "clubs"),
    ("communaute/clubs/berck-kite-club.md", "club", "clubs"),
    ("communaute/clubs/club-bertry.md", "club", "clubs"),
    ("communaute/clubs/le-vent-de-bray-dunes.md", "club", "clubs"),
    ("communaute/clubs/les-galibots.md", "club", "clubs"),
    ("communaute/clubs/miztral.md", "club", "clubs"),
    ("communaute/clubs/ok-mistral.md", "club", "clubs"),
    
    # Models
    ("types/pilotables/orao-fourlines.md", "model", "models"),
    ("types/pilotables/revolution-quad.md", "model", "models"),
    ("types/pilotables/skyburner-fulcrum.md", "model", "models"),
    
    # History
    ("histoire/brevets-inventeurs.md", "timeline", "timeline"),
    ("histoire/evolution-cerfs-volants-competition.md", "timeline", "timeline"),
    ("histoire/origines-anciennes.md", "timeline", "timeline"),
]

NEW_TEMPLATE = """---
id: "{slug}"
type: "{type}"
title: "{title}"
date_range: "{date_range}"
geography: "{geography}"
category: "{category}"
tags: {tags}
related: []
summary: "{summary}"
ai_status: "draft"
source_verified: false
reviewer: null
review_date: null
---

# {title}

## Summary

{summary_long}

## Key Facts

| Field | Value |
|---|---|
| Date range | {date_range} |
| Geography | {geography} |
| Category | {category} |

## Historical Context / Full Content (Migrated)

{body}

## Sources (Migrated)

{sources}
"""

def migrate():
    if not STAGING_DIR.exists():
        print(f"ERROR: {STAGING_DIR} not found. Please run from project root.")
        return

    for remote_path, entity_type, target_folder in MIGRATION_LIST:
        slug = Path(remote_path).stem
        output_path = STAGING_DIR / target_folder / f"{slug}.md"
        
        if output_path.exists():
            print(f"SKIP: {slug} already exists in staging.")
            continue
            
        url = f"{REMOTE_RAW_BASE}/{remote_path}"
        print(f"FETCHING: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_content = response.text
        except Exception as e:
            print(f"FAILED to fetch {url}: {e}")
            continue

        # Parse Hugo Frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---", raw_content, re.DOTALL)
        if not fm_match:
            print(f"ERROR: No frontmatter in {remote_path}")
            continue
            
        old_fm = yaml.safe_load(fm_match.group(1))
        body = raw_content[fm_match.end():].strip()
        
        # Mapping fields
        title = old_fm.get("title", slug.replace("-", " ").title())
        summary = old_fm.get("description", f"Documentation for {title}.")
        tags = old_fm.get("tags", [entity_type])
        if entity_type not in tags:
            tags.append(entity_type)
            
        # Extract sources from body if present
        sources = "Add sources here."
        if "## Sources" in body:
            parts = body.split("## Sources", 1)
            body = parts[0].strip()
            sources = parts[1].strip()
        elif "## Références" in body:
            parts = body.split("## Références", 1)
            body = parts[0].strip()
            sources = parts[1].strip()

        # Prepare new content
        new_content = NEW_TEMPLATE.format(
            slug=slug,
            type=entity_type,
            title=title,
            date_range="TODO: 19XX-present",
            geography="TODO: Country",
            category="TODO: Role",
            tags=yaml.dump(tags, allow_unicode=True, default_flow_style=False).strip(),
            summary=summary,
            summary_long=summary,
            body=body,
            sources=sources
        )
        
        # Ensure target dir exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(new_content, encoding="utf-8")
        print(f"✓ MIGRATED: {output_path}")

if __name__ == "__main__":
    migrate()
