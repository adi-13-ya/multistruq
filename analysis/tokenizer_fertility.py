"""
Measure how finely each model's tokenizer splits the injected attack text, per language category.

Reads   datasets/multilingual_eval_dataset_v3.json, datasets/multilingual_eval_dataset_ood.json
Writes  analysis/tokenizer_fertility_extended.json  (read by summarize_extended.py)

For every distinct attack text in the two evaluation corpora we count characters (excluding
whitespace), whitespace-separated words and tokens, and report per language category:

    tokens per character   tokens / non-whitespace characters
    tokens per word        tokens / words (the usual "fertility")

Only the tokenizer files are downloaded, not the model weights. Llama-3.1 is gated; when no
Hugging Face token is available the identical tokenizer of an ungated mirror is used and the
source actually read is recorded in the output.

Usage:  pip install tokenizers huggingface_hub
        python analysis/tokenizer_fertility.py
"""

import json
import os

from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "analysis", "tokenizer_fertility_extended.json")
CORPORA = {"template": "multilingual_eval_dataset_v3.json", "unseen": "multilingual_eval_dataset_ood.json"}

# macro key -> (official repo, ungated mirror with the same tokenizer)
TOKENIZERS = {
    "qwen": ("Qwen/Qwen2.5-7B-Instruct", None),
    "llama": ("meta-llama/Llama-3.1-8B-Instruct", "unsloth/Meta-Llama-3.1-8B-Instruct"),
    "mistral": ("mistralai/Mistral-7B-Instruct-v0.3", "unsloth/mistral-7b-instruct-v0.3"),
}


def load_tokenizer(official, mirror):
    for repo in [official] + ([mirror] if mirror else []):
        try:
            return Tokenizer.from_file(hf_hub_download(repo, "tokenizer.json")), repo
        except Exception as e:  # gated or offline: try the mirror
            last = e
    raise last


def attack_texts():
    """Distinct attack texts per language category, over both corpora."""
    texts = {}
    for name, fname in CORPORA.items():
        with open(os.path.join(REPO, "datasets", fname), encoding="utf-8") as f:
            for s in json.load(f):
                texts.setdefault(s["language"], set()).add(s["attack_text"])
    return {lang: sorted(t) for lang, t in texts.items()}


def main():
    texts = attack_texts()
    out = {"corpora": list(CORPORA.values()), "n_texts": {l: len(t) for l, t in texts.items()},
           "tokenizers": {}, "per_language": {}}
    for mkey, (official, mirror) in TOKENIZERS.items():
        tok, source = load_tokenizer(official, mirror)
        out["tokenizers"][mkey] = {"model": official, "tokenizer_source": source}
        for lang, items in texts.items():
            chars = sum(len("".join(t.split())) for t in items)
            words = sum(len(t.split()) for t in items)
            tokens = sum(len(tok.encode(t, add_special_tokens=False).ids) for t in items)
            out["per_language"].setdefault(lang, {})[mkey] = {
                "tokens": tokens, "chars": chars, "words": words,
                "tokens_per_char": tokens / chars, "tokens_per_word": tokens / words,
            }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    for lang, per in out["per_language"].items():
        print(f"{lang:14} " + "  ".join(f"{m}: {v['tokens_per_char']:.2f} tok/char {v['tokens_per_word']:.2f} tok/word"
                                        for m, v in per.items()))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
