# MultiStruQ: Comprehensive Results Analysis

**Date**: July 27, 2026
**Dataset**: 400 evaluation samples across 9 languages
**Training**: 6,000 samples (3,000 clean + 3,000 attacked)
**Models**: Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3

---
## 1. Overall Results Summary

| Model | Baseline ASR | StruQ ASR | MultiStruQ ASR | Reduction (B→M) |
|-------|-------------|-----------|----------------|-----------------|
| **Qwen2.5-7B** | 54.2% | 61.3% | 0.2% | **-54.0pp** (100% relative) |
| **Llama-3.1-8B** | 29.2% | 22.8% | 1.5% | **-27.8pp** (95% relative) |
| **Mistral-7B** | 34.5% | 16.2% | 7.5% | **-27.0pp** (78% relative) |
| **Average** | 39.3% | 33.4% | 3.1% | **-36.2pp** (92% relative) |

**Key Finding**: MultiStruQ reduces the average ASR from **39.3%** to **3.1%**, a **92%** relative reduction across all three models.

---
## 2. Per-Model Analysis


### 2.1. Qwen2.5-7B

| Language | Baseline | StruQ | MultiStruQ | Reduction |
|----------|----------|-------|------------|-----------|
| English | 67.8% | 82.2% | 1.1% | +66.7pp |
| Hindi | 39.7% | 50.0% | 0.0% | +39.7pp |
| Hinglish | 53.6% | 66.7% | 0.0% | +53.6pp |
| Bengali | 53.6% | 85.7% | 0.0% | +53.6pp |
| Tamil | 44.4% | 11.1% | 0.0% | +44.4pp |
| Marathi | 50.0% | 43.8% | 0.0% | +50.0pp |
| Telugu | 16.7% | 33.3% | 0.0% | +16.7pp |
| Cross-lingual | 70.0% | 70.0% | 0.0% | +70.0pp |
| Cultural | 52.3% | 36.4% | 0.0% | +52.3pp |
| **Overall** | **54.2%** | **61.3%** | **0.2%** | **+54.0pp** |

**Insights for Qwen2.5-7B:**
- Most vulnerable language at baseline: **Cross-lingual** (70.0% ASR)
- Languages with 0% ASR after MultiStruQ: **Hindi, Hinglish, Bengali, Tamil, Marathi, Telugu, Cross-lingual, Cultural**
- Largest improvement: **Cross-lingual** (+70.0pp)
- ⚠️ StruQ format INCREASED ASR by 7.0pp (format may expose model to more attacks)

### 2.2. Llama-3.1-8B

| Language | Baseline | StruQ | MultiStruQ | Reduction |
|----------|----------|-------|------------|-----------|
| English | 27.8% | 52.2% | 4.4% | +23.3pp |
| Hindi | 11.8% | 13.2% | 0.0% | +11.8pp |
| Hinglish | 56.0% | 19.0% | 0.0% | +56.0pp |
| Bengali | 14.3% | 7.1% | 7.1% | +7.1pp |
| Tamil | 5.6% | 22.2% | 0.0% | +5.6pp |
| Marathi | 12.5% | 6.2% | 0.0% | +12.5pp |
| Telugu | 8.3% | 8.3% | 0.0% | +8.3pp |
| Cross-lingual | 22.5% | 15.0% | 0.0% | +22.5pp |
| Cultural | 45.5% | 11.4% | 0.0% | +45.5pp |
| **Overall** | **29.2%** | **22.8%** | **1.5%** | **+27.8pp** |

**Insights for Llama-3.1-8B:**
- Most vulnerable language at baseline: **Hinglish** (56.0% ASR)
- Languages with 0% ASR after MultiStruQ: **Hindi, Hinglish, Tamil, Marathi, Telugu, Cross-lingual, Cultural**
- Largest improvement: **Hinglish** (+56.0pp)
- StruQ format alone reduced ASR by 6.5pp

### 2.3. Mistral-7B

| Language | Baseline | StruQ | MultiStruQ | Reduction |
|----------|----------|-------|------------|-----------|
| English | 34.4% | 31.1% | 10.0% | +24.4pp |
| Hindi | 27.9% | 13.2% | 4.4% | +23.5pp |
| Hinglish | 36.9% | 9.5% | 11.9% | +25.0pp |
| Bengali | 28.6% | 10.7% | 0.0% | +28.6pp |
| Tamil | 16.7% | 11.1% | 0.0% | +16.7pp |
| Marathi | 12.5% | 6.2% | 6.2% | +6.2pp |
| Telugu | 8.3% | 8.3% | 0.0% | +8.3pp |
| Cross-lingual | 57.5% | 20.0% | 0.0% | +57.5pp |
| Cultural | 45.5% | 11.4% | 15.9% | +29.5pp |
| **Overall** | **34.5%** | **16.2%** | **7.5%** | **+27.0pp** |

**Insights for Mistral-7B:**
- Most vulnerable language at baseline: **Cross-lingual** (57.5% ASR)
- Languages with 0% ASR after MultiStruQ: **Bengali, Tamil, Telugu, Cross-lingual**
- Largest improvement: **Cross-lingual** (+57.5pp)
- StruQ format alone reduced ASR by 18.2pp

---
## 3. Cross-Model Comparison

### 3.1. Baseline Vulnerability Ranking

Models ranked by baseline vulnerability (highest ASR = most vulnerable):

1. **Qwen2.5-7B**: 54.2% ASR
2. **Mistral-7B**: 34.5% ASR
3. **Llama-3.1-8B**: 29.2% ASR

### 3.2. MultiStruQ Defense Effectiveness Ranking

Models ranked by MultiStruQ effectiveness (lowest ASR = best defense):

1. **Qwen2.5-7B**: 0.2% ASR
2. **Llama-3.1-8B**: 1.5% ASR
3. **Mistral-7B**: 7.5% ASR

### 3.3. Per-Language Comparison Across Models

| Language | Qwen2.5-7B (B→M) | Llama-3.1-8B (B→M) | Mistral-7B (B→M) |
|----------| --- | --- | --- |
| English | 68% → 1% | 28% → 4% | 34% → 10% |
| Hindi | 40% → 0% | 12% → 0% | 28% → 4% |
| Hinglish | 54% → 0% | 56% → 0% | 37% → 12% |
| Bengali | 54% → 0% | 14% → 7% | 29% → 0% |
| Tamil | 44% → 0% | 6% → 0% | 17% → 0% |
| Marathi | 50% → 0% | 12% → 0% | 12% → 6% |
| Telugu | 17% → 0% | 8% → 0% | 8% → 0% |
| Cross-lingual | 70% → 0% | 22% → 0% | 57% → 0% |
| Cultural | 52% → 0% | 45% → 0% | 45% → 16% |

---
## 4. Defense Comparison

### 4.1. All Baselines Together

| Language | Qwen2.5-7B | Llama-3.1-8B | Mistral-7B | Average |
|----------|---|---|---|---------|
| English | 67.8% | 27.8% | 34.4% | 43.3% |
| Hindi | 39.7% | 11.8% | 27.9% | 26.5% |
| Hinglish | 53.6% | 56.0% | 36.9% | 48.8% |
| Bengali | 53.6% | 14.3% | 28.6% | 32.1% |
| Tamil | 44.4% | 5.6% | 16.7% | 22.2% |
| Marathi | 50.0% | 12.5% | 12.5% | 25.0% |
| Telugu | 16.7% | 8.3% | 8.3% | 11.1% |
| Cross-lingual | 70.0% | 22.5% | 57.5% | 50.0% |
| Cultural | 52.3% | 45.5% | 45.5% | 47.7% |
| **Overall** | **54.2%** | **29.2%** | **34.5%** | **39.3%** |

### 4.2. All StruQ Together

| Language | Qwen2.5-7B | Llama-3.1-8B | Mistral-7B | Average |
|----------|---|---|---|---------|
| English | 82.2% | 52.2% | 31.1% | 55.2% |
| Hindi | 50.0% | 13.2% | 13.2% | 25.5% |
| Hinglish | 66.7% | 19.0% | 9.5% | 31.7% |
| Bengali | 85.7% | 7.1% | 10.7% | 34.5% |
| Tamil | 11.1% | 22.2% | 11.1% | 14.8% |
| Marathi | 43.8% | 6.2% | 6.2% | 18.8% |
| Telugu | 33.3% | 8.3% | 8.3% | 16.7% |
| Cross-lingual | 70.0% | 15.0% | 20.0% | 35.0% |
| Cultural | 36.4% | 11.4% | 11.4% | 19.7% |
| **Overall** | **61.3%** | **22.8%** | **16.2%** | **33.4%** |

### 4.3. All MultiStruQ Together

| Language | Qwen2.5-7B | Llama-3.1-8B | Mistral-7B | Average |
|----------|---|---|---|---------|
| English | 1.1% | 4.4% | 10.0% | 5.2% |
| Hindi | 0.0% | 0.0% | 4.4% | 1.5% |
| Hinglish | 0.0% | 0.0% | 11.9% | 4.0% |
| Bengali | 0.0% | 7.1% | 0.0% | 2.4% |
| Tamil | 0.0% | 0.0% | 0.0% | 0.0% |
| Marathi | 0.0% | 0.0% | 6.2% | 2.1% |
| Telugu | 0.0% | 0.0% | 0.0% | 0.0% |
| Cross-lingual | 0.0% | 0.0% | 0.0% | 0.0% |
| Cultural | 0.0% | 0.0% | 15.9% | 5.3% |
| **Overall** | **0.2%** | **1.5%** | **7.5%** | **3.1%** |

---
## 5. Key Findings for Research Paper

### Finding 1: All Models Are Vulnerable to Multilingual Prompt Injection

- Average baseline ASR across all models: **39.3%**
- Most vulnerable model: **Qwen2.5-7B** (54.2%)
- Least vulnerable model: **Llama-3.1-8B** (29.2%)

### Finding 2: StruQ Format Alone Has Inconsistent Results

- **Qwen2.5-7B**: StruQ increased ASR by 7.0pp (54.2% → 61.3%)
- **Llama-3.1-8B**: StruQ decreased ASR by 6.5pp (29.2% → 22.8%)
- **Mistral-7B**: StruQ decreased ASR by 18.2pp (34.5% → 16.2%)

### Finding 3: MultiStruQ Training Dramatically Reduces ASR

- **Qwen2.5-7B**: 54.2% → 0.2% (**100% relative reduction**)
- **Llama-3.1-8B**: 29.2% → 1.5% (**95% relative reduction**)
- **Mistral-7B**: 34.5% → 7.5% (**78% relative reduction**)

### Finding 4: Language-Specific Vulnerability Patterns

**Baseline vulnerability by language (average across models):**

- Cross-lingual: 50.0%
- Hinglish: 48.8%
- Cultural: 47.7%
- English: 43.3%
- Bengali: 32.1%
- Hindi: 26.5%
- Marathi: 25.0%
- Tamil: 22.2%
- Telugu: 11.1%

### Finding 5: Cross-lingual Transfer Learning

MultiStruQ training on mixed-language data provides cross-lingual defense:
- **Tamil**: Average MultiStruQ ASR = 0.0%
- **Telugu**: Average MultiStruQ ASR = 0.0%
- **Marathi**: Average MultiStruQ ASR = 2.1%
- **Bengali**: Average MultiStruQ ASR = 2.4%

---
## 6. Statistical Summary

- **Total evaluations conducted**: 3,600
- **Evaluation dataset size**: 400 samples
- **Training dataset size**: 6,000 samples
- **Languages tested**: 9 (5 Indic + English + Hinglish + Cross-lingual + Cultural)
- **Models tested**: 3 (Qwen2.5-7B, Llama-3.1-8B, Mistral-7B)
- **Defense methods**: 3 (Baseline, StruQ, MultiStruQ)

---
## 7. Generated Figures

- **`fig1_overall_asr_comparison.png`**: Overall ASR comparison across models and defenses (grouped bar chart)
- **`fig2_asr_heatmap.png`**: ASR heatmap: models × languages × defenses
- **`fig3_per_model_defense_comparison.png`**: Per-model grouped bar chart showing all languages
- **`fig4_asr_reduction.png`**: ASR reduction from baseline to MultiStruQ per language
- **`fig5_radar_vulnerability.png`**: Radar chart showing language vulnerability profiles
- **`fig6_language_categories.png`**: Defense effectiveness by language category
- **`fig7_attack_distribution_pie.png`**: Pie charts showing distribution of successful attacks
- **`fig8_defense_progression.png`**: Line chart showing defense progression across methods
- **`fig9_before_after.png`**: Before/after comparison: Baseline vs MultiStruQ

---
*Report generated automatically from experimental results.*