"""
Create the clean-task utility set used by the extended evaluation.

Draws 200 Alpaca examples that have a non-empty input and are disjoint from
the MultiStruQ training corpus (no shared instruction+input pair), so utility
is measured on tasks the adapters have never seen. References are capped at
600 characters so that a 128-token generation budget can cover them.

Output: datasets/utility_eval_dataset_extended.json
"""

import json
import os
import random

N_SAMPLES = 200
MAX_REF_CHARS = 600
SEED = 42


def main():
    from datasets import load_dataset

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "multilingual_train_dataset_v2.json"), encoding="utf-8") as f:
        train = json.load(f)

    # Attacked training inputs carry an appended injection, so compare on the
    # clean prefix as well as the full input.
    seen_pairs = set()
    seen_inputs = set()
    for s in train:
        seen_pairs.add((s["instruction"].strip(), s["input"].strip()))
        seen_inputs.add(s["input"].strip().split("\n\n")[0])

    alpaca = load_dataset("tatsu-lab/alpaca", split="train")
    candidates = []
    for idx, s in enumerate(alpaca):
        ins, inp, out = s["instruction"].strip(), s["input"].strip(), s["output"].strip()
        if not inp or not out or len(out) > MAX_REF_CHARS:
            continue
        if (ins, inp) in seen_pairs or inp in seen_inputs:
            continue
        candidates.append({"id": f"alpaca_{idx}", "instruction": ins, "input": inp, "reference": out})

    random.seed(SEED)
    sample = random.sample(candidates, N_SAMPLES)
    sample.sort(key=lambda s: int(s["id"].split("_")[1]))

    out_path = os.path.join(here, "utility_eval_dataset_extended.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    print(f"Candidates disjoint from training: {len(candidates)}")
    print(f"Wrote {len(sample)} utility samples to {out_path}")


if __name__ == "__main__":
    main()
