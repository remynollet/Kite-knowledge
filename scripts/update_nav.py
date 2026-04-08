import os
import re
from pathlib import Path
import yaml

# Configuration - Look for files in current dir first, then fallback
MKDOCS_FILE = Path("mkdocs.yml")
DOCS_DIR = Path("docs")

if not MKDOCS_FILE.exists():
    MKDOCS_FILE = Path("Kite-knowledge/mkdocs.yml")
    DOCS_DIR = Path("Kite-knowledge/docs")

def get_title(path):
    try:
        content = path.read_text(encoding='utf-8')
        match = re.search(r'^title:\s*\"?(.*?)\"?\s*$', content, re.MULTILINE)
        if match:
            t = match.group(1).strip()
            if ":" in t:
                t = t.split(":")[0].strip()
            return t
    except:
        pass
    return path.stem.replace('-', ' ').title()

def scan_dir(subdir, exclude_index=True):
    folder = DOCS_DIR / subdir
    if not folder.exists():
        return []
    items = []
    files = sorted(folder.glob("*.md"))
    for f in files:
        if any(f.name.endswith(ext) for ext in [".en.md", ".de.md", ".it.md", ".es.md"]):
            continue
        if exclude_index and f.name == "index.md":
            continue
        title = get_title(f)
        items.append({title: f"{subdir}/{f.name}"})
    return items

def generate_nav():
    nav = [
        {"Home": "index.md"},
        {"People": [{"Home": "people/index.md"}] + scan_dir("people")},
        {"Brands": [{"Home": "brands/index.md"}] + scan_dir("brands")},
        {"Models": [{"Home": "models/index.md"}] + scan_dir("models")},
        {"Materials": [{"Home": "materials/index.md"}] + scan_dir("materials")},
        {"Frames": [{"Home": "frames/index.md"}] + scan_dir("frames")},
        {"Clubs": [{"Home": "clubs/index.md"}] + scan_dir("clubs")},
        {"Teams": scan_dir("teams", exclude_index=False)},
        {"Festivals": scan_dir("festivals", exclude_index=False)},
        {"Shops": [{"Home": "shops/index.md"}] + scan_dir("shops")},
        {"Timeline": [{"Home": "timeline/index.md"}] + scan_dir("timeline")},
        {"Releases": [{"Home": "releases/index.md"}] + scan_dir("releases")},
        {"Community": [
            {"Contributors": "contributors.md"},
            {"Pilots": "pilots/index.md"}
        ]},
        {"Glossary": "glossary/index.md"}
    ]
    return nav

def update_mkdocs():
    if not MKDOCS_FILE.exists():
        print(f"ERROR: mkdocs.yml not found.")
        return

    with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["nav"] = generate_nav()

    with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"✓ Navigation updated in {MKDOCS_FILE}")

if __name__ == "__main__":
    update_mkdocs()
