"""
OpenAI (ChatGPT) Integration for Prompt Enhancement
Uses OpenAI API to enhance and optimize prompts for image generation
"""
import os
import logging
from typing import Optional
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)

class OpenAIPromptEnhancer:
    """Uses OpenAI ChatGPT to enhance prompts for better image generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI prompt enhancer
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Prompt enhancement will be disabled.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def enhance_prompt(
        self,
        base_prompt: str,
        product_type: Optional[str] = None,
        style_preferences: Optional[str] = None,
        target_platform: Optional[str] = None
    ) -> str:
        """
        Use ChatGPT to enhance the prompt for better image generation
        
        Args:
            base_prompt: Original user prompt
            product_type: Type of product (optional)
            style_preferences: Style preferences (optional)
            target_platform: Target EC platform (optional)
            
        Returns:
            Enhanced prompt optimized for image generation
        """
        if not self.client:
            logger.warning("OpenAI client not available. Using base prompt without enhancement.")
            return base_prompt
        
        logger.info(f"Enhancing prompt with OpenAI: '{base_prompt[:50]}...'")
        
        # Build enhancement request
        system_prompt = """You are an expert at creating prompts for AI image generation. 
Your task is to enhance product description prompts to generate high-quality, 
e-commerce-ready product images. Focus on:
- Clear, detailed product description
- Professional photography style
- Clean, white or neutral backgrounds
- Optimal studio lighting
- E-commerce presentation quality
- Avoid text in the image (text will be added separately)
- High resolution, sharp details
Return only the enhanced prompt, no explanations or additional text."""
        
        user_prompt = f"Enhance this product image prompt for AI image generation:\n\n{base_prompt}"
        
        if product_type:
            user_prompt += f"\n\nProduct type: {product_type}"
        if style_preferences:
            user_prompt += f"\n\nStyle preferences: {style_preferences}"
        if target_platform:
            user_prompt += f"\n\nTarget platform: {target_platform}"
        
        try:
            logger.debug(f"Sending request to OpenAI API (model: {Config.OPENAI['model']})")
            response = self.client.chat.completions.create(
                model=Config.OPENAI['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=Config.OPENAI['max_tokens'],
                temperature=Config.OPENAI['temperature']
            )
            
            enhanced = response.choices[0].message.content.strip()
            logger.info(f"Prompt enhanced successfully. Length: {len(enhanced)} characters")
            logger.debug(f"Enhanced prompt: {enhanced}")
            return enhanced
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            logger.warning("Falling back to base prompt")
            return base_prompt
    
    def generate_negative_prompt(
        self,
        base_prompt: str
    ) -> str:
        """
        Use ChatGPT to generate an effective negative prompt
        
        Args:
            base_prompt: Original prompt
            
        Returns:
            Negative prompt to avoid unwanted elements
        """
        if not self.client:
            logger.debug("OpenAI not available, using default negative prompt")
            return "text, watermark, low quality, distorted, blurry, bad anatomy, extra limbs"
        
        logger.info("Generating negative prompt with OpenAI")
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI['model'],
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating negative prompts for AI image generation. Generate a concise negative prompt that will prevent unwanted elements in the image."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a negative prompt for this image description: {base_prompt}\n\nFocus on avoiding: text, watermarks, low quality, distortions, unwanted objects, bad anatomy. Return only the negative prompt, comma-separated, no explanations."
                    }
                ],
                max_tokens=100,
                temperature=0.5
            )
            
            negative = response.choices[0].message.content.strip()
            logger.info(f"Negative prompt generated: {negative[:100]}...")
            return negative
            
        except Exception as e:
            logger.error(f"OpenAI negative prompt generation failed: {e}")
            return "text, watermark, low quality, distorted, blurry, bad anatomy, extra limbs"

