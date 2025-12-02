# Fixing PyTorch Compatibility Error

## Error Message
```
RuntimeError: module 'torch' has no attribute 'float8_e4m3fn'
```

## Cause
This error occurs when there's a version mismatch between PyTorch and diffusers. The installed PyTorch version is too old for the diffusers version being used.

## Solution

### Option 1: Automatic Fix (Recommended)

Run the fix script:
```bash
python fix_torch_compatibility.py
```

This will:
1. Uninstall conflicting packages
2. Install compatible versions (PyTorch 2.1.0 + compatible diffusers)
3. Verify the installation

### Option 2: Manual Fix

#### Step 1: Uninstall existing packages
```bash
pip uninstall -y torch torchvision torchaudio diffusers transformers accelerate
```

#### Step 2: Install compatible versions

**For CUDA (NVIDIA GPU):**
```bash
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
pip install diffusers>=0.21.0,<0.30.0 transformers>=4.30.0,<5.0.0 accelerate>=0.20.0
```

**For CPU only:**
```bash
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0
pip install diffusers>=0.21.0,<0.30.0 transformers>=4.30.0,<5.0.0 accelerate>=0.20.0
```

#### Step 3: Verify installation
```bash
python -c "import torch; import diffusers; print(f'PyTorch: {torch.__version__}'); print(f'diffusers: {diffusers.__version__}')"
```

### Option 3: Upgrade PyTorch (Alternative)

If you want to use the latest versions:
```bash
# Uninstall old versions
pip uninstall -y torch torchvision torchaudio

# Install latest (may require CUDA 11.8+)
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or for CPU
pip install --upgrade torch torchvision torchaudio
```

## Recommended Versions

For best compatibility, use:
- **PyTorch**: 2.1.0 or 2.2.0
- **diffusers**: 0.21.0 to 0.29.0
- **transformers**: 4.30.0 to 4.40.0

## After Fixing

Test the installation:
```bash
python main.py --prompt "test" --platform amazon --output test.jpg --no-quality-check
```

## Still Having Issues?

1. Check Python version (requires 3.8+):
   ```bash
   python --version
   ```

2. Check if CUDA is available (for GPU):
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. Clear pip cache:
   ```bash
   pip cache purge
   ```

4. Create a fresh virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

## Notes

- The fix script (`fix_torch_compatibility.py`) handles all of this automatically
- Installation may take 10-20 minutes depending on your internet speed
- First run will download the Stable Diffusion model (~4GB)

