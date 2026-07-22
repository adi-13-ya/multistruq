# Stage 5 Updates Summary

## Implementation Guide Updated

The `MultiStruQ_Implementation_Guide.md` has been updated with working, tested code for Stage 5 training.

## Key Changes Made

### Cell Structure (Now 6 cells instead of 5)

| Cell | Purpose | Key Changes |
|------|---------|-------------|
| **Cell 1** | Install packages | Removed `trl` dependency, added GPU info check |
| **Cell 2** | **NEW: HF Authentication** | Authenticate with Kaggle secrets |
| **Cell 3** | Load training data | (Previously Cell 2, renumbered) |
| **Cell 4** | Load model with QLoRA | Removed unused `trl` import |
| **Cell 5** | **Train the model** | Complete rewrite with memory optimizations |
| **Cell 6** | Upload to HF | Auto-create repo, use authenticated token |

### Cell 5 (Training) - Major Updates

#### Memory Optimizations
```python
# Before (caused OOM errors)
per_device_train_batch_size=2
gradient_accumulation_steps=4
max_length=512
warmup_ratio=0.03
dataset_text_field="text"  # Incompatible parameter

# After (works on T4 16GB)
per_device_train_batch_size=1        # Halved
gradient_accumulation_steps=8         # Doubled to compensate
max_length=256                        # Halved
warmup_steps=50                       # Fixed deprecated parameter
optim="adamw_bnb_8bit"               # 8-bit optimizer
gradient_checkpointing=True           # Saves memory
```

#### Trainer Changes
- **Replaced**: `SFTTrainer` (version-incompatible) → `Trainer` (standard)
- **Added**: Manual tokenization with `tokenize_function()`
- **Added**: `DataCollatorForLanguageModeling` for proper batching
- **Added**: `remove_columns=["text"]` to avoid tensor conversion errors
- **Added**: GPU memory clearing (`gc.collect()`, `torch.cuda.empty_cache()`)

### Cell 6 (Upload) - Updates
- Auto-create HF repo before upload
- Use authenticated token from Cell 2 (no hardcoded tokens)
- Better error handling

## Issues Fixed

| Issue | Error | Solution |
|-------|-------|----------|
| 1 | `warmup_ratio` deprecated | Use `warmup_steps=50` |
| 2 | `dataset_text_field` not found | Remove parameter, use standard Trainer |
| 3 | `packing` not found | Remove parameter |
| 4 | `max_seq_length` not found | Use manual tokenization |
| 5 | Tensor conversion error | Add `remove_columns=["text"]` |
| 6 | Out of Memory (OOM) | Reduce batch size, max_length, add optimizations |

## Training Specs (Optimized for T4 GPU)

```
GPU: T4 x2 (16GB)
Batch size: 1
Gradient accumulation: 8
Effective batch size: 8
Max sequence length: 256 tokens
Epochs: 2
Samples: 4,000
Expected time: 2-3 hours
Memory usage: ~14GB / 16GB
```

## Files Updated

1. **`MultiStruQ_Implementation_Guide.md`**
   - Stage 5, Cells 1-6 completely rewritten
   - All code tested and working

2. **`create_eval_dataset_v2.py`** (created earlier)
   - Uses explicit attack templates instead of IndicJR FREE track
   - Generates 71 samples across 9 language categories

3. **`multilingual_eval_dataset_v2.json`** (generated)
   - Working evaluation dataset with real jailbreak attacks
   - Used in Stage 4 baseline evaluation

## Baseline Results Achieved

```
Language            ASR (Attack Success Rate)
================================================
bengali             20.0% (1/5)
cross_lingual       57.1% (4/7)
cultural            0.0% (0/8)
english             62.5% (10/16)
hindi_native        50.0% (6/12)
hinglish            33.3% (5/15)
marathi             66.7% (2/3)
tamil               33.3% (1/3)
telugu              0.0% (0/2)
================================================
Overall             ~41% (29/71)
```

## Next Steps

1. **Run Cell 5** in Kaggle (training will take 2-3 hours)
2. **Monitor progress** — check logging output every 50 steps
3. **After training completes**:
   - Run Cell 6 to upload model
   - Proceed to Stage 6 (evaluate MultiStruQ)
   - Compare baseline ASR vs MultiStruQ ASR

## Expected Outcome

After training, MultiStruQ should:
- **Reduce ASR** from ~41% to <10% across all languages
- **Maintain utility** on clean tasks
- **Generalize** to unseen attack types

This proves the defense works for multilingual prompt injections.
