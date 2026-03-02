#!/bin/bash
#SBATCH --job-name=saxnerf_jaw
#SBATCH --partition=defq
#SBATCH --gres=gpu:1
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/jaw_inference_%j.out
#SBATCH --error=logs/jaw_inference_%j.err

# Create logs directory if it doesn't exist
mkdir -p logs

echo "=========================================="
echo "Job started at: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Running on node: $(hostname)"
echo "=========================================="

# Load required modules
module load miniconda3

# Set CUDA paths (nvcc is in /usr/bin on DGX)
export CUDA_HOME=/usr
export PATH=/usr/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Initialize conda for bash shell
eval "$(conda shell.bash hook)"

# Activate conda environment
conda activate sax_nerf

# Navigate to project directory
cd /home/67070309/eak_project/SAX-NeRF

# Print environment info
echo ""
echo "Environment Information:"
echo "Python version: $(python --version)"
echo "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "GPU device: $(python -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\")')"
echo ""

# Run inference
echo "Starting SAX-NeRF inference on jaw dataset..."
echo "=========================================="

python test.py \
    --method Lineformer \
    --category jaw \
    --config config/Lineformer/jaw_50.yaml \
    --weights pretrained/jaw.tar \
    --output_path output \
    --gpu_id 0

echo ""
echo "=========================================="
echo "Inference completed at: $(date)"
echo "Output saved to: output/Lineformer/jaw/"
echo "=========================================="

# List output directory structure
echo ""
echo "Output directory structure:"
ls -lh output/Lineformer/jaw/ 2>/dev/null || echo "Output directory not found"

echo ""
echo "Job finished successfully!"
