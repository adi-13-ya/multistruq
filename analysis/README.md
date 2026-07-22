# Analysis Scripts

## analyse_results.py

Generates plots and tables from evaluation results.

### Usage
```bash
python analysis/analyse_results.py
```

### Outputs
- `results/plots/comparison_plot.png` - Baseline vs MultiStruQ comparison
- `results/plots/improvement_plot.png` - Per-language improvement
- `results/data/results_table.csv` - Results table for paper
- Console output with LaTeX table code

### Requirements
- matplotlib
- seaborn
- pandas
- numpy
