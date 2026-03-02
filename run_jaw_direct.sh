#!/bin/bash
#SBATCH --job-name=saxnerf_jaw
#SBATCH --partition=defq
#SBATCH --gres=gpu:1
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/jaw_inference_%j.out
#SBATCH --error=logs/jaw_inference_%j.err

mkdir -p logs

echo "=========================================="
echo "Job started at: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Running on node: $(hostname)"
echo "=========================================="

# Set CUDA paths (CUDA 12.2 on DGX)
export CUDA_HOME=/usr/local/cuda-12.2
export PATH=/usr/local/cuda-12.2/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH

# Use conda environment directly without module
CONDA_ENV="/home/67070309/.conda/envs/sax_nerf"
export PATH="$CONDA_ENV/bin:$PATH"
export LD_LIBRARY_PATH="$CONDA_ENV/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$CONDA_ENV/lib/python3.9/site-packages:$PYTHONPATH"

cd /home/67070309/eak_project/SAX-NeRF

echo ""
echo "Environment Information:"
echo "Python: $(which python)"
python --version
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
echo ""

echo "Starting SAX-NeRF inference..."
python test.py --method Lineformer --category jaw \
    --config config/Lineformer/jaw_50.yaml \
    --weights pretrained/jaw.tar \
    --output_path output --gpu_id 0

echo ""
echo "Job completed at: $(date)"
ls -lh output/Lineformer/jaw/ 2>/dev/null || echo "Output check failed"
