"""
Summarize the extended MultiStruQ results and regenerate every number, table and
figure used in the paper.

Reads   experiments/<model>/results/extended/*_extended.json
Writes  <out>/summary_extended.json      all computed statistics
        <out>/numbers_extended.tex       \\R{key} values used in the paper text
        <out>/tab_*_extended.tex         tabular bodies \\input by the paper
        <out>/fig_*.pdf (+ .png)         paper figures

Tables whose inputs do not exist yet are skipped; the paper shows a red
"pending" box in their place. Files this script generated earlier are removed
from <out> first, so a stale table can never survive a rerun.

MultiStruQ has two training recipes. Results of conditions that use the adapter
carry the recipe tag in their file names (qwen_improved_multistruq_...), stock-model
results do not. --recipe picks the main recipe (the "ms" numbers); the other
recipe is reported as an ablation under keys ending in "alt" (e.g. "msalt").
"auto" uses "improved" once all three models have it, otherwise "paper".

Usage:  python analysis/summarize_extended.py --out manuscripts/generated [--recipe auto|improved|paper]
"""

import argparse
import glob
import json
import math
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (macro key, folder, display name, file prefix)
MODELS = [
    ("qwen", "qwen2.5-7b", "Qwen2.5-7B-Instruct", "qwen"),
    ("llama", "llama3.1-8b", "Llama-3.1-8B-Instruct", "llama31_8b"),
    ("mistral", "mistral-7b", "Mistral-7B-Instruct-v0.3", "mistral_7b"),
]
SHORT = {"qwen": "Qwen2.5-7B", "llama": "Llama-3.1-8B", "mistral": "Mistral-7B"}

# (macro key, file condition, label)
CORE = [("baseline", "baseline", "No defense"), ("sf", "struq", "Format only"), ("ms", "multistruq", "MultiStruQ")]
STOCK_EXTRA = [
    ("chat", "baseline_chat", "No defense (chat template)"),
    ("instructional", "instructional", "Instructional prompt"),
    ("sandwich", "sandwich", "Sandwich prompt"),
    ("spotlight", "spotlight", "Spotlighting (datamarking)"),
    ("secalign", "meta_secalign", "Meta-SecAlign-8B"),
    ("forgerysf", "forgery_struq", "Format only + forged headers"),
    ("forgerysansf", "forgery_sanitized_struq", "Format only + forged headers, sanitized"),
]
ADAPTER_EXTRA = [
    ("sanms", "sanitized_multistruq", "MultiStruQ, sanitized"),
    ("forgeryms", "forgery_multistruq", "MultiStruQ + forged headers"),
    ("forgerysanms", "forgery_sanitized_multistruq", "MultiStruQ + forged headers, sanitized"),
]
EXTRA = STOCK_EXTRA + ADAPTER_EXTRA
ADAPTER_KEYS = {"ms"} | {k for k, _, _ in ADAPTER_EXTRA}
RECIPE_TAGS = {"paper": "", "improved": "improved"}
RECIPE_NOTE = {"paper": "full-sequence loss", "improved": "response-only loss"}
# Rebuilt in main() once the alternative recipe is known: adds "<key>alt" rows for adapter conditions.
CONDS = CORE + EXTRA

# (macro key, file language, label)
LANGS = [
    ("english", "english", "English"), ("hinglish", "hinglish", "Hinglish"), ("hindi", "hindi_native", "Hindi"),
    ("cultural", "cultural", "Cultural"), ("crosslingual", "cross_lingual", "Cross-lingual"),
    ("bengali", "bengali", "Bengali"), ("tamil", "tamil", "Tamil"), ("marathi", "marathi", "Marathi"),
    ("telugu", "telugu", "Telugu"),
]
LANG_LABEL = {f: lab for _, f, lab in LANGS}


def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (100 * max(0.0, centre - half), 100 * min(1.0, centre + half))


def pct(k, n):
    return 100 * k / n if n else 0.0


def f2(x):
    return f"{x:.2f}"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def result_path(folder, prefix, condition, kind="results", tag=""):
    name = prefix + (f"_{tag}" if tag else "") + f"_{condition}_{kind}_extended.json"
    return os.path.join(REPO, "experiments", folder, "results", "extended", name)


def alt_conditions(alt):
    note = RECIPE_NOTE[alt]
    return [(f"{k}alt", f, f"{lab} ({note})") for k, f, lab in [CORE[2]] + ADAPTER_EXTRA]


def tag_for(ckey, main, alt):
    if ckey.endswith("alt"):
        return RECIPE_TAGS[alt]
    return RECIPE_TAGS[main] if ckey in ADAPTER_KEYS else ""


def pick_recipe(requested):
    if requested != "auto":
        return requested
    have = all(os.path.exists(result_path(folder, prefix, "multistruq", tag="improved")) for _, folder, _, prefix in MODELS)
    return "improved" if have else "paper"


def counts(res, key="results"):
    """Sum total/succeeded/hijacked over a results dict; hijacked is None if not recorded."""
    groups = res.get(key) or {}
    total = sum(g["total"] for g in groups.values())
    succ = sum(g["succeeded"] for g in groups.values())
    has_hr = all("hijacked" in g for g in groups.values()) and bool(groups)
    hij = sum(g["hijacked"] for g in groups.values()) if has_hr else None
    return total, succ, hij


def load_all(main, alt):
    data = {"conditions": {}, "utility": {}, "train": {}, "train_alt": {}, "tokens": {}, "tokens_alt": {}, "holdout": {}}
    for mkey, folder, _, prefix in MODELS:
        for ckey, cfile, _ in CONDS:
            tag = tag_for(ckey, main, alt)
            p = result_path(folder, prefix, cfile, tag=tag)
            if os.path.exists(p):
                data["conditions"].setdefault(mkey, {})[ckey] = load_json(p)
            p = result_path(folder, prefix, cfile, "utility", tag=tag)
            if os.path.exists(p):
                data["utility"].setdefault(mkey, {})[ckey] = load_json(p)
        for recipe, suffix in [(main, ""), (alt, "_alt")]:
            tag = RECIPE_TAGS[recipe]
            stem = prefix + (f"_{tag}" if tag else "")
            for kind, slot in [("train_log", "train"), ("token_stats", "tokens")]:
                p = os.path.join(REPO, "experiments", folder, "results", "extended", f"{stem}_{kind}_extended.json")
                if os.path.exists(p):
                    data[slot + suffix][mkey] = load_json(p)
        stem = prefix + (f"_{RECIPE_TAGS[main]}" if RECIPE_TAGS[main] else "")
        for p in glob.glob(os.path.join(REPO, "experiments", folder, "results", "extended",
                                        f"{stem}_holdout-*_multistruq_results_extended.json")):
            tag = os.path.basename(p)[len(stem) + 1:].split("_multistruq_")[0]
            data["holdout"].setdefault(mkey, {})[tag] = load_json(p)
    return data


# ---------------------------------------------------------------------------
# Statistics and macros
# ---------------------------------------------------------------------------
def compute(data):
    R = {}       # macro key -> string
    S = {"models": {}, "pooled": {}, "per_language": {}, "per_attack_type": {}}
    conds = data["conditions"]
    complete = [m for m, _, _, _ in MODELS if all(c in conds.get(m, {}) for c, _, _ in CORE)]

    def put(prefix, total, succ, hij):
        lo, hi = wilson(succ, total)
        R[f"{prefix}-asr"] = f2(pct(succ, total))
        R[f"{prefix}-k"] = str(succ)
        R[f"{prefix}-n"] = f"{total:,}".replace(",", "{,}")
        R[f"{prefix}-ci"] = f"[{f2(lo)}, {f2(hi)}]"
        if hij is not None:
            R[f"{prefix}-hr"] = f2(pct(hij, total))
            R[f"{prefix}-hk"] = str(hij)
        return {"n": total, "succeeded": succ, "asr": pct(succ, total), "ci95": [lo, hi],
                "hijacked": hij, "hijack_rate": None if hij is None else pct(hij, total)}

    # per model and pooled, every available condition
    for ckey, _, _ in CONDS:
        pooled = [0, 0, 0]
        pooled_hr_ok, n_models = True, 0
        for mkey, _, _, _ in MODELS:
            res = conds.get(mkey, {}).get(ckey)
            if not res:
                continue
            total, succ, hij = counts(res)
            S["models"].setdefault(mkey, {})[ckey] = put(f"{mkey}-{ckey}", total, succ, hij)
            if mkey in complete:
                n_models += 1
                pooled[0] += total
                pooled[1] += succ
                if hij is None:
                    pooled_hr_ok = False
                else:
                    pooled[2] += hij
        if n_models == len(complete) and complete:
            S["pooled"][ckey] = put(f"pooled-{ckey}", pooled[0], pooled[1], pooled[2] if pooled_hr_ok else None)

    # reductions
    for mkey in [m for m, _, _, _ in MODELS] + ["pooled"]:
        src = S["pooled"] if mkey == "pooled" else S["models"].get(mkey, {})
        if not all(c in src for c in ("baseline", "sf", "ms")):
            continue
        b, sf, ms = src["baseline"]["asr"], src["sf"]["asr"], src["ms"]["asr"]
        R[f"{mkey}-dabs"] = f2(b - ms)
        R[f"{mkey}-drel"] = f2(100 * (b - ms) / b) if b else "0.00"
        R[f"{mkey}-sfabs"] = f2(abs(sf - b))
        R[f"{mkey}-sfdir"] = "raises" if sf > b else "reduces"
        if src["baseline"]["hijack_rate"] is not None and src["ms"]["hijack_rate"] is not None:
            R[f"{mkey}-hrdabs"] = f2(src["baseline"]["hijack_rate"] - src["ms"]["hijack_rate"])
    if all(c in S["pooled"] for c in ("baseline", "sf", "ms")):
        b, sf, ms = (S["pooled"][c]["asr"] for c in ("baseline", "sf", "ms"))
        R["pooled-sfrecovered"] = f2(100 * (b - sf) / (b - ms)) if b != ms else "0.00"
        base = {m: S["models"][m]["baseline"]["asr"] for m in complete}
        R["baseline-min"], R["baseline-max"] = f2(min(base.values())), f2(max(base.values()))
        R["models-complete"] = str(len(complete))

    # per language (pooled over complete models) and per model
    for lkey, lfile, _ in LANGS:
        for ckey, _, _ in CONDS:
            tot = succ = hij = 0
            hr_ok, ok = True, bool(complete)
            for mkey in complete:
                res = conds[mkey].get(ckey)
                if not res or lfile not in res.get("results", {}):
                    ok = False
                    break
                g = res["results"][lfile]
                tot, succ = tot + g["total"], succ + g["succeeded"]
                if "hijacked" in g:
                    hij += g["hijacked"]
                else:
                    hr_ok = False
                R[f"{mkey}-{lkey}-{ckey}-asr"] = f2(pct(g["succeeded"], g["total"]))
            if ok:
                R[f"lang-{lkey}-{ckey}-asr"] = f2(pct(succ, tot))
                R[f"lang-{lkey}-n"] = str(tot)
                if hr_ok:
                    R[f"lang-{lkey}-{ckey}-hr"] = f2(pct(hij, tot))
                S["per_language"].setdefault(lfile, {})[ckey] = {"n": tot, "succeeded": succ, "asr": pct(succ, tot),
                                                                 "hijack_rate": pct(hij, tot) if hr_ok else None}

    # per attack type (only once the extended notebooks have recorded it)
    for ckey, _, _ in CORE:
        agg, ok = {}, bool(complete)
        for mkey in complete:
            by_type = conds[mkey][ckey].get("results_by_attack_type")
            if not by_type:
                ok = False
                break
            for t, g in by_type.items():
                a = agg.setdefault(t, {"n": 0, "succeeded": 0, "hijacked": 0})
                a["n"] += g["total"]
                a["succeeded"] += g["succeeded"]
                a["hijacked"] += g.get("hijacked", 0)
        if ok:
            for t, a in agg.items():
                S["per_attack_type"].setdefault(t, {})[ckey] = {**a, "asr": pct(a["succeeded"], a["n"]),
                                                                "hijack_rate": pct(a["hijacked"], a["n"])}

    # utility
    for mkey, per in data["utility"].items():
        for ckey, u in per.items():
            R[f"{mkey}-{ckey}-rougel"] = f"{100 * u['rouge_l_mean']:.1f}"
            if "clean_target_rate" in u:
                R[f"{mkey}-{ckey}-cleantarget"] = f2(u["clean_target_rate"])

    # training provenance ("-alt-" keys describe the alternative recipe)
    for slot, infix in [("train", ""), ("train_alt", "-alt")]:
        for mkey, log in data[slot].items():
            R[f"{mkey}{infix}-steps"] = str(log["global_step"])
            R[f"{mkey}{infix}-ntrain"] = f"{log['n_train']:,}".replace(",", "{,}")
            if "n_gpu" in log:
                R[f"{mkey}{infix}-ngpu"] = str(log["n_gpu"])
                R[f"{mkey}{infix}-effbatch"] = str(log["effective_batch"])
            if "n_dropped_no_response" in log:
                R[f"{mkey}{infix}-dropped"] = str(log["n_dropped_no_response"])

    # truncation at each recipe's max length
    for slot, infix in [("tokens", ""), ("tokens_alt", "-alt")]:
        for mkey, ts in data[slot].items():
            per = ts["per_language"]
            n_all = sum(v["n"] for v in per.values())
            R[f"{mkey}{infix}-maxlen"] = str(ts["max_length"])
            R[f"{mkey}{infix}-trunc-all"] = f"{sum(v['n'] * v['pct_truncated'] for v in per.values()) / n_all:.1f}"
            for lkey, lfile, _ in LANGS + [("clean", "clean", "Clean")]:
                if lfile in per:
                    R[f"{mkey}{infix}-trunc-{lkey}"] = f"{per[lfile]['pct_truncated']:.1f}"
                    R[f"{mkey}{infix}-noresp-{lkey}"] = f"{per[lfile]['pct_prompt_overflow']:.1f}"

    # held-out languages
    for mkey, tags in data["holdout"].items():
        for tag, res in tags.items():
            for lkey, lfile, _ in LANGS:
                g = res["results"].get(lfile)
                if g:
                    R[f"holdout-{mkey}-{lkey}-asr"] = f2(pct(g["succeeded"], g["total"]))
            total, succ, _ = counts(res)
            R[f"holdout-{mkey}-asr"] = f2(pct(succ, total))
            S.setdefault("holdout", {}).setdefault(mkey, {})[tag] = {"n": total, "succeeded": succ, "asr": pct(succ, total)}

    S["complete_models"] = complete
    return R, S


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------
def write_macros(R, out):
    lines = ["% Generated by analysis/summarize_extended.py -- do not edit by hand."]
    for k in sorted(R):
        lines.append(f"\\expandafter\\def\\csname msq@{k}\\endcsname{{{R[k]}}}")
    with open(os.path.join(out, "numbers_extended.tex"), "w") as f:
        f.write("\n".join(lines) + "\n")


def write(out, name, body):
    with open(os.path.join(out, name), "w") as f:
        f.write("% Generated by analysis/summarize_extended.py -- do not edit by hand.\n" + body)


def tab_main(S, out):
    if not S["pooled"]:
        return
    rows = ["\\begin{tabular}{@{}llrrr@{}}", "\\toprule",
            "Model & Condition & ASR (\\%) & 95\\% CI & HR (\\%) \\\\", "\\midrule"]
    blocks = [(m, name, S["models"][m]) for m, _, name, _ in MODELS if m in S["complete_models"]]
    blocks.append(("pooled", "\\textbf{Pooled}", S["pooled"]))
    for i, (mkey, name, src) in enumerate(blocks):
        for j, (ckey, _, label) in enumerate(CORE):
            st = src[ckey]
            asr = f2(st["asr"])
            if ckey == "ms":
                asr = f"\\textbf{{{asr}}}"
            hr = "\\pend" if st["hijack_rate"] is None else f2(st["hijack_rate"])
            lead = f"\\multirow{{3}}{{*}}{{{name}}}" if j == 0 else ""
            rows.append(f"{lead} & {label} & {asr} ({st['succeeded']}/{st['n']}) & "
                        f"[{f2(st['ci95'][0])}, {f2(st['ci95'][1])}] & {hr} \\\\")
        rows.append("\\bottomrule" if i == len(blocks) - 1 else "\\midrule")
    rows.append("\\end{tabular}")
    write(out, "tab_main_extended.tex", "\n".join(rows) + "\n")


def tab_perlang(S, out):
    per = S["per_language"]
    if not all(all(c in per.get(l, {}) for c, _, _ in CORE) for _, l, _ in LANGS):
        return
    order = sorted(per, key=lambda l: -per[l]["baseline"]["asr"])
    rows = ["\\begin{tabular}{@{}lrrrr@{}}", "\\toprule",
            "Category & $n$ & No defense & Format only & MultiStruQ \\\\", "\\midrule"]
    for l in order:
        ms = f2(per[l]["ms"]["asr"])
        if per[l]["ms"]["succeeded"] == 0:
            ms = f"\\textbf{{{ms}}}"
        rows.append(f"{LANG_LABEL[l]} & {per[l]['baseline']['n']} & {f2(per[l]['baseline']['asr'])} & "
                    f"{f2(per[l]['sf']['asr'])} & {ms} \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_perlang_extended.tex", "\n".join(rows) + "\n")


def tab_attacktype(S, out):
    per = S["per_attack_type"]
    if not per or not all(all(c in v for c, _, _ in CORE) for v in per.values()):
        return
    order = sorted(per, key=lambda t: -per[t]["baseline"]["asr"])
    rows = ["\\begin{tabular}{@{}lrrrrr@{}}", "\\toprule",
            "Strategy & $n$ & No def. & SF & \\multicolumn{2}{c}{MultiStruQ} \\\\",
            "\\cmidrule(l){5-6}", " & & ASR & ASR & ASR & HR \\\\", "\\midrule"]
    for t in order:
        v = per[t]
        rows.append(f"{t.replace('_', ' ')} & {v['baseline']['n']} & {f2(v['baseline']['asr'])} & "
                    f"{f2(v['sf']['asr'])} & {f2(v['ms']['asr'])} & {f2(v['ms']['hijack_rate'])} \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_attacktype_extended.tex", "\n".join(rows) + "\n")


EXTRAS_ORDER = ["baseline", "sf", "ms", "msalt", "chat", "instructional", "sandwich", "spotlight", "secalign", "|",
                "sanms", "sanmsalt", "forgerysf", "forgerysansf", "forgeryms", "forgerysanms", "forgerymsalt",
                "forgerysanmsalt"]


def tab_extras(S, out):
    labels = {c: lab for c, _, lab in CONDS}
    present = lambda c: any(c in S["models"].get(m, {}) for m, _, _, _ in MODELS)
    if not any(present(c) for c, _, _ in EXTRA):
        return
    rows = ["\\begin{tabular}{@{}lccc@{}}", "\\toprule",
            "Condition & " + " & ".join(SHORT[m] for m, _, _, _ in MODELS) + " \\\\", "\\midrule"]

    def cell(m, c):
        st = S["models"].get(m, {}).get(c)
        if not st:
            return "--"
        hr = "" if st["hijack_rate"] is None else f" / {f2(st['hijack_rate'])}"
        return f"{f2(st['asr'])}{hr}"

    for c in EXTRAS_ORDER:
        if c == "|":
            rows.append("\\midrule")
        elif present(c):
            rows.append(f"{labels[c]} & " + " & ".join(cell(m, c) for m, _, _, _ in MODELS) + " \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_extras_extended.tex", "\n".join(rows) + "\n")


def tab_utility(data, out):
    util = data["utility"]
    if not util:
        return
    rows = ["\\begin{tabular}{@{}llrr@{}}", "\\toprule",
            "Model & Condition & ROUGE-L & Clean-input target (\\%) \\\\", "\\midrule"]
    labels = {c: lab for c, _, lab in CONDS}
    blocks = [(m, name) for m, _, name, _ in MODELS if m in util]
    for i, (m, name) in enumerate(blocks):
        conds = [c for c, _, _ in CONDS if c in util[m]]
        for j, c in enumerate(conds):
            u = util[m][c]
            lead = f"\\multirow{{{len(conds)}}}{{*}}{{{name}}}" if j == 0 else ""
            clean = f2(u["clean_target_rate"]) if "clean_target_rate" in u else "--"
            rows.append(f"{lead} & {labels[c]} & {100 * u['rouge_l_mean']:.1f} & {clean} \\\\")
        rows.append("\\bottomrule" if i == len(blocks) - 1 else "\\midrule")
    rows.append("\\end{tabular}")
    write(out, "tab_utility_extended.tex", "\n".join(rows) + "\n")


def tab_tokens(data, out):
    """% of training sequences truncated, one column group per max length (128 and/or 256 tokens)."""
    groups = {}
    for slot in ("tokens", "tokens_alt"):
        for m, _, _, _ in MODELS:
            ts = data[slot].get(m)
            if ts:
                groups.setdefault(ts["max_length"], {})[m] = ts["per_language"]
    if not groups:
        return
    cols = [(L, m) for L in sorted(groups) for m, _, _, _ in MODELS if m in groups[L]]
    rows = ["\\begin{tabular}{@{}l" + "r" * len(cols) + "@{}}", "\\toprule"]
    head, rules, start = ["Max. length"], [], 2
    for L in sorted(groups):
        n = sum(1 for c in cols if c[0] == L)
        head.append(f"\\multicolumn{{{n}}}{{c}}{{{L} tokens}}")
        rules.append(f"\\cmidrule(lr){{{start}-{start + n - 1}}}")
        start += n
    rows += [" & ".join(head) + " \\\\", " ".join(rules),
             "Category & " + " & ".join(SHORT[m].split("-")[0] for _, m in cols) + " \\\\", "\\midrule"]
    for _, lfile, lab in [("clean", "clean", "Clean")] + LANGS:
        vals = [groups[L][m].get(lfile) for L, m in cols]
        if any(v is None for v in vals):
            continue
        rows.append(f"{lab} & " + " & ".join(f"{v['pct_truncated']:.1f}" for v in vals) + " \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_tokens_extended.tex", "\n".join(rows) + "\n")


# ---------------------------------------------------------------------------
# Figures (static, print-bound: validated 3-slot categorical palette + hatching
# for grayscale, direct value labels as contrast relief)
# ---------------------------------------------------------------------------
COND_COLORS = {"baseline": "#2a78d6", "sf": "#eb6834", "ms": "#1baf7a"}
COND_HATCH = {"baseline": "", "sf": "////", "ms": "...."}
MODEL_COLORS = {"qwen": "#2a78d6", "llama": "#eb6834", "mistral": "#1baf7a"}
MODEL_MARKERS = {"qwen": "o", "llama": "s", "mistral": "^"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def _style(plt):
    plt.rcParams.update({
        "font.family": "serif", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.axisbelow": True, "legend.frameon": False, "hatch.linewidth": 0.5,
        "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.dpi": 300,
    })


def _save(fig, out, name):
    fig.savefig(os.path.join(out, f"{name}.pdf"))
    fig.savefig(os.path.join(out, f"{name}.png"))


def figures(S, data, out):
    if not S["pooled"]:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    _style(plt)
    models = S["complete_models"]
    labels = {c: lab for c, _, lab in CORE}

    # fig_overall: grouped bars per model
    fig, ax = plt.subplots(figsize=(3.45, 2.2))
    x, w = np.arange(len(models)), 0.26
    for i, (c, _, _) in enumerate(CORE):
        vals = [S["models"][m][c]["asr"] for m in models]
        bars = ax.bar(x + (i - 1) * w, vals, w - 0.03, color=COND_COLORS[c], hatch=COND_HATCH[c],
                      edgecolor="white", linewidth=0.4, label=labels[c])
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.2f}", ha="center", va="bottom", fontsize=5.5, color=INK)
    ax.set_xticks(x, [SHORT[m] for m in models])
    ax.set_ylabel("Attack success rate (%)")
    ax.set_ylim(0, max(S["models"][m][c]["asr"] for m in models for c, _, _ in CORE) * 1.18)
    ax.legend(ncol=3, fontsize=6.5, loc="upper right", bbox_to_anchor=(1, 1.13))
    _save(fig, out, "fig_overall")
    plt.close(fig)

    # fig_progression: one line per model across conditions, mean dashed
    fig, ax = plt.subplots(figsize=(3.45, 2.1))
    xs = np.arange(3)
    for m in models:
        ys = [S["models"][m][c]["asr"] for c, _, _ in CORE]
        ax.plot(xs, ys, color=MODEL_COLORS[m], marker=MODEL_MARKERS[m], markersize=4, linewidth=1.5, label=SHORT[m])
    mean = [np.mean([S["models"][m][c]["asr"] for m in models]) for c, _, _ in CORE]
    ax.plot(xs, mean, color=MUTED, linestyle="--", marker="D", markersize=3.5, linewidth=1.2, label="Mean")
    ax.set_xticks(xs, [labels[c] for c, _, _ in CORE])
    ax.set_ylabel("Attack success rate (%)")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=6.5, loc="upper right")
    _save(fig, out, "fig_progression")
    plt.close(fig)

    # fig_heatmap: language x model per condition (single-hue sequential ramp)
    langs = [l for _, l, _ in LANGS]
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 1.75), sharey=True)
    for ax, (c, _, _) in zip(axes, CORE):
        res = {m: data["conditions"][m][c]["results"] for m in models}
        grid = np.array([[pct(res[m][l]["succeeded"], res[m][l]["total"]) for l in langs] for m in models])
        im = ax.imshow(grid, cmap="Blues", vmin=0, vmax=100, aspect="auto")
        for i in range(len(models)):
            for j in range(len(langs)):
                v = grid[i, j]
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=5.5, color="white" if v > 55 else INK)
        ax.set_title(labels[c], fontsize=7.5)
        ax.set_xticks(range(len(langs)), [LANG_LABEL[l] for l in langs], rotation=60, ha="right", fontsize=6)
        ax.set_yticks(range(len(models)), [SHORT[m] for m in models], fontsize=6.5)
        ax.grid(False)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    cbar = fig.colorbar(im, ax=axes, fraction=0.015, pad=0.01)
    cbar.set_label("ASR (%)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)
    _save(fig, out, "fig_heatmap")
    plt.close(fig)

    # fig_perlang: pooled per language, ordered by baseline
    per = S["per_language"]
    order = sorted(per, key=lambda l: -per[l]["baseline"]["asr"])
    fig, ax = plt.subplots(figsize=(3.45, 2.2))
    x, w = np.arange(len(order)), 0.27
    for i, (c, _, _) in enumerate(CORE):
        ax.bar(x + (i - 1) * w, [per[l][c]["asr"] for l in order], w - 0.03, color=COND_COLORS[c],
               hatch=COND_HATCH[c], edgecolor="white", linewidth=0.4, label=labels[c])
    ax.set_xticks(x, [f"{LANG_LABEL[l]} ({per[l]['baseline']['n']})" for l in order], fontsize=6,
                  rotation=40, ha="right", rotation_mode="anchor")
    ax.set_ylabel("Pooled ASR (%)")
    ax.legend(ncol=3, fontsize=6.5, loc="upper right", bbox_to_anchor=(1, 1.13))
    _save(fig, out, "fig_perlang")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(REPO, "analysis", "output_extended"))
    ap.add_argument("--recipe", choices=["auto", "improved", "paper"], default="auto",
                    help="training recipe reported as the main MultiStruQ result")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for pattern in ["numbers_extended.tex", "tab_*_extended.tex", "fig_*.pdf", "fig_*.png", "summary_extended.json"]:
        for stale in glob.glob(os.path.join(args.out, pattern)):
            os.remove(stale)

    main_recipe = pick_recipe(args.recipe)
    alt_recipe = "paper" if main_recipe == "improved" else "improved"
    CONDS[:] = CORE + EXTRA + alt_conditions(alt_recipe)

    data = load_all(main_recipe, alt_recipe)
    R, S = compute(data)
    R["main-recipe"] = main_recipe
    S["main_recipe"] = main_recipe

    write_macros(R, args.out)
    tab_main(S, args.out)
    tab_perlang(S, args.out)
    tab_attacktype(S, args.out)
    tab_extras(S, args.out)
    tab_utility(data, args.out)
    tab_tokens(data, args.out)
    figures(S, data, args.out)
    with open(os.path.join(args.out, "summary_extended.json"), "w") as f:
        json.dump({"stats": S, "numbers": R}, f, indent=2)

    print(f"Main MultiStruQ recipe: {main_recipe} ({RECIPE_NOTE[main_recipe]}); "
          f"'{alt_recipe}' rows are reported with an 'alt' suffix")
    print(f"Models with all three core conditions: {', '.join(S['complete_models']) or 'none'}")
    for c, _, lab in CONDS:
        if c in S["pooled"]:
            p = S["pooled"][c]
            hr = "" if p["hijack_rate"] is None else f"  HR {p['hijack_rate']:.2f}%"
            print(f"  pooled {lab:30} ASR {p['asr']:6.2f}% ({p['succeeded']}/{p['n']}){hr}")
    print(f"Wrote {len(R)} numbers and tables/figures to {args.out}")


if __name__ == "__main__":
    main()
