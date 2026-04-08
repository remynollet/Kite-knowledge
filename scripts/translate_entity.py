import yaml
import re
import argparse
import os
from pathlib import Path

# NOTE: This script is an infrastructure for the AI translation pipeline.
# It handles frontmatter preservation and technical terminology enforcement.

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

def load_dictionary():
    dict_path = Path("scripts/data/technical_dictionary.yaml")
    if not dict_path.exists():
        dict_path = Path("Kite-knowledge/scripts/data/technical_dictionary.yaml")
    
    with open(dict_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def translate_content(content, target_lang, dictionary):
    """
    Placeholder for LLM translation logic.
    Ensures technical terms from the dictionary are respected.
    """
    translated_content = content
    
    # demo: replace FR terms with target lang terms if found in content
    # In a production pipeline, this would be a prompt hint for the LLM.
    for term in dictionary["terms"]:
        fr_term = term.get("fr")
        target_term = term.get(target_lang)
        if fr_term and target_term:
            pattern = re.compile(re.escape(fr_term), re.IGNORECASE)
            translated_content = pattern.sub(target_term, translated_content)
            
    return translated_content

def translate_entity(file_path, target_lang, force=False):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: File {file_path} not found.")
        return

    # Skip if already a localized file
    if any(file_path.name.endswith(f".{l}.md") for l in ["en", "de", "it", "es"]):
        return

    output_path = file_path.with_suffix(f".{target_lang}.md")
    if output_path.exists() and not force:
        print(f"SKIP: {output_path} already exists. Use --force to overwrite.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    match = FRONTMATTER_RE.match(raw_text)
    if not match:
        print(f"ERROR: No frontmatter in {file_path}")
        return

    fm_raw = match.group(1)
    body = raw_text[match.end():]
    fm = yaml.safe_load(fm_raw)
    dictionary = load_dictionary()

    # Update frontmatter for translation
    fm["ai_translated"] = True
    fm["ai_status"] = "in-review" # Needs native speaker/Ambassador review

    # Translate body (Simulation/Placeholder)
    translated_body = translate_content(body, target_lang, dictionary)
    
    # Construct new file
    new_fm_raw = yaml.dump(fm, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{new_fm_raw}---\n{translated_body}"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✓ Translated: {file_path} -> {output_path}")

def batch_translate(directory, target_lang, force=False):
    path = Path(directory)
    for root, _, files in os.walk(path):
        for name in files:
            if name.endswith(".md"):
                file_path = Path(root) / name
                translate_entity(file_path, target_lang, force)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AI translation for entities.")
    parser.add_argument("path", help="Path to a file or directory to translate.")
    parser.add_argument("--lang", default="en", help="Target language code (en, de, it, es).")
    parser.add_argument("--force", action="store_true", help="Overwrite existing translations.")
    args = parser.parse_args()
    
    if os.path.isdir(args.path):
        batch_translate(args.path, args.lang, args.force)
    else:
        translate_entity(args.path, args.lang, args.force)
