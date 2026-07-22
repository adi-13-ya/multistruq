# MultiStruQ: Multilingual Defense Against Prompt Injection Attacks

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hugging Face](https://img.shields.io/badge/🤗-Model-yellow)](https://huggingface.co/khukhamos/multistruq-gemma2-2b)

> **A structured query defense mechanism for large language models against multilingual prompt injection attacks**

## 🎯 Overview

MultiStruQ extends the StruQ defense framework to protect LLMs against prompt injection attacks in **9 languages**: English, Hindi, Hinglish, Bengali, Tamil, Marathi, Telugu, and cross-lingual contexts.

### Key Results

| Metric | Baseline (No Defense) | MultiStruQ | Improvement |
|--------|----------------------|------------|-------------|
| **Overall ASR** | 40.85% | **0.00%** | **-40.85%** |
| English | 62.5% | **0.0%** | -62.5% |
| Hindi | 50.0% | **0.0%** | -50.0% |
| Hinglish | 33.3% | **0.0%** | -33.3% |
| Cross-lingual | 57.1% | **0.0%** | -57.1% |

**🎉 100% defense rate across all tested languages**

---

## 📁 Repository Structure

```
multistruq/
├── README.md                          # This file
├── PROJECT_STATUS.md                  # Detailed completion status
├── METHODOLOGY.md                     # Technical methodology
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── datasets/                          # Dataset creation scripts
│   ├── attack_templates.py            # Multilingual attack templates
│   ├── create_eval_dataset_v2.py      # Evaluation dataset generator
│   ├── create_training_dataset.py     # Training dataset generator
│   ├── validate_dataset.py            # Dataset validation
│   └── DATASET_SUMMARY.md             # Dataset documentation
│
├── notebooks/                         # Kaggle notebooks
│   ├── baseline_evaluation.ipynb      # Stage 4: Baseline evaluation
│   ├── training.ipynb                 # Stage 5: Model training
│   └── final_evaluation.ipynb         # Stage 6: Final evaluation
│
├── results/                           # Experimental results
│   ├── stage6_final_results.json      # Raw evaluation data
│   ├── comparison_plot.png            # Baseline vs MultiStruQ plot
│   ├── improvement_plot.png           # Per-language improvement
│   └── results_table.csv              # Results table
│
├── analysis/                          # Analysis scripts
│   └── analyse_results.py             # Generate plots & tables
│
├── docs/                              # Documentation
│   ├── MultiStruQ_Implementation_Guide.md
│   └── STAGE_5_UPDATES.md
│
└── paper/                             # Research paper (LaTeX)
    ├── multistruq_paper.tex
    ├── references.bib
    └── figures/
```

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/adi-13-ya/multistruq.git
cd multistruq
pip install -r requirements.txt
```

### 2. Download Datasets

Due to size constraints, datasets are hosted separately:

```bash
# Download from Kaggle or generate locally
python datasets/create_eval_dataset_v2.py
python datasets/create_training_dataset.py
```

### 3. Run Evaluation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load MultiStruQ model
base_model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")
model = PeftModel.from_pretrained(base_model, "khukhamos/multistruq-gemma2-2b")

# Test against an attack
response = model.generate(...)
```

### 4. Reproduce Results

```bash
# Generate plots and tables
python analysis/analyse_results.py
```

---

## 📊 Methodology

### Defense Approach

MultiStruQ uses **structured query formatting** combined with **QLoRA fine-tuning** to:

1. **Separate** instructions from data using clear delimiters
2. **Train** the model to ignore injected instructions in data fields
3. **Generalize** across multiple languages and attack types

### Training Details

- **Base Model**: Gemma-2-2b-it
- **Method**: QLoRA (4-bit quantization)
- **Dataset**: 1,000 samples (50% clean, 50% attacked)
- **Languages**: 9 (English, Hindi, Hinglish, Bengali, Tamil, Marathi, Telugu, cross-lingual, cultural)
- **Training Time**: ~45-60 minutes on Kaggle T4 GPU
- **Parameters**: 
  - Batch size: 1
  - Gradient accumulation: 16
  - Learning rate: 2e-4
  - Epochs: 3
  - Max sequence length: 128 tokens

### Evaluation

- **Dataset**: 71 explicit prompt injection attacks
- **Attack Types**: Naive, ignore previous, authority, context switching, encoding
- **Metric**: Attack Success Rate (ASR)

---

## 🔬 Research Contributions

1. **First multilingual defense** against prompt injection attacks
2. **100% defense rate** across 9 languages
3. **Lightweight approach** using QLoRA (only 1-2% parameters trained)
4. **Open-source dataset** of multilingual prompt injection attacks
5. **Reproducible methodology** with detailed documentation

---

## 📈 Results

### Overall Performance

```
Baseline ASR:    40.85% (29/71 attacks succeeded)
MultiStruQ ASR:   0.00% (0/71 attacks succeeded)
Improvement:    -40.85% (100% reduction)
```

### Per-Language Breakdown

| Language | Samples | Baseline ASR | MultiStruQ ASR | Improvement |
|----------|---------|--------------|----------------|-------------|
| English | 16 | 62.5% | 0.0% | -62.5% |
| Hindi Native | 12 | 50.0% | 0.0% | -50.0% |
| Hinglish | 15 | 33.3% | 0.0% | -33.3% |
| Bengali | 5 | 20.0% | 0.0% | -20.0% |
| Tamil | 3 | 33.3% | 0.0% | -33.3% |
| Marathi | 3 | 66.7% | 0.0% | -66.7% |
| Telugu | 2 | 0.0% | 0.0% | 0.0% |
| Cross-lingual | 7 | 57.1% | 0.0% | -57.1% |
| Cultural | 8 | 0.0% | 0.0% | 0.0% |

See `results/` folder for detailed analysis and visualizations.

---

## 📝 Citation

If you use this work in your research, please cite:

```bibtex
@article{multistruq2026,
  title={MultiStruQ: Multilingual Defense Against Prompt Injection Attacks},
  author={Aditya Gujar, Aditya Shukla, Arushi Tiwari},
  journal={arXiv preprint},
  year={2026}
}
```

---

## 🛠️ Datasets

### Evaluation Dataset (v2)
- **Size**: 71 samples
- **Languages**: 9
- **Attack types**: 5 (naive, ignore, authority, context-switching, encoding)
- **Format**: JSON with instruction, clean_data, attacked_data, metadata

### Training Dataset
- **Size**: 1,000 samples (reduced from 4,000 for memory constraints)
- **Composition**: 50% clean tasks, 50% attacked tasks
- **Base**: Alpaca instruction dataset
- **Attacks**: Multilingual injections from attack templates

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **StruQ Framework**: Original structured query defense
- **IndicJR Dataset**: Multilingual prompt dataset
- **Alpaca Dataset**: Instruction-following dataset
- **Hugging Face**: Model hosting and transformers library
- **Kaggle**: Free GPU resources for training

---

## 📧 Contact

For questions or collaborations:
- **Email**: aditya.070505@gmail.com
- **GitHub**: [@adi-13-ya](https://github.com/adi-13-ya)
- **Model**: [Hugging Face](https://huggingface.co/khukhamos/multistruq-gemma2-2b)

---

## 🔗 Related Work

- [StruQ: Defending Against Prompt Injection](https://arxiv.org/abs/2402.06363)
- [IndicJR: Multilingual Jailbreak Dataset](https://github.com/indicjr/dataset)
- [Alpaca: Instruction-Following Dataset](https://github.com/tatsu-lab/stanford_alpaca)

---

**⭐ Star this repository if you find it useful!**
