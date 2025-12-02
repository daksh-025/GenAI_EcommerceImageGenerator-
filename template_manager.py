"""
Template Management Module
Handles EC platform-specific templates and automatic optimization
"""
import random
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw
from config import Config, PlatformConfig

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages templates for different EC platforms"""
    
    def __init__(self):
        """Initialize template manager"""
        self.platforms = Config.PLATFORMS
        self.patterns = Config.TEMPLATE_PATTERNS
        logger.info("TemplateManager initialized")
        logger.debug(f"Available platforms: {list(self.platforms.keys())}")
        logger.debug(f"Available patterns: {[p['name'] for p in self.patterns]}")
    
    def get_template(
        self,
        platform: str,
        pattern_name: Optional[str] = None
    ) -> Dict:
        """
        Get template configuration for a platform
        
        Args:
            platform: Platform name ('rakuten', 'amazon', 'yahoo', 'mercari')
            pattern_name: Optional pattern name for variation
            
        Returns:
            Template configuration dictionary
        """
        logger.info(f"Getting template for platform: {platform}, pattern: {pattern_name or 'random'}")
        
        platform_config = Config.get_platform_config(platform)
        
        # Select pattern (random if not specified)
        if pattern_name:
            pattern = next((p for p in self.patterns if p['name'] == pattern_name), self.patterns[0])
            logger.debug(f"Using specified pattern: {pattern_name}")
        else:
            pattern = random.choice(self.patterns)
            logger.debug(f"Using random pattern: {pattern['name']}")
        
        template = {
            'platform': platform,
            'platform_config': platform_config,
            'pattern': pattern,
            'size': (platform_config.width, platform_config.height),
            'background_color': platform_config.background_color,
            'margin_ratio': platform_config.margin_ratio,
            'text_positions': self._calculate_text_positions(platform_config, pattern),
            'product_area': self._calculate_product_area(platform_config, pattern)
        }
        
        logger.info(f"Template created: {platform} with pattern '{pattern['name']}'")
        return template
    
    def _calculate_text_positions(
        self,
        platform_config: PlatformConfig,
        pattern: Dict
    ) -> Dict[str, Tuple[int, int]]:
        """
        Calculate text positions based on platform and pattern
        
        Args:
            platform_config: Platform configuration
            pattern: Layout pattern
            
        Returns:
            Dictionary of text element positions
        """
        logger.debug("Calculating text positions")
        base_positions = platform_config.text_position.copy()
        alignment = pattern.get('text_alignment', 'center')
        
        # Adjust positions based on pattern
        width = platform_config.width
        margin = int(width * platform_config.margin_ratio)
        
        adjusted_positions = {}
        for key, (x, y) in base_positions.items():
            if alignment == 'left':
                x = margin + 50
            elif alignment == 'right':
                x = width - margin - 50
            # 'center' keeps original x
            
            adjusted_positions[key] = (x, y)
        
        logger.debug(f"Text positions calculated: {adjusted_positions}")
        return adjusted_positions
    
    def _calculate_product_area(
        self,
        platform_config: PlatformConfig,
        pattern: Dict
    ) -> Dict[str, int]:
        """
        Calculate product placement area
        
        Args:
            platform_config: Platform configuration
            pattern: Layout pattern
            
        Returns:
            Dictionary with product area bounds
        """
        logger.debug("Calculating product area")
        width = platform_config.width
        height = platform_config.height
        margin = int(width * platform_config.margin_ratio)
        
        product_pos = pattern.get('product_position', (width // 2, height // 2))
        
        # Calculate safe area for product (avoiding text areas)
        text_y_positions = [pos[1] for pos in platform_config.text_position.values()]
        min_text_y = min(text_y_positions) if text_y_positions else height // 2
        max_text_y = max(text_y_positions) if text_y_positions else height // 2
        
        # Product area (centered around product position, avoiding text)
        product_size = min(width, height) - (2 * margin)
        
        area = {
            'center_x': product_pos[0],
            'center_y': product_pos[1],
            'width': product_size,
            'height': product_size,
            'margin': margin
        }
        
        logger.debug(f"Product area calculated: {area}")
        return area
    
    def apply_template_to_image(
        self,
        base_image: Image.Image,
        template: Dict,
        resize_product: bool = True
    ) -> Image.Image:
        """
        Apply template to base image (resize, add background, etc.)
        
        Args:
            base_image: Base product image
            template: Template configuration
            resize_product: Whether to resize product to fit template
            
        Returns:
            Image with template applied
        """
        logger.info("Applying template to image")
        platform_config = template['platform_config']
        size = template['size']
        bg_color = template['background_color']
        product_area = template['product_area']
        
        logger.debug(f"Template size: {size}, background: {bg_color}")
        
        # Create new image with platform background
        result = Image.new('RGB', size, color=bg_color)
        
        # Resize and place product image
        if resize_product:
            # Calculate size to fit in product area
            max_size = min(product_area['width'], product_area['height'])
            
            # Maintain aspect ratio
            base_aspect = base_image.width / base_image.height
            if base_aspect > 1:
                new_width = max_size
                new_height = int(max_size / base_aspect)
            else:
                new_width = int(max_size * base_aspect)
                new_height = max_size
            
            logger.debug(f"Resizing product from {base_image.size} to ({new_width}, {new_height})")
            
            # Resize product image
            product_resized = base_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            product_resized = base_image
        
        # Calculate paste position (center in product area)
        paste_x = product_area['center_x'] - product_resized.width // 2
        paste_y = product_area['center_y'] - product_resized.height // 2
        
        # Ensure paste position is within bounds
        paste_x = max(0, min(paste_x, size[0] - product_resized.width))
        paste_y = max(0, min(paste_y, size[1] - product_resized.height))
        
        logger.debug(f"Pasting product at position: ({paste_x}, {paste_y})")
        
        # Paste product image
        if product_resized.mode == 'RGBA':
            result.paste(product_resized, (paste_x, paste_y), product_resized)
        else:
            result.paste(product_resized, (paste_x, paste_y))
        
        logger.info("Template applied successfully")
        return result
    
    def get_all_patterns(self) -> List[str]:
        """Get list of all available pattern names"""
        return [p['name'] for p in self.patterns]
    
    def validate_template(self, template: Dict) -> bool:
        """
        Validate template configuration
        
        Args:
            template: Template to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['platform', 'platform_config', 'size', 'text_positions', 'product_area']
        is_valid = all(key in template for key in required_keys)
        
        if not is_valid:
            logger.warning(f"Template validation failed. Missing keys: {[k for k in required_keys if k not in template]}")
        
        return is_valid

