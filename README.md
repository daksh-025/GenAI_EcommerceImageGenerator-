# EC Product Image Generator with AI

A comprehensive system for generating e-commerce product images using generative AI (OpenAI + Stable Diffusion) with automatic Japanese text embedding and template optimization for multiple EC platforms.

## Features

- **AI Image Generation**: Integration with OpenAI (ChatGPT) for prompt enhancement and Stable Diffusion for image generation
- **Japanese Text Embedding**: Accurate Japanese text rendering using font embedding and layer composition
- **Multi-Platform Templates**: Automatic optimization for Rakuten, Amazon, Yahoo Shopping, and Mercari
- **Quality Verification**: Automatic checking for character collapse, color saturation, and resolution
- **GUI Interface**: User-friendly operation panel for non-engineers
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Reproducibility**: Template-based system ensuring consistent output quality

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Stable Diffusion Dependencies

For image generation, you need PyTorch and Stable Diffusion:

```bash
# For CPU (works on any computer, slower)
pip install torch torchvision torchaudio

# For GPU (NVIDIA CUDA, much faster)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Then install Stable Diffusion:
```bash
pip install diffusers transformers accelerate
```

### 3. Configure API Keys

The `.env` file already contains the OpenAI API key. If you need to update it:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_key_here"

# Linux/Mac
export OPENAI_API_KEY="your_key_here"
```

**Note**: LOVART does not have an API, so the system uses Stable Diffusion for actual image generation. The OpenAI API is used for intelligent prompt enhancement.

## Usage

### GUI Mode (Recommended for Non-Engineers)

```bash
python gui_app.py
```

1. Enter your product prompt
2. Select platform (Amazon, Rakuten, Yahoo, Mercari)
3. Optionally add text elements (title, price, tagline)
4. Click "Generate Image"
5. Review quality report
6. Save the image

### Command Line Mode

#### Basic Usage
```bash
python main.py --prompt "Modern smartphone on white background" --platform amazon --output product.jpg
```

#### With Japanese Text
```bash
python main.py \
  --prompt "Modern smartphone on white background" \
  --platform rakuten \
  --title "スマートフォン Pro" \
  --price "¥49,800" \
  --tagline "SALE 30% OFF" \
  --output product.jpg
```

#### Advanced Options
```bash
python main.py \
  --prompt "Product description" \
  --platform amazon \
  --pattern centered \
  --output product.jpg \
  --auto-fix \
  --log-level DEBUG
```

## Project Structure

- `main.py`: Main application entry point
- `gui_app.py`: GUI interface
- `image_generator.py`: AI image generation (Stable Diffusion)
- `openai_enhancer.py`: OpenAI prompt enhancement
- `text_compositor.py`: Japanese text layer composition
- `template_manager.py`: EC platform template management
- `quality_checker.py`: Image quality verification
- `config.py`: Configuration management
- `logger_config.py`: Logging setup
- `logs/`: Log files directory (created automatically)
- `fonts/`: Japanese font files
- `output/`: Generated images directory

## Logging

The system includes comprehensive logging:

- **Log Files**: Saved in `logs/` directory with timestamps
- **Console Output**: Real-time status updates
- **Log Levels**: DEBUG, INFO, WARNING, ERROR

View logs:
```bash
# Windows
type logs\ec_image_generator_*.log

# Linux/Mac
cat logs/ec_image_generator_*.log
```

## Configuration

Edit `config.py` to customize:
- Platform-specific settings
- Image generation parameters
- Text rendering options
- Quality thresholds
- Template patterns

## Platform Support

- **Rakuten**: 1000x1000px, 10% margin, 800x800px minimum
- **Amazon**: 1000x1000px, 15% margin, 1000x1000px minimum
- **Yahoo Shopping**: 1000x1000px, 12% margin, 800x800px minimum
- **Mercari**: 1000x1000px, 10% margin, 640x640px minimum

## Layout Patterns

- **centered**: Product and text centered
- **left_aligned**: Product on left, text left-aligned
- **right_aligned**: Product on right, text right-aligned
- **top_heavy**: Product in upper area
- **bottom_heavy**: Product in lower area

## Troubleshooting

### "Stable Diffusion dependencies not installed"
```bash
pip install torch diffusers transformers accelerate
```

### "OpenAI API key not found"
- Check `.env` file exists and contains `OPENAI_API_KEY`
- Or set environment variable manually

### "CUDA out of memory"
- Reduce image size in config
- Use CPU mode (slower but works)
- Close other GPU applications

### Generation is slow
- First run downloads model (~4GB)
- Use GPU if available (much faster)
- Reduce `num_inference_steps` in config

## License

MIT License

