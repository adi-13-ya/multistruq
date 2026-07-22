# Kaggle Notebooks

## Files

### 1. baseline_evaluation.ipynb
**Stage 4**: Evaluate undefended model against multilingual attacks

- Load Gemma-2-2b-it
- Run evaluation on 71 attack samples
- Calculate baseline ASR
- Save results

### 2. training.ipynb
**Stage 5**: Train MultiStruQ defense using QLoRA

- Load base model with 4-bit quantization
- Add LoRA adapters
- Train on 1,000 samples (50% clean, 50% attacked)
- Save trained model to Hugging Face

### 3. final_evaluation.ipynb
**Stage 6**: Evaluate MultiStruQ defense

- Load trained model
- Run evaluation on same 71 attack samples
- Compare with baseline
- Generate final results

## Running on Kaggle

1. Create new notebook
2. Enable GPU (T4 x2)
3. Add dataset: `multistruq-multilingual-dataset`
4. Copy-paste cells from notebook
5. Run all cells
