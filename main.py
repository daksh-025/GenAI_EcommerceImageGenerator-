"""
Main Application Entry Point
EC Product Image Generator with AI
"""
import utils.session
import argparse
import os
import sys
import logging
from typing import Optional, Dict
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from logger_config import setup_logger
from config import Config
from image_generator import ImageGenerator
from text_compositor import TextCompositor
from template_manager import TemplateManager
from quality_checker import QualityChecker
from openai_enhancer import OpenAIPromptEnhancer

# Setup logger
logger = setup_logger("ECImageGenerator", logging.INFO)

class ECImageGenerator:
    """Main application class for EC product image generation"""
    
    def __init__(self, model_type: str = 'stable_diffusion', use_openai: bool = True):
        """
        Initialize EC Image Generator
        
        Args:
            model_type: Type of AI model to use ('stable_diffusion', 'lovart')
            use_openai: Whether to use OpenAI for prompt enhancement
        """
        logger.info("=" * 60)
        logger.info("Initializing EC Product Image Generator")
        logger.info("=" * 60)
        
        self.image_generator = ImageGenerator(model_type=model_type)
        self.text_compositor = TextCompositor()
        self.template_manager = TemplateManager()
        self.quality_checker = QualityChecker()
        
        # Initialize OpenAI if requested
        self.use_openai = use_openai
        if self.use_openai:
            self.openai_enhancer = OpenAIPromptEnhancer()
            if self.openai_enhancer.client:
                logger.info("OpenAI prompt enhancement enabled")
            else:
                logger.warning("OpenAI requested but API key not found. Using built-in enhancement.")
                self.use_openai = False
        else:
            self.openai_enhancer = None
            logger.info("Using built-in prompt enhancement (OpenAI disabled)")
    
    def generate_product_image(
        self,
        prompt: str,
        platform: str = 'amazon',
        text_elements: Optional[Dict] = None,
        pattern_name: Optional[str] = None,
        output_path: Optional[str] = None,
        run_quality_check: bool = True,
        auto_fix: bool = False
    ) -> Image.Image:
        """
        Generate complete EC product image
        
        Args:
            prompt: Product description prompt
            platform: Target EC platform ('rakuten', 'amazon', 'yahoo', 'mercari')
            text_elements: Dictionary of text elements to add
            pattern_name: Optional layout pattern name
            output_path: Optional path to save output image
            run_quality_check: Whether to run quality verification
            auto_fix: Whether to automatically fix quality issues
            
        Returns:
            Generated product image
        """
        logger.info("=" * 60)
        logger.info("Starting Product Image Generation")
        logger.info("=" * 60)
        logger.info(f"Platform: {platform}")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Pattern: {pattern_name or 'random'}")
        
        # Step 1: Get template
        logger.info("-" * 60)
        logger.info("Step 1: Template Selection")
        logger.info("-" * 60)
        template = self.template_manager.get_template(platform, pattern_name)
        logger.info(f"Selected template: {template['pattern']['name']}")
        
        # Step 2: Enhance prompt
        logger.info("-" * 60)
        logger.info("Step 2: Prompt Enhancement")
        logger.info("-" * 60)
        if self.use_openai and self.openai_enhancer and self.openai_enhancer.client:
            logger.info("Using OpenAI to enhance prompt...")
            enhanced_prompt = self.openai_enhancer.enhance_prompt(
                prompt,
                target_platform=platform
            )
            negative_prompt = self.openai_enhancer.generate_negative_prompt(prompt)
        else:
            logger.info("Using built-in prompt enhancement...")
            enhanced_prompt, negative_prompt = self.image_generator.enhance_prompt_for_japanese(
                prompt,
                include_layout=True,
                include_style=True
            )
        
        logger.info(f"Enhanced prompt: {enhanced_prompt[:100]}...")
        
        # Step 3: Generate base image
        logger.info("-" * 60)
        logger.info("Step 3: AI Image Generation")
        logger.info("-" * 60)
        logger.info("Generating base image with AI (this may take several minutes)...")
        base_image = self.image_generator.generate(
            enhanced_prompt,
            size=template['size'],
            negative_prompt=negative_prompt
        )
        logger.info(f"Base image generated: {base_image.size}")
        
        # Step 4: Apply template
        logger.info("-" * 60)
        logger.info("Step 4: Template Application")
        logger.info("-" * 60)
        templated_image = self.template_manager.apply_template_to_image(
            base_image,
            template,
            resize_product=True
        )
        logger.info("Template applied successfully")
        
        # Step 5: Composite text layers
        if text_elements:
            logger.info("-" * 60)
            logger.info("Step 5: Text Composition")
            logger.info("-" * 60)
            logger.info(f"Adding {len(text_elements)} text elements")
            # Add positions from template
            for element_name, element_data in text_elements.items():
                if element_name in template['text_positions']:
                    element_data['position'] = template['text_positions'][element_name]
                element_data.setdefault('alignment', template['pattern']['text_alignment'])
            
            final_image = self.text_compositor.composite_text_layers(
                templated_image,
                text_elements,
                template['platform_config']
            )
            logger.info("Text composition completed")
        else:
            final_image = templated_image
            logger.info("No text elements to add")
        
        # Step 6: Quality check
        if run_quality_check:
            logger.info("-" * 60)
            logger.info("Step 6: Quality Verification")
            logger.info("-" * 60)
            quality_results = self.quality_checker.check_all(final_image, platform)
            
            if not quality_results['overall']['passed']:
                logger.warning("Quality check failed!")
                logger.warning(self.quality_checker.generate_quality_report(final_image, platform))
                
                if auto_fix:
                    logger.info("Attempting to fix quality issues...")
                    final_image = self.quality_checker.fix_common_issues(final_image, quality_results)
                    # Re-check after fix
                    quality_results = self.quality_checker.check_all(final_image, platform)
                    logger.info("Quality check after fixes:")
                    logger.info(self.quality_checker.generate_quality_report(final_image, platform))
            else:
                logger.info("Quality check passed!")
                logger.info(f"Quality Score: {quality_results['overall']['score'] * 100:.1f}%")
        
        # Step 7: Save if output path specified
        if output_path:
            logger.info("-" * 60)
            logger.info("Step 7: Saving Image")
            logger.info("-" * 60)
            final_image.save(output_path, quality=95)
            logger.info(f"Image saved to: {output_path}")
        
        logger.info("=" * 60)
        logger.info("Image Generation Completed Successfully!")
        logger.info("=" * 60)
        
        return final_image
    
    def batch_generate(
        self,
        prompts: list,
        platform: str = 'amazon',
        output_dir: str = 'output',
        **kwargs
    ):
        """
        Generate multiple product images
        
        Args:
            prompts: List of product prompts
            platform: Target platform
            output_dir: Output directory
            **kwargs: Additional arguments for generate_product_image
        """
        logger.info(f"Starting batch generation: {len(prompts)} images")
        os.makedirs(output_dir, exist_ok=True)
        
        for i, prompt in enumerate(prompts):
            logger.info(f"\n{'='*60}")
            logger.info(f"Batch Item {i+1}/{len(prompts)}")
            logger.info(f"{'='*60}")
            output_path = os.path.join(output_dir, f"product_{i+1:03d}.jpg")
            self.generate_product_image(
                prompt,
                platform=platform,
                output_path=output_path,
                **kwargs
            )

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='EC Product Image Generator with AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single image
  python main.py --prompt "Modern smartphone on white background" --platform amazon --output product.jpg
  
  # Generate with text elements
  python main.py --prompt "Product description" --platform rakuten --title "商品名" --price "¥1,980" --output product.jpg
  
  # Use specific pattern
  python main.py --prompt "Product" --platform amazon --pattern centered --output product.jpg
  
  # Disable OpenAI (use built-in enhancement)
  python main.py --prompt "Product" --platform amazon --no-openai --output product.jpg
        """
    )
    
    parser.add_argument('--prompt', type=str, required=True, help='Product description prompt')
    parser.add_argument('--platform', type=str, default='amazon', 
                       choices=['rakuten', 'amazon', 'yahoo', 'mercari'],
                       help='Target EC platform')
    parser.add_argument('--model', type=str, default='stable_diffusion',
                       choices=['stable_diffusion', 'lovart'],
                       help='AI model to use (lovart falls back to stable_diffusion)')
    parser.add_argument('--pattern', type=str, help='Layout pattern name')
    parser.add_argument('--title', type=str, help='Product title text')
    parser.add_argument('--price', type=str, help='Product price text')
    parser.add_argument('--tagline', type=str, help='Tagline text (e.g., SALE 50% OFF)')
    parser.add_argument('--output', type=str, help='Output image path')
    parser.add_argument('--no-quality-check', action='store_true', help='Skip quality check')
    parser.add_argument('--auto-fix', action='store_true', help='Automatically fix quality issues')
    parser.add_argument('--no-openai', action='store_true', help='Disable OpenAI prompt enhancement')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logger with specified level
    log_level = getattr(logging, args.log_level.upper())
    setup_logger("ECImageGenerator", log_level)
    
    # Build text elements dictionary
    text_elements = {}
    if args.title:
        text_elements['title'] = {'text': args.title}
    if args.price:
        text_elements['price'] = {'text': args.price}
    if args.tagline:
        text_elements['tagline'] = {'text': args.tagline}
    
    # Initialize generator
    generator = ECImageGenerator(
        model_type=args.model,
        use_openai=not args.no_openai
    )
    
    # Generate image
    try:
        image = generator.generate_product_image(
            prompt=args.prompt,
            platform=args.platform,
            text_elements=text_elements if text_elements else None,
            pattern_name=args.pattern,
            output_path=args.output,
            run_quality_check=not args.no_quality_check,
            auto_fix=args.auto_fix
        )
        
        if not args.output:
            # Show image if no output path specified
            logger.info("Displaying image...")
            image.show()
        
        logger.info("\n[SUCCESS] Image generation completed!")
        
    except Exception as e:
        logger.error(f"\n[ERROR] Generation failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

