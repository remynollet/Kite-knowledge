import yaml
import re
import argparse
from pathlib import Path

# NOTE: This script is a template/infrastructure for the AI translation pipeline.
# In a real environment, it would call an LLM API (OpenAI, Anthropic, etc.).
# For this YOLO mode, the script prepares the structure and placeholders.

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
    # 1. Protect technical terms (simple substitution for now as a proof of concept)
    # In a real pipeline, these would be passed as 'hints' or 'system prompt' to the LLM.
    translated_content = content
    
    # Simple demo: replace FR terms with target lang terms if found in content
    # (Only for very specific keywords to avoid linguistic mess without real LLM)
    for term in dictionary["terms"]:
        fr_term = term.get("fr")
        target_term = term.get(target_lang)
        if fr_term and target_term:
            # Case insensitive replace
            pattern = re.compile(re.escape(fr_term), re.IGNORECASE)
            translated_content = pattern.sub(target_term, translated_content)
            
    return translated_content

def translate_entity(file_path, target_lang):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: File {file_path} not found.")
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

    # Update frontmatter
    fm["ai_translated"] = True
    # Keep ai_status as validated if the source was validated, but maybe add a note
    # or keep it as in-review for Linguistic Ambassador validation as per PRD
    fm["ai_status"] = "in-review" 

    # Translate body (Simulation)
    translated_body = translate_content(body, target_lang, dictionary)
    
    # Construct new file
    new_fm_raw = yaml.dump(fm, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{new_fm_raw}---\n{translated_body}"
    
    output_path = file_path.with_suffix(f".{target_lang}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✓ Created translation draft: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AI translation for an entity.")
    parser.add_argument("file", help="Path to the source .md file (usually in docs/)")
    parser.add_argument("--lang", default="en", help="Target language code (en, de, it, es)")
    args = parser.parse_args()
    
    translate_entity(args.file, args.lang)
