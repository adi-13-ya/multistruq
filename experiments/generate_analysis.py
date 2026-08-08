"""
MultiStruQ Comprehensive Analysis & Visualization
Generates all charts, tables, and analysis for the research paper.
"""

import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ============================================================
# Configuration
# ============================================================
EXPERIMENTS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(EXPERIMENTS_DIR, "analysis_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODELS = {
    "Qwen2.5-7B": "qwen2.5-7b",
    "Llama-3.1-8B": "llama3.1-8b",
    "Mistral-7B": "mistral-7b",
}

LANGUAGES = ["english", "hindi_native", "hinglish", "bengali", "tamil", "marathi", "telugu", "cross_lingual", "cultural"]
LANG_LABELS = {
    "english": "English",
    "hindi_native": "Hindi",
    "hinglish": "Hinglish",
    "bengali": "Bengali",
    "tamil": "Tamil",
    "marathi": "Marathi",
    "telugu": "Telugu",
    "cross_lingual": "Cross-lingual",
    "cultural": "Cultural",
}

DEFENSE_COLORS = {
    "baseline": "#e74c3c",
    "struq": "#f39c12",
    "multistruq": "#27ae60",
}

MODEL_COLORS = {
    "Qwen2.5-7B": "#3498db",
    "Llama-3.1-8B": "#e74c3c",
    "Mistral-7B": "#2ecc71",
}

# ============================================================
# Load all results
# ============================================================
def load_results():
    data = {}
    file_map = {
        "qwen2.5-7b": {
            "baseline": "qwen_baseline_results_extended.json",
            "struq": "qwen_struq_results_extended.json",
            "multistruq": "qwen_multistruq_results_extended.json",
        },
        "llama3.1-8b": {
            "baseline": "llama31_8b_baseline_results_extended.json",
            "struq": "llama31_8b_struq_results_extended.json",
            "multistruq": "llama31_8b_multistruq_results_extended.json",
        },
        "mistral-7b": {
            "baseline": "mistral_7b_baseline_results_extended.json",
            "struq": "mistral_7b_struq_results_extended.json",
            "multistruq": "mistral_7b_multistruq_results_extended.json",
        },
    }

    for model_name, model_dir in MODELS.items():
        data[model_name] = {}
        for defense, filename in file_map[model_dir].items():
            filepath = os.path.join(EXPERIMENTS_DIR, model_dir, "results", "extended", filename)
            with open(filepath) as f:
                data[model_name][defense] = json.load(f)
    return data


def get_asr(result, lang):
    """Get ASR for a specific language."""
    r = result["results"].get(lang, {"total": 0, "succeeded": 0})
    if r["total"] == 0:
        return 0.0
    return r["succeeded"] / r["total"] * 100


def get_overall_asr(result):
    """Get overall ASR."""
    return result.get("overall_asr", 0.0)


# ============================================================
# FIGURE 1: Overall ASR Comparison (Grouped Bar Chart)
# ============================================================
def fig1_overall_comparison(data):
    fig, ax = plt.subplots(figsize=(10, 6))

    models = list(MODELS.keys())
    defenses = ["baseline", "struq", "multistruq"]
    defense_labels = ["Baseline", "StruQ", "MultiStruQ"]

    x = np.arange(len(models))
    width = 0.25

    for i, (defense, label) in enumerate(zip(defenses, defense_labels)):
        values = [get_overall_asr(data[m][defense]) for m in models]
        bars = ax.bar(x + i * width, values, width, label=label, color=DEFENSE_COLORS[defense], edgecolor='white', linewidth=0.5)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.8,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Attack Success Rate (ASR %)', fontsize=12)
    ax.set_title('Overall Attack Success Rate Across Models and Defenses', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(models, fontsize=11)
    ax.legend(fontsize=11)
    ax.set_ylim(0, max([get_overall_asr(data[m]["baseline"]) for m in models]) * 1.25)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_overall_asr_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 1: Overall ASR Comparison saved")


# ============================================================
# FIGURE 2: Per-Language ASR Heatmap (3 models × 9 languages × 3 defenses)
# ============================================================
def fig2_heatmap(data):
    fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharey=True)

    defenses = ["baseline", "struq", "multistruq"]
    defense_labels = ["Baseline (No Defense)", "StruQ Format Only", "MultiStruQ (Trained)"]

    for idx, (defense, title) in enumerate(zip(defenses, defense_labels)):
        ax = axes[idx]
        models = list(MODELS.keys())
        matrix = []
        for model in models:
            row = [get_asr(data[model][defense], lang) for lang in LANGUAGES]
            matrix.append(row)

        matrix = np.array(matrix)
        im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)

        ax.set_xticks(np.arange(len(LANGUAGES)))
        ax.set_xticklabels([LANG_LABELS[l] for l in LANGUAGES], rotation=45, ha='right', fontsize=9)
        ax.set_yticks(np.arange(len(models)))
        ax.set_yticklabels(models, fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')

        for i in range(len(models)):
            for j in range(len(LANGUAGES)):
                val = matrix[i, j]
                color = 'white' if val > 50 else 'black'
                ax.text(j, i, f'{val:.0f}%', ha='center', va='center', color=color, fontsize=8, fontweight='bold')

    fig.colorbar(im, ax=axes, shrink=0.6, label='ASR (%)')
    fig.suptitle('Attack Success Rate by Language, Model, and Defense', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_asr_heatmap.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 2: ASR Heatmap saved")


# ============================================================
# FIGURE 3: Per-Model Defense Comparison (3 subplots)
# ============================================================
def fig3_per_model(data):
    fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharey=True)

    models = list(MODELS.keys())
    defenses = ["baseline", "struq", "multistruq"]
    defense_labels = ["Baseline", "StruQ", "MultiStruQ"]

    for idx, model in enumerate(models):
        ax = axes[idx]
        x = np.arange(len(LANGUAGES))
        width = 0.25

        for i, (defense, label) in enumerate(zip(defenses, defense_labels)):
            values = [get_asr(data[model][defense], lang) for lang in LANGUAGES]
            ax.bar(x + i * width, values, width, label=label, color=DEFENSE_COLORS[defense], edgecolor='white', linewidth=0.5)

        ax.set_xlabel('Language', fontsize=10)
        if idx == 0:
            ax.set_ylabel('ASR (%)', fontsize=11)
        ax.set_title(model, fontsize=12, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels([LANG_LABELS[l] for l in LANGUAGES], rotation=45, ha='right', fontsize=8)
        ax.legend(fontsize=8, loc='upper right')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    fig.suptitle('Per-Language ASR: Baseline vs StruQ vs MultiStruQ', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig3_per_model_defense_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 3: Per-Model Defense Comparison saved")


# ============================================================
# FIGURE 4: ASR Reduction (Improvement) Chart
# ============================================================
def fig4_asr_reduction(data):
    fig, ax = plt.subplots(figsize=(12, 6))

    models = list(MODELS.keys())
    x = np.arange(len(LANGUAGES))
    width = 0.25

    for idx, model in enumerate(models):
        reductions = []
        for lang in LANGUAGES:
            baseline_asr = get_asr(data[model]["baseline"], lang)
            multistruq_asr = get_asr(data[model]["multistruq"], lang)
            reduction = baseline_asr - multistruq_asr
            reductions.append(reduction)

        ax.bar(x + idx * width, reductions, width, label=model, color=MODEL_COLORS[model], edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Language', fontsize=12)
    ax.set_ylabel('ASR Reduction (percentage points)', fontsize=12)
    ax.set_title('MultiStruQ ASR Reduction from Baseline (Higher = Better Defense)', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels([LANG_LABELS[l] for l in LANGUAGES], rotation=45, ha='right', fontsize=10)
    ax.legend(fontsize=11)
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig4_asr_reduction.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 4: ASR Reduction Chart saved")


# ============================================================
# FIGURE 5: Radar/Spider Chart - Per Language Vulnerability Profile
# ============================================================
def fig5_radar_chart(data):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw=dict(polar=True))

    defenses = ["baseline", "struq", "multistruq"]
    defense_labels = ["Baseline", "StruQ", "MultiStruQ"]

    angles = np.linspace(0, 2 * np.pi, len(LANGUAGES), endpoint=False).tolist()
    angles += angles[:1]

    for idx, model in enumerate(MODELS.keys()):
        ax = axes[idx]

        for defense, label in zip(defenses, defense_labels):
            values = [get_asr(data[model][defense], lang) for lang in LANGUAGES]
            values += values[:1]
            ax.plot(angles, values, 'o-', linewidth=2, label=label, color=DEFENSE_COLORS[defense])
            ax.fill(angles, values, alpha=0.1, color=DEFENSE_COLORS[defense])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([LANG_LABELS[l] for l in LANGUAGES], fontsize=7)
        ax.set_ylim(0, 100)
        ax.set_title(model, fontsize=12, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)

    fig.suptitle('Language Vulnerability Profile by Defense Type', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig5_radar_vulnerability.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 5: Radar Vulnerability Chart saved")


# ============================================================
# FIGURE 6: Defense Effectiveness by Language Category
# ============================================================
def fig6_language_categories(data):
    categories = {
        "High-Resource\n(English)": ["english"],
        "Native Indic\n(Hindi, Bengali,\nTamil, Marathi, Telugu)": ["hindi_native", "bengali", "tamil", "marathi", "telugu"],
        "Code-Mixed\n(Hinglish)": ["hinglish"],
        "Cross-lingual\n& Cultural": ["cross_lingual", "cultural"],
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    defenses = ["baseline", "struq", "multistruq"]
    defense_labels = ["Baseline", "StruQ", "MultiStruQ"]

    for idx, model in enumerate(MODELS.keys()):
        ax = axes[idx]
        x = np.arange(len(categories))
        width = 0.25

        for i, (defense, label) in enumerate(zip(defenses, defense_labels)):
            values = []
            for cat_name, cat_langs in categories.items():
                total_succ = sum(data[model][defense]["results"].get(l, {}).get("succeeded", 0) for l in cat_langs)
                total_all = sum(data[model][defense]["results"].get(l, {}).get("total", 0) for l in cat_langs)
                asr = (total_succ / total_all * 100) if total_all > 0 else 0
                values.append(asr)
            bars = ax.bar(x + i * width, values, width, label=label, color=DEFENSE_COLORS[defense], edgecolor='white')
            for bar, val in zip(bars, values):
                if val > 2:
                    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                            f'{val:.1f}%', ha='center', va='bottom', fontsize=7, fontweight='bold')

        ax.set_title(model, fontsize=12, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels(list(categories.keys()), fontsize=8)
        if idx == 0:
            ax.set_ylabel('ASR (%)', fontsize=11)
        ax.legend(fontsize=8)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    fig.suptitle('Defense Effectiveness by Language Category', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig6_language_categories.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 6: Language Categories Chart saved")


# ============================================================
# FIGURE 7: Pie Charts - Attack Success Distribution per Defense
# ============================================================
def fig7_pie_charts(data):
    fig, axes = plt.subplots(3, 3, figsize=(16, 16))

    models = list(MODELS.keys())
    defenses = ["baseline", "struq", "multistruq"]
    defense_labels = ["Baseline", "StruQ", "MultiStruQ"]

    colors_list = plt.cm.Set3(np.linspace(0, 1, len(LANGUAGES)))

    for row, model in enumerate(models):
        for col, (defense, dlabel) in enumerate(zip(defenses, defense_labels)):
            ax = axes[row][col]
            succeeded_per_lang = []
            labels = []
            for lang in LANGUAGES:
                r = data[model][defense]["results"].get(lang, {"succeeded": 0})
                s = r.get("succeeded", 0)
                if s > 0:
                    succeeded_per_lang.append(s)
                    labels.append(LANG_LABELS[lang])

            if sum(succeeded_per_lang) == 0:
                ax.text(0.5, 0.5, 'No Attacks\nSucceeded!', ha='center', va='center',
                        fontsize=14, fontweight='bold', color='green',
                        transform=ax.transAxes)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
            else:
                wedges, texts, autotexts = ax.pie(succeeded_per_lang, labels=labels,
                    autopct='%1.0f%%', startangle=90, colors=colors_list[:len(labels)],
                    textprops={'fontsize': 7})
                for t in autotexts:
                    t.set_fontsize(7)

            title = f"{model}\n{dlabel}"
            ax.set_title(title, fontsize=10, fontweight='bold')

    fig.suptitle('Distribution of Successful Attacks by Language', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig7_attack_distribution_pie.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 7: Pie Charts saved")


# ============================================================
# FIGURE 8: Line Chart - Defense Progression
# ============================================================
def fig8_defense_progression(data):
    fig, ax = plt.subplots(figsize=(10, 6))

    defenses_x = [0, 1, 2]
    defense_labels = ["Baseline\n(No Defense)", "StruQ\n(Format Only)", "MultiStruQ\n(Trained)"]

    for model in MODELS.keys():
        values = [
            get_overall_asr(data[model]["baseline"]),
            get_overall_asr(data[model]["struq"]),
            get_overall_asr(data[model]["multistruq"]),
        ]
        ax.plot(defenses_x, values, 'o-', linewidth=3, markersize=10, label=model, color=MODEL_COLORS[model])
        for x, v in zip(defenses_x, values):
            ax.annotate(f'{v:.1f}%', (x, v), textcoords="offset points", xytext=(0, 12),
                        ha='center', fontsize=10, fontweight='bold', color=MODEL_COLORS[model])

    ax.set_xticks(defenses_x)
    ax.set_xticklabels(defense_labels, fontsize=11)
    ax.set_ylabel('Attack Success Rate (ASR %)', fontsize=12)
    ax.set_title('Defense Progression: Reducing Attack Success Rate', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_ylim(0, max([get_overall_asr(data[m]["baseline"]) for m in MODELS.keys()]) * 1.3)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig8_defense_progression.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 8: Defense Progression Line Chart saved")


# ============================================================
# FIGURE 9: Stacked Bar - Baseline vs MultiStruQ per Language (all models)
# ============================================================
def fig9_before_after(data):
    fig, axes = plt.subplots(1, 3, figsize=(20, 6), sharey=True)

    for idx, model in enumerate(MODELS.keys()):
        ax = axes[idx]
        x = np.arange(len(LANGUAGES))
        width = 0.35

        baseline_vals = [get_asr(data[model]["baseline"], l) for l in LANGUAGES]
        multistruq_vals = [get_asr(data[model]["multistruq"], l) for l in LANGUAGES]

        ax.bar(x - width/2, baseline_vals, width, label='Baseline', color=DEFENSE_COLORS["baseline"], alpha=0.8)
        ax.bar(x + width/2, multistruq_vals, width, label='MultiStruQ', color=DEFENSE_COLORS["multistruq"], alpha=0.8)

        ax.set_title(model, fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([LANG_LABELS[l] for l in LANGUAGES], rotation=45, ha='right', fontsize=8)
        if idx == 0:
            ax.set_ylabel('ASR (%)', fontsize=11)
        ax.legend(fontsize=9)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    fig.suptitle('Before vs After: Baseline → MultiStruQ Defense', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig9_before_after.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 9: Before/After Comparison saved")


# ============================================================
# Generate Comprehensive Report
# ============================================================
def generate_report(data):
    report = []
    report.append("# MultiStruQ: Comprehensive Results Analysis")
    report.append(f"\n**Date**: July 27, 2026")
    report.append(f"**Dataset**: 400 evaluation samples across 9 languages")
    report.append(f"**Training**: 6,000 samples (3,000 clean + 3,000 attacked)")
    report.append(f"**Models**: Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3")

    # ============================================================
    # Section 1: Overall Results
    # ============================================================
    report.append("\n---\n## 1. Overall Results Summary\n")
    report.append("| Model | Baseline ASR | StruQ ASR | MultiStruQ ASR | Reduction (B→M) |")
    report.append("|-------|-------------|-----------|----------------|-----------------|")

    for model in MODELS.keys():
        b = get_overall_asr(data[model]["baseline"])
        s = get_overall_asr(data[model]["struq"])
        m = get_overall_asr(data[model]["multistruq"])
        reduction = b - m
        pct_reduction = (reduction / b * 100) if b > 0 else 0
        report.append(f"| **{model}** | {b:.1f}% | {s:.1f}% | {m:.1f}% | **-{reduction:.1f}pp** ({pct_reduction:.0f}% relative) |")

    avg_b = np.mean([get_overall_asr(data[m]["baseline"]) for m in MODELS.keys()])
    avg_s = np.mean([get_overall_asr(data[m]["struq"]) for m in MODELS.keys()])
    avg_m = np.mean([get_overall_asr(data[m]["multistruq"]) for m in MODELS.keys()])
    report.append(f"| **Average** | {avg_b:.1f}% | {avg_s:.1f}% | {avg_m:.1f}% | **-{avg_b - avg_m:.1f}pp** ({(avg_b - avg_m)/avg_b*100:.0f}% relative) |")

    report.append(f"\n**Key Finding**: MultiStruQ reduces the average ASR from **{avg_b:.1f}%** to **{avg_m:.1f}%**, "
                  f"a **{(avg_b - avg_m)/avg_b*100:.0f}%** relative reduction across all three models.")

    # ============================================================
    # Section 2: Per-Model Analysis
    # ============================================================
    report.append("\n---\n## 2. Per-Model Analysis\n")

    for model in MODELS.keys():
        report.append(f"\n### 2.{list(MODELS.keys()).index(model)+1}. {model}\n")
        report.append(f"| Language | Baseline | StruQ | MultiStruQ | Reduction |")
        report.append(f"|----------|----------|-------|------------|-----------|")

        for lang in LANGUAGES:
            b = get_asr(data[model]["baseline"], lang)
            s = get_asr(data[model]["struq"], lang)
            m = get_asr(data[model]["multistruq"], lang)
            red = b - m
            report.append(f"| {LANG_LABELS[lang]} | {b:.1f}% | {s:.1f}% | {m:.1f}% | {red:+.1f}pp |")

        overall_b = get_overall_asr(data[model]["baseline"])
        overall_s = get_overall_asr(data[model]["struq"])
        overall_m = get_overall_asr(data[model]["multistruq"])
        report.append(f"| **Overall** | **{overall_b:.1f}%** | **{overall_s:.1f}%** | **{overall_m:.1f}%** | **{overall_b - overall_m:+.1f}pp** |")

        # Model-specific insights
        report.append(f"\n**Insights for {model}:**")

        # Most vulnerable language at baseline
        baseline_asrs = {l: get_asr(data[model]["baseline"], l) for l in LANGUAGES}
        most_vuln = max(baseline_asrs, key=baseline_asrs.get)
        report.append(f"- Most vulnerable language at baseline: **{LANG_LABELS[most_vuln]}** ({baseline_asrs[most_vuln]:.1f}% ASR)")

        # Best defended language with MultiStruQ
        multistruq_asrs = {l: get_asr(data[model]["multistruq"], l) for l in LANGUAGES}
        zero_langs = [l for l, v in multistruq_asrs.items() if v == 0.0]
        if zero_langs:
            report.append(f"- Languages with 0% ASR after MultiStruQ: **{', '.join(LANG_LABELS[l] for l in zero_langs)}**")

        # Biggest improvement
        improvements = {l: get_asr(data[model]["baseline"], l) - get_asr(data[model]["multistruq"], l) for l in LANGUAGES}
        best_imp = max(improvements, key=improvements.get)
        report.append(f"- Largest improvement: **{LANG_LABELS[best_imp]}** ({improvements[best_imp]:+.1f}pp)")

        # StruQ effectiveness
        struq_change = overall_s - overall_b
        if struq_change < 0:
            report.append(f"- StruQ format alone reduced ASR by {abs(struq_change):.1f}pp")
        else:
            report.append(f"- ⚠️ StruQ format INCREASED ASR by {struq_change:.1f}pp (format may expose model to more attacks)")

    # ============================================================
    # Section 3: Cross-Model Comparison
    # ============================================================
    report.append("\n---\n## 3. Cross-Model Comparison\n")

    report.append("### 3.1. Baseline Vulnerability Ranking\n")
    report.append("Models ranked by baseline vulnerability (highest ASR = most vulnerable):\n")
    baseline_ranked = sorted(MODELS.keys(), key=lambda m: get_overall_asr(data[m]["baseline"]), reverse=True)
    for i, model in enumerate(baseline_ranked):
        asr = get_overall_asr(data[model]["baseline"])
        report.append(f"{i+1}. **{model}**: {asr:.1f}% ASR")

    report.append("\n### 3.2. MultiStruQ Defense Effectiveness Ranking\n")
    report.append("Models ranked by MultiStruQ effectiveness (lowest ASR = best defense):\n")
    multistruq_ranked = sorted(MODELS.keys(), key=lambda m: get_overall_asr(data[m]["multistruq"]))
    for i, model in enumerate(multistruq_ranked):
        asr = get_overall_asr(data[model]["multistruq"])
        report.append(f"{i+1}. **{model}**: {asr:.1f}% ASR")

    report.append("\n### 3.3. Per-Language Comparison Across Models\n")
    report.append("| Language | " + " | ".join([f"{m} (B→M)" for m in MODELS.keys()]) + " |")
    report.append("|----------| " + " | ".join(["---" for _ in MODELS.keys()]) + " |")

    for lang in LANGUAGES:
        row = f"| {LANG_LABELS[lang]} |"
        for model in MODELS.keys():
            b = get_asr(data[model]["baseline"], lang)
            m = get_asr(data[model]["multistruq"], lang)
            row += f" {b:.0f}% → {m:.0f}% |"
        report.append(row)

    # ============================================================
    # Section 4: Defense Comparison
    # ============================================================
    report.append("\n---\n## 4. Defense Comparison\n")

    report.append("### 4.1. All Baselines Together\n")
    report.append("| Language | " + " | ".join(MODELS.keys()) + " | Average |")
    report.append("|----------|" + "|".join(["---" for _ in MODELS.keys()]) + "|---------|")
    for lang in LANGUAGES:
        vals = [get_asr(data[m]["baseline"], lang) for m in MODELS.keys()]
        avg = np.mean(vals)
        report.append(f"| {LANG_LABELS[lang]} | " + " | ".join(f"{v:.1f}%" for v in vals) + f" | {avg:.1f}% |")
    overall_vals = [get_overall_asr(data[m]["baseline"]) for m in MODELS.keys()]
    report.append(f"| **Overall** | " + " | ".join(f"**{v:.1f}%**" for v in overall_vals) + f" | **{np.mean(overall_vals):.1f}%** |")

    report.append("\n### 4.2. All StruQ Together\n")
    report.append("| Language | " + " | ".join(MODELS.keys()) + " | Average |")
    report.append("|----------|" + "|".join(["---" for _ in MODELS.keys()]) + "|---------|")
    for lang in LANGUAGES:
        vals = [get_asr(data[m]["struq"], lang) for m in MODELS.keys()]
        avg = np.mean(vals)
        report.append(f"| {LANG_LABELS[lang]} | " + " | ".join(f"{v:.1f}%" for v in vals) + f" | {avg:.1f}% |")
    overall_vals = [get_overall_asr(data[m]["struq"]) for m in MODELS.keys()]
    report.append(f"| **Overall** | " + " | ".join(f"**{v:.1f}%**" for v in overall_vals) + f" | **{np.mean(overall_vals):.1f}%** |")

    report.append("\n### 4.3. All MultiStruQ Together\n")
    report.append("| Language | " + " | ".join(MODELS.keys()) + " | Average |")
    report.append("|----------|" + "|".join(["---" for _ in MODELS.keys()]) + "|---------|")
    for lang in LANGUAGES:
        vals = [get_asr(data[m]["multistruq"], lang) for m in MODELS.keys()]
        avg = np.mean(vals)
        report.append(f"| {LANG_LABELS[lang]} | " + " | ".join(f"{v:.1f}%" for v in vals) + f" | {avg:.1f}% |")
    overall_vals = [get_overall_asr(data[m]["multistruq"]) for m in MODELS.keys()]
    report.append(f"| **Overall** | " + " | ".join(f"**{v:.1f}%**" for v in overall_vals) + f" | **{np.mean(overall_vals):.1f}%** |")

    # ============================================================
    # Section 5: Key Findings
    # ============================================================
    report.append("\n---\n## 5. Key Findings for Research Paper\n")

    # Finding 1: Models are vulnerable
    report.append("### Finding 1: All Models Are Vulnerable to Multilingual Prompt Injection\n")
    report.append(f"- Average baseline ASR across all models: **{avg_b:.1f}%**")
    report.append(f"- Most vulnerable model: **{baseline_ranked[0]}** ({get_overall_asr(data[baseline_ranked[0]]['baseline']):.1f}%)")
    report.append(f"- Least vulnerable model: **{baseline_ranked[-1]}** ({get_overall_asr(data[baseline_ranked[-1]]['baseline']):.1f}%)")

    # Finding 2: StruQ alone is insufficient
    report.append("\n### Finding 2: StruQ Format Alone Has Inconsistent Results\n")
    for model in MODELS.keys():
        b = get_overall_asr(data[model]["baseline"])
        s = get_overall_asr(data[model]["struq"])
        change = s - b
        direction = "increased" if change > 0 else "decreased"
        report.append(f"- **{model}**: StruQ {direction} ASR by {abs(change):.1f}pp ({b:.1f}% → {s:.1f}%)")

    # Finding 3: MultiStruQ is effective
    report.append("\n### Finding 3: MultiStruQ Training Dramatically Reduces ASR\n")
    for model in MODELS.keys():
        b = get_overall_asr(data[model]["baseline"])
        m = get_overall_asr(data[model]["multistruq"])
        reduction = b - m
        pct = (reduction / b * 100) if b > 0 else 0
        report.append(f"- **{model}**: {b:.1f}% → {m:.1f}% (**{pct:.0f}% relative reduction**)")

    # Finding 4: Language-specific insights
    report.append("\n### Finding 4: Language-Specific Vulnerability Patterns\n")

    # Average ASR per language across models for baseline
    report.append("**Baseline vulnerability by language (average across models):**\n")
    lang_avg_baseline = {}
    for lang in LANGUAGES:
        avg = np.mean([get_asr(data[m]["baseline"], lang) for m in MODELS.keys()])
        lang_avg_baseline[lang] = avg
    sorted_langs = sorted(lang_avg_baseline.items(), key=lambda x: -x[1])
    for lang, avg in sorted_langs:
        report.append(f"- {LANG_LABELS[lang]}: {avg:.1f}%")

    # Finding 5: Cross-lingual transfer
    report.append("\n### Finding 5: Cross-lingual Transfer Learning\n")
    report.append("MultiStruQ training on mixed-language data provides cross-lingual defense:")
    for lang in ["tamil", "telugu", "marathi", "bengali"]:
        avgs = [get_asr(data[m]["multistruq"], lang) for m in MODELS.keys()]
        overall_avg = np.mean(avgs)
        report.append(f"- **{LANG_LABELS[lang]}**: Average MultiStruQ ASR = {overall_avg:.1f}%")

    # ============================================================
    # Section 6: Statistical Summary
    # ============================================================
    report.append("\n---\n## 6. Statistical Summary\n")

    total_attacks = 400 * 3 * 3  # 400 samples × 3 models × 3 defenses
    report.append(f"- **Total evaluations conducted**: {total_attacks:,}")
    report.append(f"- **Evaluation dataset size**: 400 samples")
    report.append(f"- **Training dataset size**: 6,000 samples")
    report.append(f"- **Languages tested**: 9 (5 Indic + English + Hinglish + Cross-lingual + Cultural)")
    report.append(f"- **Models tested**: 3 (Qwen2.5-7B, Llama-3.1-8B, Mistral-7B)")
    report.append(f"- **Defense methods**: 3 (Baseline, StruQ, MultiStruQ)")

    # ============================================================
    # Section 7: Figures Index
    # ============================================================
    report.append("\n---\n## 7. Generated Figures\n")
    figures = [
        ("fig1_overall_asr_comparison.png", "Overall ASR comparison across models and defenses (grouped bar chart)"),
        ("fig2_asr_heatmap.png", "ASR heatmap: models × languages × defenses"),
        ("fig3_per_model_defense_comparison.png", "Per-model grouped bar chart showing all languages"),
        ("fig4_asr_reduction.png", "ASR reduction from baseline to MultiStruQ per language"),
        ("fig5_radar_vulnerability.png", "Radar chart showing language vulnerability profiles"),
        ("fig6_language_categories.png", "Defense effectiveness by language category"),
        ("fig7_attack_distribution_pie.png", "Pie charts showing distribution of successful attacks"),
        ("fig8_defense_progression.png", "Line chart showing defense progression across methods"),
        ("fig9_before_after.png", "Before/after comparison: Baseline vs MultiStruQ"),
    ]
    for filename, desc in figures:
        report.append(f"- **`{filename}`**: {desc}")

    report.append("\n---\n*Report generated automatically from experimental results.*")

    # Write report
    report_path = os.path.join(OUTPUT_DIR, "COMPREHENSIVE_ANALYSIS_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"  ✅ Report saved to {report_path}")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("MultiStruQ Comprehensive Analysis")
    print("=" * 60)

    print("\n📊 Loading all results...")
    data = load_results()
    print("  ✅ Loaded results for 3 models × 3 defenses = 9 result files\n")

    print("📈 Generating figures...")
    fig1_overall_comparison(data)
    fig2_heatmap(data)
    fig3_per_model(data)
    fig4_asr_reduction(data)
    fig5_radar_chart(data)
    fig6_language_categories(data)
    fig7_pie_charts(data)
    fig8_defense_progression(data)
    fig9_before_after(data)

    print("\n📝 Generating comprehensive report...")
    generate_report(data)

    print(f"\n✅ All analysis complete!")
    print(f"📁 Output saved to: {OUTPUT_DIR}")
    print(f"   - 9 figures (.png)")
    print(f"   - 1 comprehensive report (.md)")
