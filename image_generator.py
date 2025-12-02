"""
AI Image Generation Module
Supports Stable Diffusion (LOVART API not available)
"""
import os
import logging
from typing import Optional, Tuple
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Base class for AI image generation"""
    
    def __init__(self, model_type: str = 'stable_diffusion', api_key: Optional[str] = None):
        """
        Initialize image generator
        
        Args:
            model_type: Type of model ('stable_diffusion', 'lovart' - note: LOVART has no API)
            api_key: API key for the service (if required)
        """
        self.model_type = model_type
        self.api_key = api_key
        self.pipeline = None
        
        logger.info(f"Initializing ImageGenerator with model: {model_type}")
        
        if model_type == 'lovart':
            logger.warning("LOVART API is not available. Falling back to Stable Diffusion.")
            self.model_type = 'stable_diffusion'
    
    def _load_stable_diffusion_pipeline(self):
        """Load Stable Diffusion pipeline (lazy loading)"""
        if self.pipeline is not None:
            return self.pipeline
        
        try:
            logger.info("Loading Stable Diffusion pipeline...")
            import torch
            
            # Check PyTorch version compatibility
            torch_version = torch.__version__
            logger.debug(f"PyTorch version: {torch_version}")
            
            # Import diffusers with error handling
            try:
                from diffusers import StableDiffusionPipeline
            except RuntimeError as e:
                if "float8_e4m3fn" in str(e):
                    logger.error("PyTorch version incompatibility detected!")
                    logger.error("Please upgrade PyTorch: pip install --upgrade torch torchvision torchaudio")
                    logger.error("Or use compatible versions: pip install torch==2.1.0 torchvision==0.16.0")
                    raise RuntimeError(
                        "PyTorch version too old. Please upgrade:\n"
                        "pip install --upgrade torch torchvision torchaudio\n"
                        "Or reinstall compatible versions:\n"
                        "pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0"
                    ) from e
                raise
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            model_id = "runwayml/stable-diffusion-v1-5"
            logger.debug(f"Loading model: {model_id}")
            
            # Use float32 for CPU, float16 for CUDA (if supported)
            if device == "cuda" and torch.cuda.is_available():
                try:
                    dtype = torch.float16
                    logger.debug("Using float16 for CUDA")
                except:
                    dtype = torch.float32
                    logger.debug("Falling back to float32 for CUDA")
            else:
                dtype = torch.float32
                logger.debug("Using float32 for CPU")
            
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=dtype
            )
            self.pipeline = self.pipeline.to(device)
            
            # Enable memory efficient attention if available
            if hasattr(self.pipeline, 'enable_attention_slicing'):
                self.pipeline.enable_attention_slicing()
                logger.debug("Enabled attention slicing for memory efficiency")
            
            logger.info("Stable Diffusion pipeline loaded successfully")
            return self.pipeline
            
        except ImportError as e:
            logger.error(f"Stable Diffusion dependencies not installed: {e}")
            logger.error("Install with: pip install torch diffusers transformers accelerate")
            raise
        except RuntimeError as e:
            # Re-raise RuntimeError with better message
            raise
        except Exception as e:
            logger.error(f"Failed to load Stable Diffusion pipeline: {e}", exc_info=True)
            raise
    
    def generate(
        self, 
        prompt: str, 
        size: Tuple[int, int] = (1000, 1000),
        negative_prompt: Optional[str] = None,
        num_steps: int = 50,
        guidance_scale: float = 7.5
    ) -> Image.Image:
        """
        Generate image from prompt
        
        Args:
            prompt: Text prompt describing the image
            size: Output image size (width, height)
            negative_prompt: Negative prompt to avoid certain elements
            num_steps: Number of inference steps
            guidance_scale: Guidance scale for generation
            
        Returns:
            Generated PIL Image
        """
        logger.info(f"Generating image with prompt: '{prompt[:50]}...'")
        logger.debug(f"Parameters: size={size}, steps={num_steps}, guidance={guidance_scale}")
        
        if self.model_type == 'stable_diffusion':
            return self._generate_stable_diffusion(prompt, size, negative_prompt, num_steps, guidance_scale)
        elif self.model_type == 'lovart':
            logger.warning("LOVART API not available. Using Stable Diffusion instead.")
            return self._generate_stable_diffusion(prompt, size, negative_prompt, num_steps, guidance_scale)
        else:
            logger.error(f"Unsupported model type: {self.model_type}")
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _generate_stable_diffusion(
        self, 
        prompt: str, 
        size: Tuple[int, int],
        negative_prompt: Optional[str],
        num_steps: int,
        guidance_scale: float
    ) -> Image.Image:
        """
        Generate image using Stable Diffusion
        
        Note: This implementation uses diffusers library.
        Requires torch and transformers to be installed.
        """
        logger.info("Starting Stable Diffusion image generation...")
        
        try:
            pipeline = self._load_stable_diffusion_pipeline()
            
            negative_prompt_text = negative_prompt or "text, watermark, low quality, distorted, blurry, bad anatomy"
            logger.debug(f"Negative prompt: {negative_prompt_text[:100]}...")
            
            logger.info(f"Generating image (this may take a while, {num_steps} steps)...")
            result = pipeline(
                prompt,
                negative_prompt=negative_prompt_text,
                width=size[0],
                height=size[1],
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale
            )
            
            image = result.images[0]
            logger.info(f"Image generated successfully. Size: {image.size}")
            return image
            
        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {e}", exc_info=True)
            raise
    
    def enhance_prompt_for_japanese(
        self, 
        base_prompt: str,
        include_layout: bool = True,
        include_style: bool = True
    ) -> tuple:
        """
        Enhance prompt with Japanese-specific instructions and layout hints
        
        Args:
            base_prompt: Base product description prompt
            include_layout: Whether to include layout instructions
            include_style: Whether to include style instructions
            
        Returns:
            Tuple of (enhanced_prompt, negative_prompt)
        """
        logger.debug("Enhancing prompt for Japanese/EC optimization")
        enhanced = base_prompt
        
        if include_style:
            enhanced += ", high quality, professional product photography, clean background, studio lighting"
        
        if include_layout:
            enhanced += ", centered composition, product focus, e-commerce ready"
        
        # Add negative prompts to avoid text artifacts
        negative = "no text, no watermark, no characters, no letters, clean design, no writing"
        
        logger.debug(f"Enhanced prompt length: {len(enhanced)} characters")
        return enhanced, negative

