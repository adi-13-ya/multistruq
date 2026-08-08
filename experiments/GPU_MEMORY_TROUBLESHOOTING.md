# GPU Memory Troubleshooting Guide

## Problem: OutOfMemoryError on Kaggle T4

**Error message:**
```
OutOfMemoryError: CUDA out of memory. Tried to allocate 130.00 MiB. 
GPU 1 has a total capacity of 14.56 GiB of which 80.81 MiB is free.
```

## Root Causes

1. **Previous model still in GPU memory** (from training or another notebook)
2. **Memory fragmentation** (PyTorch doesn't release memory immediately)
3. **Multiple notebooks running** (Kaggle allows only 1 GPU session at a time)
4. **4-bit quantization during eval** (unnecessary — use FP16 instead)

---

## ✅ Solution 1: Restart Kernel (Easiest)

**On Kaggle:**
1. Click **"Restart & Clear Output"** in the notebook menu
2. Run all cells from the beginning

This clears all GPU memory.

---

## ✅ Solution 2: Clear GPU Cache in Code

Add this to **Cell 1** of your evaluation notebook:

```python
import torch
import gc

# Clear GPU cache
torch.cuda.empty_cache()
gc.collect()

print(f"GPU Memory Allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
print(f"GPU Memory Cached: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
```

And add this **before loading the model** (Cell 3):

```python
# Clear GPU memory before loading
torch.cuda.empty_cache()
gc.collect()
```

---

## ✅ Solution 3: Use FP16 Instead of 4-bit for Evaluation

**Wrong (causes OOM):**
```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,  # ← Don't use this for eval
    device_map="auto",
)
```

**Correct (works fine):**
```python
base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,  # ← Use FP16 directly
    device_map="auto",
    low_cpu_mem_usage=True,
)
```

**Why?** 
- 4-bit is for **training** (saves memory for gradients)
- For **evaluation**, FP16 is faster and uses less memory than 4-bit + adapter loading

---

## ✅ Solution 4: Check for Multiple Sessions

**On Kaggle:**
1. Go to **"Your Work"** → **"Sessions"**
2. **Stop all other GPU sessions**
3. Only run 1 GPU notebook at a time

---

## ✅ Solution 5: Use Smaller Batch Size (if still failing)

In `generate_response()`, process in smaller chunks:

```python
def generate_response(prompt, max_tokens=50):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]

    # Clear cache before generation
    torch.cuda.empty_cache()
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = outputs[0][input_len:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    
    # Clear cache after generation
    del inputs, outputs
    torch.cuda.empty_cache()
    
    return response
```

---

## Memory Usage Reference

| Model | Precision | Size | T4 GPU (15 GB) |
|-------|-----------|------|----------------|
| Qwen2.5-7B | FP32 | ~28 GB | ❌ Won't fit |
| Qwen2.5-7B | FP16 | ~14 GB | ✅ Fits |
| Qwen2.5-7B | 4-bit | ~4 GB | ✅ Fits (but slower for eval) |
| Qwen2.5-7B + LoRA | FP16 | ~14.5 GB | ✅ Fits |

---

## Expected Memory Usage (FP16)

```
Cell 1 (imports):           ~0.5 GB
Cell 3 (load model):        ~14 GB
Cell 6 (inference):         ~14.5 GB (peak during generation)
```

**Total peak: ~14.5 GB / 15 GB available** ✅

---

## Quick Checklist

Before running evaluation:
- [ ] Restart kernel
- [ ] Stop other GPU sessions
- [ ] Use `torch_dtype=torch.float16` (not 4-bit)
- [ ] Add `torch.cuda.empty_cache()` in Cell 1 and Cell 3
- [ ] Use `low_cpu_mem_usage=True`
- [ ] Set `max_new_tokens=50` (not 100)

---

## If Still Failing

**Option 1:** Use Google Colab T4 (same 15 GB GPU)
**Option 2:** Use Kaggle P100 (16 GB, paid tier)
**Option 3:** Reduce eval dataset to 200 samples temporarily

---

## Updated Notebooks

I've already updated:
- `test-qwen-multistruq.ipynb` (Cell 1 and Cell 3)
- `test-llama3.1-8b-multistruq.ipynb` (Cell 1 and Cell 3)
- `test-mistral-7b-multistruq.ipynb` (Cell 1 and Cell 3)

All now include GPU memory clearing and FP16 loading.
