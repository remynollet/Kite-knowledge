import yaml
import re
import os
from pathlib import Path

# Fields that MUST be identical across all language versions
TECH_FIELDS = [
    "id", "type", "date_range", "related", "patent_url", "archive_file", 
    "manufacturer", "designer", "wingspan", "wind_range", "level", "image", 
    "pinterest_board_id", "members", "website", "social", "coordinates", "logo",
    "affiliation"
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

def sync_file(source_path):
    source_path = Path(source_path)
    if not source_path.exists():
        return

    # Read source frontmatter
    with open(source_path, "r", encoding="utf-8") as f:
        source_text = f.read()
    
    source_match = FRONTMATTER_RE.match(source_text)
    if not source_match:
        return
    
    source_fm = yaml.safe_load(source_match.group(1))
    
    # Find translations
    base_name = source_path.stem
    directory = source_path.parent
    
    for lang in ["en", "de", "it", "es"]:
        trans_path = directory / f"{base_name}.{lang}.md"
        if trans_path.exists():
            with open(trans_path, "r", encoding="utf-8") as f:
                trans_text = f.read()
            
            trans_match = FRONTMATTER_RE.match(trans_text)
            if not trans_match:
                continue
            
            trans_fm = yaml.safe_load(trans_match.group(1))
            trans_body = trans_text[trans_match.end():]
            
            # Sync tech fields
            changed = False
            for field in TECH_FIELDS:
                if field in source_fm and source_fm[field] != trans_fm.get(field):
                    trans_fm[field] = source_fm[field]
                    changed = True
            
            if changed:
                new_fm_raw = yaml.dump(trans_fm, allow_unicode=True, sort_keys=False)
                new_content = f"---\n{new_fm_raw}---\n{trans_body}"
                with open(trans_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"  ⇄ Synced {field} fields to {trans_path.name}")

def main():
    docs_dir = Path("docs")
    if not docs_dir.exists():
        docs_dir = Path("Kite-knowledge/docs")
        
    print(f"Starting metadata synchronization in {docs_dir}...")
    
    for root, _, files in os.walk(docs_dir):
        for name in files:
            # Only process source files (not containing .lang.md)
            if name.endswith(".md") and not any(name.endswith(f".{l}.md") for l in ["en", "de", "it", "es"]):
                sync_file(Path(root) / name)

if __name__ == "__main__":
    main()
