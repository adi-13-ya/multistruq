"""
Validate the datasets before using them for training/evaluation.
Checks both the IndicJR-based eval dataset and the training dataset.
"""

import json
import os
import sys
from collections import Counter


def validate_eval_dataset(filepath):
    """Validate the IndicJR-based evaluation dataset."""
    print(f"\n{'='*60}")
    print(f"Validating EVAL dataset: {filepath}")
    print(f"{'='*60}")

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    errors = []

    # Check top-level structure
    if "metadata" not in data:
        errors.append("Missing 'metadata' key")
    if "attacked_benign" not in data:
        errors.append("Missing 'attacked_benign' key")
    if "clean_benign" not in data:
        errors.append("Missing 'clean_benign' key")

    if errors:
        print("STRUCTURAL ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return False

    attacked = data["attacked_benign"]
    clean = data["clean_benign"]

    print(f"  Metadata: {data['metadata']}")
    print(f"  Attacked samples: {len(attacked)}")
    print(f"  Clean samples: {len(clean)}")

    # Validate attacked samples
    for i, sample in enumerate(attacked[:50]):
        if not sample.get("prompt", "").strip():
            errors.append(f"Attacked sample {i} ({sample.get('id','')}): Empty prompt")
        if not sample.get("lang", ""):
            errors.append(f"Attacked sample {i}: Missing lang")
        if not sample.get("id", ""):
            errors.append(f"Attacked sample {i}: Missing id")

    # Validate clean samples
    for i, sample in enumerate(clean[:50]):
        prompt_field = sample.get("prompt") or sample.get("content", "")
        if not prompt_field.strip():
            errors.append(f"Clean sample {i} ({sample.get('id','')}): Empty prompt/content")

    if errors:
        print(f"\nERRORS FOUND ({len(errors)}):")
        for e in errors[:20]:
            print(f"  - {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors)-20} more")
    else:
        print("\n  Validation PASSED! No errors.")

    # Language distribution
    lang_counts = Counter(s["lang"] for s in attacked)
    print("\n  Language distribution (attacked):")
    for lang, count in sorted(lang_counts.items()):
        print(f"    {lang}: {count}")

    # Attack family distribution
    fam_counts = Counter(s.get("family", "unknown") for s in attacked)
    print("\n  Attack family distribution:")
    for fam, count in sorted(fam_counts.items()):
        print(f"    {fam}: {count}")

    # Show sample
    print("\n  Sample attacked entry:")
    s = attacked[0]
    for key, value in s.items():
        val_str = str(value)[:120] + "..." if len(str(value)) > 120 else str(value)
        print(f"    {key}: {val_str}")

    return len(errors) == 0


def validate_train_dataset(filepath):
    """Validate the training dataset."""
    print(f"\n{'='*60}")
    print(f"Validating TRAIN dataset: {filepath}")
    print(f"{'='*60}")

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    errors = []
    print(f"  Total samples: {len(data)}")

    for i, sample in enumerate(data[:100]):
        if not sample.get("instruction", "").strip():
            errors.append(f"Sample {i}: Empty instruction")
        if not sample.get("output", "").strip():
            errors.append(f"Sample {i}: Empty output")
        if "attacked" not in sample:
            errors.append(f"Sample {i}: Missing 'attacked' field")

    if errors:
        print(f"\nERRORS FOUND ({len(errors)}):")
        for e in errors[:20]:
            print(f"  - {e}")
    else:
        print("\n  Validation PASSED! No errors.")

    # Stats
    n_clean = sum(1 for s in data if not s.get("attacked", False))
    n_attacked = sum(1 for s in data if s.get("attacked", False))
    print(f"\n  Clean samples: {n_clean}")
    print(f"  Attacked samples: {n_attacked}")

    lang_counts = Counter(
        s.get("attack_language", "none") for s in data if s.get("attacked", False)
    )
    print("\n  Attack language distribution:")
    for lang, count in sorted(lang_counts.items()):
        print(f"    {lang}: {count}")

    # Show sample
    print("\n  Sample entry:")
    s = data[0]
    for key, value in s.items():
        val_str = str(value)[:120] + "..." if len(str(value)) > 120 else str(value)
        print(f"    {key}: {val_str}")

    return len(errors) == 0


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    eval_path = os.path.join(script_dir, "multilingual_eval_dataset.json")
    train_path = os.path.join(script_dir, "multilingual_train_dataset.json")

    all_ok = True

    if os.path.exists(eval_path):
        ok = validate_eval_dataset(eval_path)
        all_ok = all_ok and ok
    else:
        print(f"\n[SKIP] Eval dataset not found: {eval_path}")
        print("  Run: python create_eval_dataset.py")

    if os.path.exists(train_path):
        ok = validate_train_dataset(train_path)
        all_ok = all_ok and ok
    else:
        print(f"\n[SKIP] Train dataset not found: {train_path}")
        print("  Run: python create_training_dataset.py")

    print("\n" + "=" * 60)
    if all_ok:
        print("ALL VALIDATIONS PASSED!")
    else:
        print("SOME VALIDATIONS FAILED - check errors above")
    print("=" * 60)
