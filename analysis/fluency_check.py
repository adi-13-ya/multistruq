"""
Native-speaker check of the Indic attack texts: rating sheets and their scoring.

    python analysis/fluency_check.py make     writes datasets/fluency_check/<language>.csv
    python analysis/fluency_check.py score    reads the filled sheets, writes
                                              analysis/fluency_check_extended.json
                                              (read by summarize_extended.py)

Each sheet lists distinct attack texts of both evaluation corpora. Native-script languages are rated
in full; romanized and cross-lingual attacks are sampled with a fixed seed. Two native speakers fill
the rater columns independently, without seeing each other's ratings:

    fluency   3 = natural, as a native speaker would write it
              2 = understandable but awkward or partly unnatural
              1 = wrong or hard to understand
    intent    1 = clearly tells the reader to output the target word, 0 = it does not

Scoring reports the mean fluency, the share rated 3 and 1, the intent rate, raw agreement and
quadratic-weighted Cohen's kappa per language. Rows with a missing rating are skipped.
"""

import csv
import json
import os
import random
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.path.join(REPO, "datasets", "fluency_check")
OUT = os.path.join(REPO, "analysis", "fluency_check_extended.json")
CORPORA = {"template": "multilingual_eval_dataset_v3.json", "unseen": "multilingual_eval_dataset_ood.json"}

# sheet -> (dataset languages, number of texts to sample; None = all)
PLAN = {
    "hindi": (["hindi_native"], None),
    "bengali": (["bengali"], None),
    "marathi": (["marathi"], None),
    "tamil": (["tamil"], None),
    "telugu": (["telugu"], None),
    "hinglish": (["hinglish", "cultural"], 40),
    "crosslingual": (["cross_lingual"], 20),
}
COLUMNS = ["id", "language", "corpus", "attack_text", "fluency_rater1", "fluency_rater2",
           "intent_rater1", "intent_rater2", "comment"]


def distinct_attacks():
    rows, seen = [], set()
    for corpus, fname in CORPORA.items():
        with open(os.path.join(REPO, "datasets", fname), encoding="utf-8") as f:
            for s in json.load(f):
                key = (s["language"], s["attack_text"])
                if key not in seen:
                    seen.add(key)
                    rows.append({"language": s["language"], "corpus": corpus, "attack_text": s["attack_text"]})
    return rows


def make():
    os.makedirs(SHEETS, exist_ok=True)
    attacks = distinct_attacks()
    rng = random.Random(42)
    for sheet, (langs, k) in PLAN.items():
        items = [a for a in attacks if a["language"] in langs]
        if k is not None and len(items) > k:
            items = rng.sample(items, k)
        path = os.path.join(SHEETS, f"{sheet}.csv")
        if os.path.exists(path):
            print(f"kept {path} (already exists; delete it to regenerate)")
            continue
        # utf-8-sig so Excel shows Indic scripts correctly
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            for i, a in enumerate(items, 1):
                w.writerow({"id": f"{sheet}-{i:03d}", **a})
        print(f"wrote {path} ({len(items)} texts)")


def weighted_kappa(pairs, cats=(1, 2, 3)):
    """Quadratic-weighted Cohen's kappa for two raters."""
    n = len(pairs)
    if n == 0:
        return None
    k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    obs = [[0.0] * k for _ in range(k)]
    for a, b in pairs:
        obs[idx[a]][idx[b]] += 1
    ra = [sum(row) for row in obs]
    rb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    w = [[(i - j) ** 2 / (k - 1) ** 2 for j in range(k)] for i in range(k)]
    num = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    den = sum(w[i][j] * ra[i] * rb[j] / n for i in range(k) for j in range(k))
    return 1 - num / den if den else 1.0


def score():
    out = {"scale": "fluency 1-3, intent 0/1, two raters", "per_sheet": {}}
    all_ratings, all_intent = [], []
    for sheet in PLAN:
        path = os.path.join(SHEETS, f"{sheet}.csv")
        if not os.path.exists(path):
            continue
        pairs, ratings, intent = [], [], []
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                f1, f2 = r["fluency_rater1"].strip(), r["fluency_rater2"].strip()
                if f1 and f2:
                    pairs.append((int(f1), int(f2)))
                    ratings += [int(f1), int(f2)]
                for col in ("intent_rater1", "intent_rater2"):
                    if r[col].strip():
                        intent.append(int(r[col]))
        if not pairs:
            continue
        out["per_sheet"][sheet] = {
            "n_texts": len(pairs),
            "fluency_mean": sum(ratings) / len(ratings),
            "pct_natural": 100 * ratings.count(3) / len(ratings),
            "pct_wrong": 100 * ratings.count(1) / len(ratings),
            "intent_rate": 100 * sum(intent) / len(intent) if intent else None,
            "exact_agreement": 100 * sum(a == b for a, b in pairs) / len(pairs),
            "kappa_quadratic": weighted_kappa(pairs),
        }
        all_ratings += ratings
        all_intent += intent
    if all_ratings:
        out["overall"] = {"n_texts": sum(v["n_texts"] for v in out["per_sheet"].values()),
                          "fluency_mean": sum(all_ratings) / len(all_ratings),
                          "pct_natural": 100 * all_ratings.count(3) / len(all_ratings),
                          "intent_rate": 100 * sum(all_intent) / len(all_intent) if all_intent else None}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    for sheet, v in out["per_sheet"].items():
        print(f"{sheet:13} n={v['n_texts']:3}  fluency {v['fluency_mean']:.2f}  natural {v['pct_natural']:.0f}%  "
              f"agreement {v['exact_agreement']:.0f}%  kappa {v['kappa_quadratic']:.2f}")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    {"make": make, "score": score}[sys.argv[1] if len(sys.argv) > 1 else "make"]()
