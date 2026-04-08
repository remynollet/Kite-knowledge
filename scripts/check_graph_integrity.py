#!/usr/bin/env python3
"""check_graph_integrity.py — Quality automation for the knowledge graph."""

import json
from pathlib import Path

# Run from project root or Kite-knowledge folder
DOCS_DIR = Path("docs")
if not DOCS_DIR.exists():
    DOCS_DIR = Path("Kite-knowledge/docs")

GRAPH_DATA_PATH = DOCS_DIR / "assets/data/graph.json"

def check_integrity():
    if not GRAPH_DATA_PATH.exists():
        print(f"ERROR: Graph data not found at {GRAPH_DATA_PATH}. Run generate_graph_json.py first.")
        return 1

    with open(GRAPH_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    links = data.get("links", [])

    # node_id -> list of links where it is source or target
    connection_count = {node["id"]: 0 for node in nodes}
    
    for link in links:
        source = link["source"]
        target = link["target"]
        if source in connection_count:
            connection_count[source] += 1
        if target in connection_count:
            connection_count[target] += 1

    orphans = [node for node in nodes if connection_count[node["id"]] == 0]
    
    # Specific checks
    models_missing_brand = []
    for node in nodes:
        if node["type"] == "model":
            # Check if has a 'produced_by' link
            has_brand = any(l for l in links if l["source"] == node["id"] and l["type"] == "produced_by")
            if not has_brand:
                models_missing_brand.append(node)

    print("\n--- Knowledge Graph Integrity Report ---")
    
    print(f"\nTotal Nodes: {len(nodes)}")
    print(f"Total Links: {len(links)}")
    
    if orphans:
        print(f"\n⚠️ Found {len(orphans)} orphaned entities (0 connections):")
        for node in orphans[:10]:
            print(f"  - [{node['type']}] {node['name']} ({node['id']})")
        if len(orphans) > 10:
            print(f"  ... and {len(orphans) - 10} more.")
    else:
        print("\n✅ No orphaned entities found.")

    if models_missing_brand:
        print(f"\n⚠️ Found {len(models_missing_brand)} models missing a brand (manufacturer) link:")
        for node in models_missing_brand[:10]:
            print(f"  - {node['name']} ({node['id']})")
        if len(models_missing_brand) > 10:
            print(f"  ... and {len(models_missing_brand) - 10} more.")
    else:
        print("\n✅ All models have at least one brand link.")

    print("\n--- Recommendation ---")
    if orphans or models_missing_brand:
        print("Update the 'related', 'manufacturer', or 'designer' fields in these files to strengthen the graph.")
    else:
        print("Knowledge graph is dense and well-connected!")
    print("----------------------------------------\n")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(check_integrity())
