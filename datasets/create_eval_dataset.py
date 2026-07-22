"""
Create the multilingual evaluation dataset for MultiStruQ.
Uses IndicJR benchmark (FREE track) as the primary evaluation source.

IndicJR provides research-grade attack prompts across 12 Indic languages
with multiple attack families (instruction, format, translate).

This script:
1. Reads IndicJR FREE track prompts (attacked_benign subset)
2. Converts them into MultiStruQ evaluation format
3. Saves a unified JSON file for Kaggle evaluation
"""

import json
import os
import glob
from collections import Counter

# Path to IndicJR repo (relative to this file's location)
INDICJR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "indicjr")

# Languages to include (all 12 from IndicJR)
ALL_LANGS = ["hi", "bn", "ta", "te", "ml", "mr", "gu", "kn", "or", "ur", "ne", "pa"]

# Focus languages for initial experiments (subset for faster Kaggle runs)
FOCUS_LANGS = ["hi", "bn", "ta", "te", "mr"]

LANG_NAMES = {
    "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
    "ml": "Malayalam", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
    "or": "Odia", "ur": "Urdu", "ne": "Nepali", "pa": "Punjabi",
}


def load_jsonl(filepath):
    """Load a JSONL file into a list of dicts."""
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def load_indicjr_free_attacked(langs=None):
    """Load attacked-benign prompts from IndicJR FREE track."""
    if langs is None:
        langs = ALL_LANGS

    free_dir = os.path.join(INDICJR_DIR, "prompts_free")
    all_prompts = []

    for lang in langs:
        filepath = os.path.join(free_dir, f"{lang}.jsonl")
        if not os.path.exists(filepath):
            print(f"  [WARN] Missing: {filepath}")
            continue

        prompts = load_jsonl(filepath)
        # Only keep attacked_benign subset
        attacked = [p for p in prompts if p.get("subset") == "attacked_benign"]
        all_prompts.extend(attacked)
        print(f"  {lang} ({LANG_NAMES.get(lang, lang)}): {len(attacked)} attacked prompts")

    return all_prompts


def load_indicjr_free_clean_benign(langs=None):
    """Load clean-benign prompts from IndicJR FREE track."""
    if langs is None:
        langs = ALL_LANGS

    free_dir = os.path.join(INDICJR_DIR, "prompts_free")
    all_prompts = []

    for lang in langs:
        filepath = os.path.join(free_dir, f"clean_benign_{lang}.jsonl")
        if not os.path.exists(filepath):
            print(f"  [WARN] Missing: {filepath}")
            continue

        prompts = load_jsonl(filepath)
        all_prompts.extend(prompts)
        print(f"  {lang} clean-benign: {len(prompts)} prompts")

    return all_prompts


def convert_to_eval_format(indicjr_prompts):
    """Convert IndicJR prompts to MultiStruQ evaluation format."""
    eval_dataset = []

    for p in indicjr_prompts:
        # Get the prompt text (IndicJR uses different fields for different subsets)
        # - attacked_benign: 'prompt' field
        # - clean_benign: 'content' field
        # - JSON track: 'final_prompt' field
        prompt_text = p.get("prompt") or p.get("content") or p.get("final_prompt", "")

        sample = {
            "id": p.get("id") or p.get("prompt_id", "unknown"),
            "lang": p.get("lang", "unknown"),
            "lang_name": LANG_NAMES.get(p.get("lang", ""), p.get("lang", "")),
            "subset": p.get("subset", "attacked_benign"),
            "family": p.get("family", "unknown"),
            "mode": p.get("mode", "unknown"),
            "prompt": prompt_text,
            "source": "indicjr_free",
        }
        eval_dataset.append(sample)

    return eval_dataset


def create_eval_dataset(langs=None, output_path=None):
    """Create the full evaluation dataset."""
    if langs is None:
        langs = FOCUS_LANGS
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "multilingual_eval_dataset.json")

    print("=" * 60)
    print("Creating MultiStruQ Evaluation Dataset (IndicJR FREE track)")
    print("=" * 60)

    # Load attacked-benign prompts
    print("\n--- Attacked-Benign Prompts ---")
    attacked_prompts = load_indicjr_free_attacked(langs)

    # Load clean-benign prompts (for utility testing)
    print("\n--- Clean-Benign Prompts ---")
    clean_prompts = load_indicjr_free_clean_benign(langs)

    # Convert to eval format
    eval_attacked = convert_to_eval_format(attacked_prompts)
    eval_clean = convert_to_eval_format(clean_prompts)

    full_dataset = {
        "metadata": {
            "source": "IndicJR benchmark (FREE track)",
            "languages": langs,
            "total_attacked": len(eval_attacked),
            "total_clean": len(eval_clean),
        },
        "attacked_benign": eval_attacked,
        "clean_benign": eval_clean,
    }

    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_dataset, f, ensure_ascii=False, indent=2)

    # Print stats
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Total attacked-benign: {len(eval_attacked)}")
    print(f"Total clean-benign:    {len(eval_clean)}")

    lang_counts = Counter(s["lang"] for s in eval_attacked)
    print("\nAttacked prompts per language:")
    for lang, count in sorted(lang_counts.items()):
        print(f"  {lang} ({LANG_NAMES.get(lang, '')}): {count}")

    family_counts = Counter(s["family"] for s in eval_attacked)
    print("\nAttacked prompts per attack family:")
    for fam, count in sorted(family_counts.items()):
        print(f"  {fam}: {count}")

    print(f"\nSaved to: {output_path}")
    return full_dataset


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", default=None,
                        help="Comma-separated language codes (default: focus set)")
    parser.add_argument("--all-langs", action="store_true",
                        help="Use all 12 languages")
    parser.add_argument("--output", default=None,
                        help="Output JSON path")
    args = parser.parse_args()

    if args.all_langs:
        langs = ALL_LANGS
    elif args.langs:
        langs = [l.strip() for l in args.langs.split(",")]
    else:
        langs = FOCUS_LANGS

    create_eval_dataset(langs=langs, output_path=args.output)
    print("\nDone!")
