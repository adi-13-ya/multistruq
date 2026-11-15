# Analysis

`summarize_extended.py` reads every `experiments/<model>/results/extended/*_extended.json` file and writes:

| Output | Content |
|---|---|
| `summary_extended.json` | all computed statistics (ASR, HR, Wilson intervals, per-language, per-strategy, utility) |
| `numbers_extended.tex` | `\R{key}` values used in the paper text, e.g. `\R{pooled-ms-asr}` |
| `tab_*_extended.tex` | tabular bodies for the main, per-language, per-strategy, comparison, utility and truncation tables |
| `fig_*.pdf`, `fig_*.png` | the four paper figures |

```bash
pip install matplotlib numpy
python analysis/summarize_extended.py                          # -> analysis/output_extended/
python analysis/summarize_extended.py --out <paper>/generated  # straight into the manuscript folder
python analysis/summarize_extended.py --recipe paper           # force the main recipe (default: auto)
```

The main MultiStruQ result comes from the `improved` training recipe once all three models have it (`--recipe auto`); the other recipe's rows get an `alt` suffix, e.g. `\R{pooled-msalt-asr}`. Files the script generated earlier are deleted from the output folder first.

A table is only written once its inputs exist. For example, the per-strategy table appears after the
extended evaluation notebooks have recorded per-attack-type counts. Macro keys follow
`<model>-<condition>-<stat>`, with model `qwen | llama | mistral | pooled` and condition
`baseline | sf | ms | sanms | chat | instructional | sandwich | spotlight | secalign | forgerysf | forgerysansf | forgeryms | forgerysanms`, plus `msalt`, `sanmsalt`, `forgerymsalt`, `forgerysanmsalt` for the other recipe.

Unseen-attack results (`RUN_MODE = "ood"`) use the conditions `oodbaseline | oodsf | oodsandwich | oodms | oodforgeryms`
(e.g. `\R{pooled-oodms-asr}`, `\R{pooled-ood-dabs}`) and add `tab_ood_extended.tex` (per model) and
`tab_oodtype_extended.tex` (per attack family, keys `oodtype-<family>-<condition>-asr`).

## Language groups and tokenizer fertility

`tokenizer_fertility.py` tokenizes every distinct attack text of the two evaluation corpora with each
model's tokenizer (only the tokenizer files are downloaded) and writes `tokenizer_fertility_extended.json`:
tokens per character and tokens per word, per language category. Llama-3.1 is gated, so without a
Hugging Face token the identical tokenizer of an ungated mirror is used; the file records the source.

```bash
pip install tokenizers huggingface_hub
python analysis/tokenizer_fertility.py
```

`summarize_extended.py` reads that file when it exists and adds:

- `tab_fertility_extended.tex`: tokens per word per model next to pooled no-defense ASR, with the Spearman
  correlation between each model's fertility and its own per-category ASR (keys `tpw-<model>-<lang>`,
  `tpwratio-<model>-<lang>` relative to English, `rho-<model|pooled>-<condition>`).
- `tab_groups_extended.tex`: pooled ASR with Wilson intervals for language groups (English, romanized
  Hinglish, native-script Indic split into Hindi and the other four, cross-lingual), keys
  `grp-<group>-<condition>-asr` and `-ci`.

## Native-speaker check

`fluency_check.py make` writes rating sheets to `datasets/fluency_check/` (all distinct native-script
attacks, 40 sampled romanized and 20 cross-lingual ones). Two native speakers per language fill
`fluency_rater1/2` (1–3) and `intent_rater1/2` (0/1) independently. Then:

```bash
python analysis/fluency_check.py score             # -> analysis/fluency_check_extended.json
python analysis/summarize_extended.py --out manuscripts/generated
```

adds `tab_fluency_extended.tex` and the `fluency-*` keys; the paper's native-speaker subsection
appears only once these exist.
