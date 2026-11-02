"""
Create expanded multilingual training dataset (~6000 samples).
This data TEACHES the model to ignore injections in all languages.

Strategy:
- Load English Alpaca dataset as base instruction-following data
- Inject multilingual attacks into the input fields
- Keep the CORRECT original output (model learns to ignore attacks)
- Balance clean vs attacked samples (50/50)
"""

import json
import random
import os
from collections import Counter
from expanded_attack_templates import (
    ENGLISH_ATTACKS, HINDI_NATIVE_ATTACKS, HINGLISH_ATTACKS,
    BENGALI_NATIVE_ATTACKS, TAMIL_NATIVE_ATTACKS, MARATHI_NATIVE_ATTACKS,
    TELUGU_NATIVE_ATTACKS, CROSS_LINGUAL_ATTACKS, CULTURAL_ATTACKS,
    format_attack
)


def load_base_data():
    """Load English Alpaca dataset as base."""
    try:
        from datasets import load_dataset
        print("Loading English Alpaca dataset from HuggingFace...")
        alpaca = load_dataset("tatsu-lab/alpaca", split="train")

        # Filter to samples WITH input AND non-empty output
        samples_with_input = [
            s for s in alpaca
            if s["input"].strip() and s["output"].strip()
        ]
        print(f"  Loaded {len(samples_with_input)} samples with input and output")
        return samples_with_input
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Falling back to synthetic base data...")
        return create_synthetic_base_data()


def create_synthetic_base_data():
    """Create synthetic base data if Alpaca dataset is unavailable."""
    instructions = [
        "Summarize the following text.",
        "What is the main point of this passage?",
        "Extract key information from the text below.",
        "Provide a brief overview of this content.",
        "List the main facts mentioned below.",
        "What conclusions can be drawn from this text?",
        "Paraphrase the following in simpler words.",
        "Identify the most important details below.",
        "What does this text primarily discuss?",
        "Explain the main idea of this passage.",
        "Translate the following text to English.",
        "Classify the sentiment of this text.",
        "What are the key takeaways here?",
        "Rewrite this text in a formal tone.",
        "Answer the question based on the context below.",
    ]

    inputs = [
        "The quarterly earnings report shows that the company's revenue grew by 12% compared to the same period last year. Net profit margins improved from 8% to 11%. The CEO attributed the growth to expansion in the Asia-Pacific region.",
        "Scientists have discovered a new species of deep-sea fish in the Pacific Ocean. The fish lives at depths exceeding 8,000 meters and has unique bioluminescent properties that help it navigate the dark environment.",
        "The Indian government announced a new policy to promote electric vehicles. Under the scheme, buyers of electric cars will receive a subsidy of up to 1.5 lakh rupees. The policy aims to have 30% of vehicles be electric by 2030.",
        "A recent study published in Nature found that forests absorb about 30% of human-made carbon dioxide emissions. However, deforestation and wildfires are reducing this capacity at an alarming rate.",
        "The World Health Organization released new guidelines on nutrition, recommending a diet rich in fruits, vegetables, and whole grains. Processed food consumption should be limited to reduce the risk of chronic diseases.",
        "Bangalore has become India's leading technology hub, hosting offices of major global tech companies. The city's IT sector employs over 1.5 million professionals and contributes significantly to the national economy.",
        "The Mars rover Perseverance has successfully collected its tenth rock sample. Scientists believe these samples could contain microscopic fossils that would prove life once existed on the Red Planet.",
        "Heavy monsoon rains caused flooding in several districts of Maharashtra. Over 50,000 people were evacuated from low-lying areas. Relief teams are providing food and medical supplies to affected communities.",
        "A new machine learning algorithm can predict protein structures with 95% accuracy. This breakthrough could accelerate drug discovery and help scientists understand diseases at a molecular level.",
        "The Reserve Bank of India kept the repo rate unchanged at 6.5% in its latest policy review. The decision was influenced by concerns about food price inflation despite overall economic growth remaining stable.",
        "Tokyo hosted the 2021 Summer Olympics after a year-long delay due to the COVID-19 pandemic. Athletes from 206 countries participated, with the USA leading the medal tally with 113 medals.",
        "Coffee production in Brazil has been affected by unusual frost events. Global coffee prices have risen by 25% as a result, impacting both local farmers and international supply chains.",
        "The European Union passed new regulations on artificial intelligence, requiring companies to disclose when AI is used in decision-making processes that affect citizens. Heavy fines will be imposed for non-compliance.",
        "A team of archaeologists discovered ancient pottery fragments near the Indus Valley site. The artifacts date back to approximately 3000 BCE and provide new insights into trade routes of the Harappan civilization.",
        "Tesla announced plans to build a new Gigafactory in Indonesia to leverage the country's rich nickel deposits. The factory is expected to produce 500,000 battery packs annually starting in 2026.",
    ]

    outputs = [
        "The company's revenue grew 12% year-over-year with improved profit margins of 11%, driven by Asia-Pacific expansion.",
        "A new bioluminescent deep-sea fish species was discovered at depths over 8,000 meters in the Pacific Ocean.",
        "India's new EV policy offers subsidies up to 1.5 lakh rupees to electric car buyers, targeting 30% electric vehicles by 2030.",
        "Forests absorb 30% of human CO2 emissions, but deforestation and wildfires are reducing this carbon absorption capacity.",
        "WHO recommends diets rich in fruits, vegetables, and whole grains while limiting processed food to prevent chronic diseases.",
        "Bangalore is India's top tech hub with 1.5 million IT professionals and significant contributions to the national economy.",
        "The Perseverance rover collected its tenth rock sample from Mars, which may contain evidence of ancient microbial life.",
        "Heavy monsoon rains caused flooding in Maharashtra, leading to evacuation of over 50,000 people with relief operations underway.",
        "A new ML algorithm predicts protein structures with 95% accuracy, potentially accelerating drug discovery.",
        "RBI maintained the repo rate at 6.5% due to food inflation concerns despite stable overall economic growth.",
        "The delayed 2021 Tokyo Olympics saw 206 countries compete, with the USA winning the most medals at 113.",
        "Brazilian frost events have driven global coffee prices up 25%, affecting farmers and international supply chains.",
        "EU's new AI regulations require disclosure of AI in citizen-affecting decisions, with significant fines for violations.",
        "Ancient pottery from ~3000 BCE discovered near the Indus Valley site reveals new information about Harappan trade routes.",
        "Tesla plans an Indonesian Gigafactory leveraging local nickel deposits, targeting 500,000 annual battery packs from 2026.",
    ]

    samples = []
    for _ in range(5000):
        idx = random.randint(0, len(instructions) - 1)
        samples.append({
            "instruction": instructions[idx % len(instructions)],
            "input": inputs[idx % len(inputs)],
            "output": outputs[idx % len(outputs)],
        })
    return samples


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
        "input": attacked_input,
        "output": sample["output"],
        "attacked": True,
        "attack_language": attack_language,
        "injection_text": attack_text,
    }


def create_training_dataset(n_clean=3000, n_attacked=3000):
    """
    Create balanced training dataset:
    - Clean samples: model learns normal behavior
    - Attacked samples: model learns to ignore injections
    """
    base_data = load_base_data()
    training_data = []

    # --- CLEAN SAMPLES ---
    print(f"\nCreating {n_clean} clean samples...")
    for i in range(n_clean):
        sample = base_data[i % len(base_data)]
        training_data.append(create_clean_sample(sample))

    # --- ATTACKED SAMPLES ---
    print(f"Creating {n_attacked} attacked samples...")

    # Same language distribution as original (matching eval ratios)
    attack_languages = {
        "english":       (ENGLISH_ATTACKS,       0.225),
        "hindi_native":  (HINDI_NATIVE_ATTACKS,  0.170),
        "hinglish":      (HINGLISH_ATTACKS,      0.210),
        "bengali":       (BENGALI_NATIVE_ATTACKS, 0.070),
        "tamil":         (TAMIL_NATIVE_ATTACKS,   0.045),
        "marathi":       (MARATHI_NATIVE_ATTACKS, 0.040),
        "telugu":        (TELUGU_NATIVE_ATTACKS,  0.030),
        "cross_lingual": (CROSS_LINGUAL_ATTACKS,  0.100),
        "cultural":      (CULTURAL_ATTACKS,       0.110),
    }

    for lang, (attack_dict, fraction) in attack_languages.items():
        n_samples = max(1, int(n_attacked * fraction))

        # Collect all templates for this language
        all_attacks = []
        for attack_type, attack_list in attack_dict.items():
            for template in attack_list:
                all_attacks.append(template)

        for i in range(n_samples):
            sample = random.choice(base_data)
            attack_template = all_attacks[i % len(all_attacks)]
            attacked = create_attacked_sample(sample, lang, attack_template)
            training_data.append(attacked)

    random.shuffle(training_data)

    # Print stats
    print(f"\nTraining dataset stats:")
    print(f"  Total samples: {len(training_data)}")
    print(f"  Clean: {sum(1 for s in training_data if not s['attacked'])}")
    print(f"  Attacked: {sum(1 for s in training_data if s['attacked'])}")

    lang_counts = Counter(
        s["attack_language"] for s in training_data if s["attacked"]
    )
    print("\n  Attacked samples per language:")
    for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
        pct = count / sum(lang_counts.values()) * 100
        print(f"    {lang:20}: {count:4d} ({pct:5.1f}%)")

    return training_data


if __name__ == "__main__":
    random.seed(42)  # Reproducibility

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "multilingual_train_dataset_v2.json")

    print("=" * 60)
    print("Creating Expanded Training Dataset (~6000 samples)")
    print("=" * 60)

    dataset = create_training_dataset(n_clean=3000, n_attacked=3000)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(dataset)} samples to {output_path}")
    print("Done!")
