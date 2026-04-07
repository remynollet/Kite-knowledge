import yaml
import os
from pathlib import Path

def generate_glossaries():
    """
    Generates localized glossary pages from the technical dictionary YAML.
    """
    dict_path = Path("scripts/data/technical_dictionary.yaml")
    output_dir = Path("docs/glossary")
    
    if not dict_path.exists():
        # Fallback for root execution
        dict_path = Path("Kite-knowledge/scripts/data/technical_dictionary.yaml")
        output_dir = Path("Kite-knowledge/docs/glossary")

    if not dict_path.exists():
        print(f"ERROR: Dictionary not found at {dict_path}")
        return

    with open(dict_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    languages = {
        "fr": {"title": "Glossaire Technique", "header": "Définitions des termes techniques utilisés dans Kite-knowledge.", "term_key": "fr", "desc_key": "description_fr"},
        "en": {"title": "Technical Glossary", "header": "Definitions for technical terms used throughout Kite-knowledge.", "term_key": "en", "desc_key": "description_en"}
    }

    for lang_code, config in languages.items():
        filename = "index.md" if lang_code == "fr" else f"index.{lang_code}.md"
        file_path = output_dir / filename
        
        content = [f"# {config['title']}\n", f"{config['header']}\n"]
        
        # Sort terms by localized name
        sorted_terms = sorted(data["terms"], key=lambda x: x.get(config["term_key"], x["id"]).lower())
        
        for term in sorted_terms:
            name = term.get(config["term_key"], term["id"]).capitalize()
            desc = term.get(config["desc_key"], "Description pending.")
            
            # Show other translations in a small text block
            others = []
            for l in ["fr", "en", "de", "it", "es"]:
                if l != lang_code and l in term:
                    others.append(f"{l.upper()}: {term[l]}")
            
            content.append(f"### {name}")
            content.append(f"{desc}")
            if others:
                content.append(f"*({', '.join(others)})*")
            content.append("")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"✓ Generated: {file_path}")

if __name__ == "__main__":
    generate_glossaries()
