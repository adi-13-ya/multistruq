"""
Create the multilingual training dataset for MultiStruQ fine-tuning.
This data TEACHES the model to ignore injections in all languages.

Strategy:
- Load English Alpaca dataset as base instruction-following data
- Inject multilingual attacks into the input fields
- Keep the CORRECT original output (model learns to ignore attacks)
- Balance clean vs attacked samples
"""

import json
import random
import os
from datasets import load_dataset
from attack_templates import (
    ENGLISH_ATTACKS, HINDI_NATIVE_ATTACKS, HINGLISH_ATTACKS,
    BENGALI_NATIVE_ATTACKS, TAMIL_NATIVE_ATTACKS, MARATHI_NATIVE_ATTACKS,
    TELUGU_NATIVE_ATTACKS, CROSS_LINGUAL_ATTACKS, CULTURAL_ATTACKS,
    format_attack
)


def load_base_data():
    """Load English Alpaca dataset as base."""
    print("Loading English Alpaca dataset...")
    alpaca = load_dataset("tatsu-lab/alpaca", split="train")

    # Filter to samples WITH input AND non-empty output
    samples_with_input = [
        s for s in alpaca 
        if s["input"].strip() and s["output"].strip()
    ]
    print(f"  Loaded {len(samples_with_input)} samples with input and output")
    return samples_with_input


def create_clean_sample(sample):
    """Create a clean (unattacked) training sample."""
    return {
        "instruction": sample["instruction"],
        "input": sample["input"],
        "output": sample["output"],
        "attacked": False,
        "attack_language": None,
    }


def create_attacked_sample(sample, attack_language, attack_template):
    """
    Create an attacked training sample.
    The model must learn to output the ORIGINAL response,
    even when the data contains an injection.
    """
    attack_text = format_attack(attack_template)
    attacked_input = sample["input"] + "\n" + attack_text

    return {
        "instruction": sample["instruction"],
        "input": attacked_input,          # Contains the injection
        "output": sample["output"],       # CORRECT original response
        "attacked": True,
        "attack_language": attack_language,
        "injection_text": attack_text,
    }


def create_training_dataset(n_clean=5000, n_attacked=5000):
    """
    Create balanced training dataset with:
    - Clean samples: model learns normal behavior
    - Attacked samples: model learns to ignore injections
    """
    base_data = load_base_data()

    training_data = []

    # --- CLEAN SAMPLES ---
    print(f"\nCreating {n_clean} clean samples...")
    clean_samples = random.sample(base_data, min(n_clean, len(base_data)))
    for s in clean_samples:
        training_data.append(create_clean_sample(s))

    # --- ATTACKED SAMPLES ---
    print(f"Creating {n_attacked} attacked samples...")

    # Define attack distribution across languages
    attack_languages = {
        "english": (ENGLISH_ATTACKS, 0.25),
        "hindi_native": (HINDI_NATIVE_ATTACKS, 0.20),
        "hinglish": (HINGLISH_ATTACKS, 0.15),
        "bengali": (BENGALI_NATIVE_ATTACKS, 0.10),
        "tamil": (TAMIL_NATIVE_ATTACKS, 0.05),
        "marathi": (MARATHI_NATIVE_ATTACKS, 0.05),
        "telugu": (TELUGU_NATIVE_ATTACKS, 0.05),
        "cross_lingual": (CROSS_LINGUAL_ATTACKS, 0.10),
        "cultural": (CULTURAL_ATTACKS, 0.05),
    }

    for lang, (attack_dict, fraction) in attack_languages.items():
        n_samples = int(n_attacked * fraction)

        for _ in range(n_samples):
            # Pick random base sample
            sample = random.choice(base_data)

            # Pick random attack type and template
            attack_type = random.choice(list(attack_dict.keys()))
            attack_template = random.choice(attack_dict[attack_type])

            attacked = create_attacked_sample(sample, lang, attack_template)
            training_data.append(attacked)

    random.shuffle(training_data)

    # Print stats
    print(f"\nTraining dataset stats:")
    print(f"  Total samples: {len(training_data)}")
    print(f"  Clean: {sum(1 for s in training_data if not s['attacked'])}")
    print(f"  Attacked: {sum(1 for s in training_data if s['attacked'])}")

    from collections import Counter
    lang_counts = Counter(
        s["attack_language"] for s in training_data if s["attacked"]
    )
    print("\n  Attacked samples per language:")
    for lang, count in sorted(lang_counts.items()):
        print(f"    {lang}: {count}")

    return training_data


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-clean", type=int, default=2000,
                        help="Number of clean samples (default: 2000)")
    parser.add_argument("--n-attacked", type=int, default=2000,
                        help="Number of attacked samples (default: 2000)")
    parser.add_argument("--output", default=None,
                        help="Output JSON path")
    args = parser.parse_args()

    output_path = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "multilingual_train_dataset.json"
    )

    print("Creating multilingual training dataset...")
    dataset = create_training_dataset(
        n_clean=args.n_clean,
        n_attacked=args.n_attacked,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(dataset)} samples to {output_path}")
    print("Done!")
