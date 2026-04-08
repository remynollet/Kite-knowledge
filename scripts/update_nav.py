import os
import re
from pathlib import Path
import yaml

# Configuration
MKDOCS_FILE = Path("mkdocs.yml")
DOCS_DIR = Path("docs")

if not MKDOCS_FILE.exists():
    MKDOCS_FILE = Path("Kite-knowledge/mkdocs.yml")
    DOCS_DIR = Path("Kite-knowledge/docs")

ERAS = [
    {"title": "Pioneers & Roots (<1980)", "max_year": 1980},
    {"title": "The Pro-Kite Era (1981-2000)", "max_year": 2000},
    {"title": "Modern Masters (2001-2015)", "max_year": 2015},
    {"title": "Today's Scene (2016+)", "max_year": 9999},
]

def get_metadata(path):
    try:
        content = path.read_text(encoding='utf-8')
        title_match = re.search(r'^title:\s*\"?(.*?)\"?\s*$', content, re.MULTILINE)
        year_match = re.search(r'date_range:\s*\"?(\d{4})', content)
        
        title = title_match.group(1).strip() if title_match else path.stem.replace('-', ' ').title()
        if ":" in title:
            title = title.split(":")[0].strip()
            
        year = int(year_match.group(1)) if year_match else 9999
        return title, year
    except:
        return path.stem.replace('-', ' ').title(), 9999

def scan_and_group(subdir):
    folder = DOCS_DIR / subdir
    if not folder.exists():
        return []
    
    # Initialize eras
    groups = {era["title"]: [] for era in ERAS}
    
    for f in sorted(folder.glob("*.md")):
        if any(f.name.endswith(ext) for ext in [".en.md", ".de.md", ".it.md", ".es.md"]):
            continue
        if f.name == "index.md":
            continue
            
        title, year = get_metadata(f)
        item = {title: f"{subdir}/{f.name}"}
        
        # Find correct era
        for era in ERAS:
            if year <= era["max_year"]:
                groups[era["title"]].append(item)
                break
    
    # Clean up empty eras and format for MkDocs
    result = [{"Home": f"{subdir}/index.md"}]
    for era in ERAS: # Keep order
        era_title = era["title"]
        if groups[era_title]:
            result.append({era_title: groups[era_title]})
            
    return result

def generate_nav():
    nav = [
        {"Home": "index.md"},
        {"People": scan_and_group("people")},
        {"Brands": scan_and_group("brands")},
        {"Models": scan_and_group("models")},
        {"Clubs & Teams": scan_and_group("clubs")},
        {"Festivals": scan_and_group("festivals")},
        {"Shops": [{"Home": "shops/index.md"}] + scan_and_group("shops")[1:]},
        {"Timeline": [
            {"Interactive Timeline": "timeline/index.md"},
            {"Historical Deep Dives": [
                {"Ancient Origins": "timeline/origines-anciennes.md"},
                {"1893 Invention of the Box Kite": "timeline/1893-invention-box-kite.md"},
                {"Evolution of Competition": "timeline/evolution-cerfs-volants-competition.md"},
                {"Patents & Inventors": "timeline/brevets-inventeurs.md"}
            ]}
        ]},
        {"Materials": scan_and_group("materials")},
        {"Frames": scan_and_group("frames")},
        {"Releases": [{"Home": "releases/index.md"}, {"Latest": "releases/2026-04.md"}]},
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
    
    print(f"✓ Hierarchical Navigation updated in {MKDOCS_FILE}")

if __name__ == "__main__":
    update_mkdocs()
