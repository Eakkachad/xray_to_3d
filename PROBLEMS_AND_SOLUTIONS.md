# สรุปปัญหาและการแก้ไข - SAX-NeRF บน DGX KMITL

## 📊 สถานะปัญหา

| # | ปัญหา | สถานะ | วิธีแก้ |
|---|-------|-------|---------|
| 1 | Conda activation ใน SLURM | ✅ แก้แล้ว | ใช้ PATH โดยตรง |
| 2 | CUDA compiler ไม่พบใน batch job | ✅ แก้แล้ว | ใช้ CUDA 12.2 path |
| 3 | salloc ไม่ auto-SSH ไป compute node | ⚠️ พบแล้ว | ต้อง SSH dgx01 ด้วยตัวเอง |

---

## ✅ ปัญหาที่ 1: Conda Environment ไม่ Active ใน SLURM

### อาการ
```bash
Python version: Python 3.8.10  # ควรเป็น 3.9
ModuleNotFoundError: No module named 'torch'
```

### สาเหตุ  
- `source activate` และ `conda activate` ไม่ทำงานใน SLURM batch script
- Shell environment ไม่ถูก initialize อย่างถูกต้อง

### วิธีแก้ ✅
```bash
# แทนที่จะใช้ conda activate
CONDA_ENV="/home/67070309/.conda/envs/sax_nerf"
export PATH="$CONDA_ENV/bin:$PATH"
export LD_LIBRARY_PATH="$CONDA_ENV/lib:$LD_LIBRARY_PATH"
```

---

## ✅ ปัญหาที่ 2: CUDA Compiler ไม่พบใน Batch Job

### อาการ
```bash
/bin/sh: /usr/bin/nvcc: No such file or directory
RuntimeError: Error building extension '_hash_encoder'
```

### สาเหตุรากลึก
กำลังสู้กับปัญหานี้:
1. **PyTorch ต้องการ compile hash encoder แบบ JIT** (Just-In-Time) ตอนรัน
2. บน DGX01:
   - ❌ `/usr/bin/nvcc` ไม่มี
   - ✅ ` /usr/local/cuda-12.2/bin/nvcc` มี (CUDA 12.2)
3. **PyTorch มองหา nvcc ที่ผิดที่:**
   - Default: หา `/usr/bin/nvcc`
   - ต้องการ: `/usr/local/cuda-12.2/bin/nvcc`

### วิธีแก้ ✅
```bash
# ตั้งค่า CUDA paths ให้ถูกต้อง
export CUDA_HOME=/usr/local/cuda-12.2
export PATH="/usr/local/cuda-12.2/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH"
```

### ผลลัพธ์
```
✓ Hash encoder compiled successfully!
```

---

## ⚠️ ปัญหาที่ 3: SLURM Interactive Session

### อาการ
```bash
salloc --partition=defq --gres=gpu:1
# หลังได้ allocation แล้ว
hostname  # ยังอยู่ bright01 ไม่ใช่ dgx01
nvidia-smi  # Command not found
```

### สาเหตุ
`salloc` แค่จอง resource แต่ไม่ auto-SSH ไปยัง compute node

### วิธีแก้
```bash
# หลัง salloc สำเร็จ ต้อง SSH ด้วยตัวเอง
ssh dgx01
```

---

## 🔧 SLURM Script ที่ถูกต้อง

```bash
#!/bin/bash
#SBATCH --job-name=saxnerf_jaw
#SBATCH --partition=defq
#SBATCH --gres=gpu:1  
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/jaw_inference_%j.out
#SBATCH --error=logs/jaw_inference_%j.err

mkdir -p logs

echo "Job started: $(date)"
echo "Node: $(hostname)"

# ✅ ตั้งค่า CUDA paths (สำคัญมาก!)
export CUDA_HOME=/usr/local/cuda-12.2
export PATH="/usr/local/cuda-12.2/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH"

# ✅ ใช้ PATH ไปยัง conda environment โดยตรง
CONDA_ENV="/home/67070309/.conda/envs/sax_nerf"
export PATH="$CONDA_ENV/bin:$PATH"
export LD_LIBRARY_PATH="$CONDA_ENV/lib:$LD_LIBRARY_PATH"

# เข้าไปยัง project directory
cd /home/67070309/eak_project/SAX-NeRF

# รัน inference
python test.py \
    --method Lineformer \
    --category jaw \
    --config config/Lineformer/jaw_50.yaml \
    --weights pretrained/jaw.tar \
    --output_path output \
    --gpu_id 0

echo "Job completed: $(date)"
```

---

## 📚 บทเรียน

1. **CUDA path ต้องถูกต้อง:** DGX ใช้ `/usr/local/cuda-12.2` ไม่ใช่ `/usr/bin`
2. **Conda ใน SLURM:** ใช้ PATH โดยตรงแทน activation
3. **Interactive session:** ต้อง SSH เข้า compute node เอง
4. **Hash encoder:** Compile แบบ JIT แรกครั้ง แล้ว cache ไว้ (ครั้งต่อไปจะเร็วขึ้น)

---

## 🎯 พร้อมแล้วสำหรับ

✅ Environment setup ครบ   
✅ CUDA paths ถูกต้อง  
✅ Hash encoder compile สำเร็จ  
✅ GPU accessible (8x A100 80GB)

**ขั้นตอนต่อไป:** Submit job เพื่อรัน inference บนข้อมูลกระดูก (jaw)
