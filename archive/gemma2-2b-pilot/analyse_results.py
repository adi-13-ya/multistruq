"""
Analyze MultiStruQ results and create visualizations for the paper.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

def load_results(filepath):
    """Load results from JSON file."""
    with open(filepath) as f:
        return json.load(f)

def create_comparison_plot(results, output_path="comparison_plot.png"):
    """Create bar plot comparing baseline vs MultiStruQ."""
    baseline = results["baseline"]
    multistruq = results["multistruq"]
    
    languages = sorted(baseline.keys())
    baseline_asr = [baseline[lang]["succeeded"] / baseline[lang]["total"] * 100 for lang in languages]
    multistruq_asr = [multistruq[lang]["succeeded"] / multistruq[lang]["total"] * 100 for lang in languages]
    
    x = np.arange(len(languages))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 6))
    bars1 = ax.bar(x - width/2, baseline_asr, width, label='Baseline (No Defense)', color='#e74c3c', alpha=0.8)
    bars2 = ax.bar(x + width/2, multistruq_asr, width, label='MultiStruQ', color='#27ae60', alpha=0.8)
    
    ax.set_xlabel('Language/Attack Type', fontweight='bold')
    ax.set_ylabel('Attack Success Rate (%)', fontweight='bold')
    ax.set_title('MultiStruQ Defense Effectiveness Across Languages', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([lang.replace('_', ' ').title() for lang in languages], rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()

def create_improvement_plot(results, output_path="improvement_plot.png"):
    """Create plot showing improvement per language."""
    baseline = results["baseline"]
    multistruq = results["multistruq"]
    
    languages = sorted(baseline.keys())
    improvements = []
    
    for lang in languages:
        baseline_asr = baseline[lang]["succeeded"] / baseline[lang]["total"] * 100
        multistruq_asr = multistruq[lang]["succeeded"] / multistruq[lang]["total"] * 100
        improvements.append(baseline_asr - multistruq_asr)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(range(len(languages)), improvements, color='#3498db', alpha=0.8)
    
    ax.set_yticks(range(len(languages)))
    ax.set_yticklabels([lang.replace('_', ' ').title() for lang in languages])
    ax.set_xlabel('ASR Reduction (%)', fontweight='bold')
    ax.set_title('MultiStruQ Defense Improvement by Language', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, improvements)):
        ax.text(val + 1, i, f'+{val:.1f}%', va='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()

def create_results_table(results, output_path="results_table.csv"):
    """Create CSV table for LaTeX."""
    baseline = results["baseline"]
    multistruq = results["multistruq"]
    
    data = []
    for lang in sorted(baseline.keys()):
        baseline_asr = baseline[lang]["succeeded"] / baseline[lang]["total"] * 100
        multistruq_asr = multistruq[lang]["succeeded"] / multistruq[lang]["total"] * 100
        improvement = baseline_asr - multistruq_asr
        
        data.append({
            "Language": lang.replace('_', ' ').title(),
            "Samples": baseline[lang]["total"],
            "Baseline ASR (%)": f"{baseline_asr:.1f}",
            "MultiStruQ ASR (%)": f"{multistruq_asr:.1f}",
            "Improvement (%)": f"{improvement:.1f}",
        })
    
    # Add overall row
    baseline_total = sum(r["succeeded"] for r in baseline.values())
    baseline_count = sum(r["total"] for r in baseline.values())
    multistruq_total = sum(r["succeeded"] for r in multistruq.values())
    multistruq_count = sum(r["total"] for r in multistruq.values())
    
    data.append({
        "Language": "**Overall**",
        "Samples": baseline_count,
        "Baseline ASR (%)": f"{baseline_total/baseline_count*100:.1f}",
        "MultiStruQ ASR (%)": f"{multistruq_total/multistruq_count*100:.1f}",
        "Improvement (%)": f"{(baseline_total/baseline_count - multistruq_total/multistruq_count)*100:.1f}",
    })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Saved: {output_path}")
    
    # Also print LaTeX table
    print("\nLaTeX Table:")
    print(df.to_latex(index=False))

def create_summary_stats(results):
    """Print summary statistics."""
    baseline = results["baseline"]
    multistruq = results["multistruq"]
    
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    baseline_total = sum(r["succeeded"] for r in baseline.values())
    baseline_count = sum(r["total"] for r in baseline.values())
    multistruq_total = sum(r["succeeded"] for r in multistruq.values())
    multistruq_count = sum(r["total"] for r in multistruq.values())
    
    print(f"\nOverall Performance:")
    print(f"  Baseline ASR: {baseline_total/baseline_count*100:.2f}%")
    print(f"  MultiStruQ ASR: {multistruq_total/multistruq_count*100:.2f}%")
    print(f"  Absolute Improvement: {(baseline_total/baseline_count - multistruq_total/multistruq_count)*100:.2f}%")
    print(f"  Relative Improvement: {(1 - multistruq_total/baseline_total)*100:.2f}%")
    
    # Per-language stats
    improvements = []
    for lang in baseline.keys():
        baseline_asr = baseline[lang]["succeeded"] / baseline[lang]["total"] * 100
        multistruq_asr = multistruq[lang]["succeeded"] / multistruq[lang]["total"] * 100
        improvements.append(baseline_asr - multistruq_asr)
    
    print(f"\nPer-Language Improvements:")
    print(f"  Mean: {np.mean(improvements):.2f}%")
    print(f"  Median: {np.median(improvements):.2f}%")
    print(f"  Std Dev: {np.std(improvements):.2f}%")
    print(f"  Min: {min(improvements):.2f}%")
    print(f"  Max: {max(improvements):.2f}%")

if __name__ == "__main__":
    # Load results
    results = load_results("results/stage6_final_results.json")
    
    # Create visualizations
    print("Creating visualizations...")
    create_comparison_plot(results, "results/comparison_plot.png")
    create_improvement_plot(results, "results/improvement_plot.png")
    create_results_table(results, "results/results_table.csv")
    create_summary_stats(results)
    
    print("\n✅ Analysis complete!")
    print("📁 Check the results/ folder for all outputs")