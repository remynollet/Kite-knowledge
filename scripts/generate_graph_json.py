#!/usr/bin/env python3
"""generate_graph_json.py — Generate a D3.js compatible JSON from entity relationships."""

import json
import os
import re
from pathlib import Path
import yaml

# Run from project root or Kite-knowledge folder
DOCS_DIR = Path("docs")
if not DOCS_DIR.exists():
    DOCS_DIR = Path("Kite-knowledge/docs")

OUTPUT_PATH = DOCS_DIR / "assets/data/graph.json"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

def extract_id_from_path(path_str):
    """Extracts slug from '../type/slug.md' or 'slug'."""
    if not path_str:
        return None
    # Remove extension if present
    s = path_str.replace(".md", "")
    # Take the last part of the path
    return s.split("/")[-1]

def generate_graph():
    nodes = []
    links = []
    
    # First pass: Collect all entities as nodes
    entity_map = {} # id -> metadata
    
    for root, _, files in os.walk(DOCS_DIR):
        if "assets" in root or "stylesheets" in root or "glossary" in root:
            continue
            
        for name in files:
            # Only process source files (not translations)
            if name.endswith(".md") and not any(name.endswith(f".{l}.md") for l in ["en", "de", "it", "es"]):
                if name == "index.md":
                    continue
                    
                path = Path(root) / name
                content = path.read_text(encoding="utf-8")
                match = FRONTMATTER_RE.match(content)
                if not match:
                    continue
                
                fm = yaml.safe_load(match.group(1))
                eid = fm.get("id")
                etype = fm.get("type")
                title = fm.get("title")
                
                if not eid:
                    continue
                    
                node = {
                    "id": eid,
                    "name": title,
                    "type": etype
                }
                nodes.append(node)
                entity_map[eid] = fm

    # Second pass: Create links
    for eid, fm in entity_map.items():
        # 1. Related links
        related = fm.get("related", [])
        if isinstance(related, list):
            for r_path in related:
                target_id = extract_id_from_path(r_path)
                if target_id in entity_map:
                    links.append({
                        "source": eid,
                        "target": target_id,
                        "type": "related"
                    })
        
        # 2. Manufacturer -> Brand
        manu = fm.get("manufacturer")
        if manu and manu in entity_map:
            links.append({
                "source": eid,
                "target": manu,
                "type": "produced_by"
            })
            
        # 3. Designer -> Person
        designer = fm.get("designer")
        if designer and designer in entity_map:
            links.append({
                "source": eid,
                "target": designer,
                "type": "designed_by"
            })
            
        # 4. Founder -> Person
        founder = fm.get("founder")
        if founder and founder in entity_map:
            links.append({
                "source": eid,
                "target": founder,
                "type": "founded_by"
            })
            
        # 5. Members -> Person
        members = fm.get("members", [])
        if isinstance(members, list):
            for m_id in members:
                if m_id in entity_map:
                    links.append({
                        "source": m_id,
                        "target": eid,
                        "type": "member_of"
                    })

    # Deduplicate links (bidirectional links might create duplicates)
    unique_links = []
    seen = set()
    for l in links:
        # Sort source/target to treat A->B and B->A as same if needed, 
        # but here we might want to keep direction for some types.
        # For now, let's just avoid exact duplicates.
        link_id = tuple(sorted([l["source"], l["target"]])) + (l["type"],)
        if link_id not in seen:
            unique_links.append(l)
            seen.add(link_id)

    graph_data = {
        "nodes": nodes,
        "links": unique_links
    }

    # Ensure directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
    print(f"✓ Generated knowledge graph with {len(nodes)} nodes and {len(unique_links)} links in {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_graph()
