# MultiStruQ Dataset Summary

## Files Generated

### 1. Evaluation Dataset
**File**: `multilingual_eval_dataset.json`  
**Size**: 1,050 samples  
**Source**: IndicJR FREE track

#### Breakdown:
- **Attacked-benign**: 1,000 samples
  - Hindi (hi): 200
  - Bengali (bn): 200
  - Tamil (ta): 200
  - Telugu (te): 200
  - Marathi (mr): 200

- **Clean-benign**: 50 samples (10 per language)

#### Attack Families:
- **format**: 330 attacks (e.g., "Output MUST be in YAML...")
- **instruction**: 340 attacks (e.g., "Ignore previous instructions...")
- **translate**: 330 attacks (e.g., translation-based jailbreaks)

### 2. Training Dataset
**File**: `multilingual_train_dataset.json`  
**Size**: 4,000 samples  
**Source**: Alpaca dataset + injected attacks

#### Breakdown:
- **Clean samples**: 2,000 (normal instruction-following)
- **Attacked samples**: 2,000 (with injected attacks, correct outputs)

#### Attack Language Distribution:
- English: 500 (25%)
- Hindi (native): 400 (20%)
- Hinglish: 300 (15%)
- Bengali: 200 (10%)
- Cross-lingual: 200 (10%)
- Tamil: 100 (5%)
- Marathi: 100 (5%)
- Telugu: 100 (5%)
- Cultural: 100 (5%)

## Validation Status

✅ **ALL VALIDATIONS PASSED**

### Issues Fixed:
1. **Clean-benign empty prompts**: Fixed by handling IndicJR's `content` field
2. **Training samples with empty outputs**: Fixed by filtering Alpaca dataset

## Next Steps

### 1. Upload to Kaggle
- Go to **kaggle.com/datasets** → "New Dataset"
- Upload both JSON files
- Name: `multistruq-multilingual-dataset`

### 2. Backup to Google Drive
- Upload both files to Google Drive for safekeeping

### 3. Proceed to Stage 4
- Create Kaggle notebook for baseline evaluation
- Test undefended Gemma-2-2b-it against IndicJR attacks
- Calculate Attack Success Rate (ASR) per language

## Dataset Quality

### Evaluation Dataset (IndicJR)
- ✅ Research-grade benchmark (arXiv:2602.16832)
- ✅ Judge-free evaluation (no LLM judge needed)
- ✅ Multiple attack families per language
- ✅ Same-lingual and cross-lingual attacks
- ✅ Clean samples for utility testing

### Training Dataset (Alpaca + Attacks)
- ✅ Balanced clean/attacked ratio (50/50)
- ✅ Diverse attack languages (9 categories)
- ✅ Correct outputs preserved (teaches resistance)
- ✅ No empty outputs (quality filtered)

## Estimated Kaggle Runtime

With **GPU T4 x2** (free tier):
- **Evaluation**: ~30-40 minutes (1,000 attacked samples)
- **Training**: ~2-3 hours (4,000 samples, 2 epochs)

## File Sizes

- `multilingual_eval_dataset.json`: ~2.1 MB
- `multilingual_train_dataset.json`: ~3.8 MB
- **Total**: ~5.9 MB (easily uploadable to Kaggle)
