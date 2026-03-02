#!/bin/bash
set -e

echo "=========================================="
echo "  SAX-NeRF Web Application — Setup"
echo "=========================================="
echo ""

# ── 1. Check conda ──
if ! command -v conda &> /dev/null; then
    echo "❌ conda not found. Please install Miniconda/Anaconda first."
    echo "   https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi
echo "✓ conda found"

# ── 2. Create/activate conda env ──
ENV_NAME="sax_nerf"
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "✓ conda env '${ENV_NAME}' already exists"
else
    echo "Creating conda env '${ENV_NAME}' (Python 3.9)..."
    conda create -n ${ENV_NAME} python=3.9 -y
fi

echo ""
echo "Activating conda env..."
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}
echo "✓ Using Python: $(python --version)"

# ── 3. Install PyTorch ──
if python -c "import torch" 2>/dev/null; then
    echo "✓ PyTorch already installed ($(python -c 'import torch; print(torch.__version__)'))"
else
    echo "Installing PyTorch (CUDA 11.3)..."
    pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 \
        --extra-index-url https://download.pytorch.org/whl/cu113
fi

# ── 4. Install SAX-NeRF core dependencies ──
echo ""
echo "Installing SAX-NeRF core dependencies..."
pip install -r requirements.txt

# ── 5. Install backend dependencies ──
echo ""
echo "Installing backend (FastAPI) dependencies..."
pip install -r server/requirements.txt

# ── 6. Install frontend dependencies ──
echo ""
if ! command -v pnpm &> /dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
fi
echo "✓ pnpm found ($(pnpm --version))"

echo "Installing frontend dependencies..."
cd web && pnpm install && cd ..

# ── 7. Create .env if not exists ──
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
else
    echo "✓ .env already exists"
fi

# ── 8. Create output directory ──
mkdir -p output/web_cache

# ── 9. Check data files ──
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""

echo "Checking required data files..."
echo ""

if ls data/*.pickle 1>/dev/null 2>&1; then
    echo "✓ Data files (.pickle) found in data/"
else
    echo "⚠ No .pickle files found in data/"
    echo "  Download from: https://drive.google.com/drive/folders/1SlneuSGkhk0nvwPjxxnpBCO59XhjGGJX"
    echo "  Place them in: $(pwd)/data/"
fi

echo ""
if ls pretrained/*.tar 1>/dev/null 2>&1; then
    echo "✓ Pretrained models (.tar) found in pretrained/"
else
    echo "⚠ No .tar files found in pretrained/"
    echo "  Download from: https://drive.google.com/drive/folders/1wlDrZQRbQENcfW1Pjrr1gasFQ8v6znHV"
    echo "  Place them in: $(pwd)/pretrained/"
fi

echo ""
echo "To start development:"
echo "  conda activate ${ENV_NAME}"
echo "  make dev"
echo ""
