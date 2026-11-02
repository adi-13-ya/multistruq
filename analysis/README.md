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
