# Quick Start Guide

Get started with the EC Product Image Generator in minutes!

## Prerequisites

1. Python 3.8 or higher
2. Internet connection (for downloading models and API calls)

## Installation Steps

### Step 1: Install Base Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Stable Diffusion (Required for Image Generation)

```bash
# For CPU (works everywhere, slower)
pip install torch torchvision torchaudio

# For GPU (NVIDIA only, much faster)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Then install Stable Diffusion
pip install diffusers transformers accelerate
```

**Note**: First run will download the Stable Diffusion model (~4GB). This happens automatically.

### Step 3: Verify Installation

```bash
python -c "from diffusers import StableDiffusionPipeline; print('✓ Stable Diffusion ready')"
python -c "from openai import OpenAI; print('✓ OpenAI ready')"
```

## Quick Test

### Test 1: Command Line

```bash
python main.py --prompt "a football on green grass" --platform amazon --output test.jpg
```

This will:
1. Use OpenAI to enhance your prompt
2. Generate image with Stable Diffusion
3. Apply Amazon template
4. Run quality checks
5. Save to `test.jpg`

Check the `logs/` directory for detailed logs!

### Test 2: GUI

```bash
python gui_app.py
```

1. Enter prompt: "Modern smartphone on white background"
2. Select platform: Amazon
3. Click "Generate Image"
4. Wait for generation (first time takes longer)
5. Review quality report
6. Save image

## Understanding the Logs

Logs are saved in `logs/` directory with timestamps. Each run creates a new log file.

**Log Levels:**
- `DEBUG`: Very detailed information (every step)
- `INFO`: Important milestones (default)
- `WARNING`: Non-critical issues
- `ERROR`: Errors that need attention

**View logs:**
```bash
# Windows
type logs\ec_image_generator_*.log | more

# Linux/Mac  
tail -f logs/ec_image_generator_*.log
```

## Common First-Run Issues

### Issue: "Model download failed"
**Solution**: Check internet connection. The model is ~4GB and may take 10-20 minutes to download.

### Issue: "CUDA out of memory"
**Solution**: The system will automatically fall back to CPU. It's slower but works.

### Issue: "OpenAI API error"
**Solution**: Check that `.env` file exists and contains the API key.

## Next Steps

1. **Read the logs**: Check `logs/` directory to see what's happening
2. **Try different prompts**: Experiment with different product descriptions
3. **Add Japanese text**: Use the `--title` and `--price` options
4. **Try different platforms**: Test Rakuten, Yahoo, Mercari templates
5. **Experiment with patterns**: Use `--pattern` to try different layouts

## Getting Help

1. Check logs in `logs/` directory
2. Use `--log-level DEBUG` for more details
3. Review README.md for full documentation

## Example Commands

```bash
# Simple generation
python main.py --prompt "football game" --platform amazon --output football.jpg

# With Japanese text
python main.py --prompt "スマートフォン" --platform rakuten --title "最新モデル" --price "¥49,800" --output phone.jpg

# Debug mode (very detailed logs)
python main.py --prompt "test" --platform amazon --output test.jpg --log-level DEBUG

# Skip OpenAI (use built-in enhancement)
python main.py --prompt "test" --platform amazon --output test.jpg --no-openai
```

Enjoy generating EC product images! 🎨

