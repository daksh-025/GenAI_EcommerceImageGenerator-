"""
Japanese Text Layer Composition Module
Handles accurate Japanese text rendering with font embedding
"""
import os
import logging
from typing import Optional, Tuple, List, Dict
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from config import Config

logger = logging.getLogger(__name__)

class TextCompositor:
    """Handles Japanese text composition and layer merging"""
    
    def __init__(self, font_path: Optional[str] = None):
        """
        Initialize text compositor
        
        Args:
            font_path: Path to Japanese font file
        """
        self.font_path = font_path or Config.TEXT_RENDERING['default_font']
        self.fallback_fonts = Config.TEXT_RENDERING['fallback_fonts']
        self.fonts = {}
        
        logger.info("Initializing TextCompositor")
        self._load_fonts()
    
    def _load_fonts(self):
        """Load Japanese fonts with fallback options"""
        logger.debug("Loading Japanese fonts...")
        
        # Try to load default font
        if os.path.exists(self.font_path):
            try:
                logger.info(f"Loading font: {self.font_path}")
                self.fonts['default'] = ImageFont.truetype(self.font_path, 48)
                self.fonts['title'] = ImageFont.truetype(self.font_path, 60)
                self.fonts['price'] = ImageFont.truetype(self.font_path, 72)
                self.fonts['tagline'] = ImageFont.truetype(self.font_path, 36)
                logger.info("Default font loaded successfully")
                return
            except Exception as e:
                logger.warning(f"Failed to load default font: {e}")
        
        # Try fallback fonts
        for fallback_path in self.fallback_fonts:
            if os.path.exists(fallback_path):
                try:
                    logger.info(f"Loading fallback font: {fallback_path}")
                    self.fonts['default'] = ImageFont.truetype(fallback_path, 48)
                    self.fonts['title'] = ImageFont.truetype(fallback_path, 60)
                    self.fonts['price'] = ImageFont.truetype(fallback_path, 72)
                    self.fonts['tagline'] = ImageFont.truetype(fallback_path, 36)
                    logger.info("Fallback font loaded successfully")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load fallback font {fallback_path}: {e}")
                    continue
        
        # Use default system font as last resort
        logger.warning("No Japanese fonts found. Using default system font (may not support Japanese)")
        try:
            self.fonts['default'] = ImageFont.load_default()
            self.fonts['title'] = ImageFont.load_default()
            self.fonts['price'] = ImageFont.load_default()
            self.fonts['tagline'] = ImageFont.load_default()
        except Exception as e:
            logger.error(f"Failed to load default system font: {e}")
    
    def get_font(self, text_type: str = 'default') -> ImageFont.FreeTypeFont:
        """Get font for specific text type"""
        font = self.fonts.get(text_type, self.fonts.get('default', ImageFont.load_default()))
        logger.debug(f"Retrieved font for type: {text_type}")
        return font
    
    def render_text_with_outline(
        self,
        image: Image.Image,
        text: str,
        position: Tuple[int, int],
        font_size: int,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        outline_color: Tuple[int, int, int] = (255, 255, 255),
        outline_width: int = 2,
        alignment: str = 'center'
    ) -> Image.Image:
        """
        Render text with outline for better visibility
        
        Args:
            image: Base image to draw on
            text: Text to render
            position: (x, y) position for text
            font_size: Size of font
            text_color: RGB color of text
            outline_color: RGB color of outline
            outline_width: Width of outline
            alignment: Text alignment ('left', 'center', 'right')
            
        Returns:
            Image with text rendered
        """
        logger.debug(f"Rendering text: '{text[:30]}...' at position {position}")
        
        # Create a copy to avoid modifying original
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Get appropriate font
        if font_size == 60:
            font = self.get_font('title')
        elif font_size == 72:
            font = self.get_font('price')
        elif font_size == 36:
            font = self.get_font('tagline')
        else:
            font = self.get_font('default')
        
        # Calculate text bounding box for alignment
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Adjust position based on alignment
        x, y = position
        if alignment == 'center':
            x = x - text_width // 2
        elif alignment == 'right':
            x = x - text_width
        # 'left' alignment uses x as-is
        
        logger.debug(f"Text dimensions: {text_width}x{text_height}, adjusted position: ({x}, {y})")
        
        # Draw outline (multiple passes for thicker outline)
        for adj in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj != 0 or adj_y != 0:
                    draw.text(
                        (x + adj, y + adj_y),
                        text,
                        font=font,
                        fill=outline_color
                    )
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
        
        logger.debug("Text rendered successfully")
        return img
    
    def composite_text_layers(
        self,
        base_image: Image.Image,
        text_elements: Dict[str, Dict],
        platform_config
    ) -> Image.Image:
        """
        Composite multiple text layers onto base image
        
        Args:
            base_image: Base product image
            text_elements: Dictionary of text elements with their properties
            platform_config: PlatformConfig object with platform-specific settings
            
        Returns:
            Image with all text layers composited
        """
        logger.info(f"Compositing {len(text_elements)} text layers")
        result_image = base_image.copy()
        
        # Get text rendering config
        text_config = Config.TEXT_RENDERING
        
        for element_name, element_data in text_elements.items():
            text = element_data.get('text', '')
            if not text:
                logger.debug(f"Skipping empty text element: {element_name}")
                continue
            
            logger.debug(f"Processing text element: {element_name} = '{text}'")
            
            # Get position (use provided or from platform config)
            position = element_data.get('position')
            if not position and element_name in platform_config.text_position:
                position = platform_config.text_position[element_name]
            elif not position:
                # Default position
                position = (500, 500)
                logger.warning(f"No position found for {element_name}, using default: {position}")
            
            # Get font size
            font_size = element_data.get('size')
            if not font_size:
                if element_name == 'title':
                    font_size = text_config['title_font_size']
                elif element_name == 'price':
                    font_size = text_config['price_font_size']
                elif element_name == 'tagline':
                    font_size = text_config['tagline_font_size']
                else:
                    font_size = text_config['default_font_size']
            
            # Get alignment
            alignment = element_data.get('alignment', 'center')
            
            # Render text with outline
            result_image = self.render_text_with_outline(
                result_image,
                text,
                position,
                font_size,
                text_color=text_config['text_color'],
                outline_color=text_config['outline_color'],
                outline_width=text_config['outline_width'],
                alignment=alignment
            )
        
        logger.info("Text composition completed")
        return result_image
    
    def measure_text_dimensions(
        self,
        text: str,
        font_size: int,
        font_type: str = 'default'
    ) -> Tuple[int, int]:
        """
        Measure text dimensions without rendering
        
        Args:
            text: Text to measure
            font_size: Font size
            font_type: Type of font ('default', 'title', 'price', 'tagline')
            
        Returns:
            (width, height) tuple
        """
        font = self.get_font(font_type)
        
        # Create temporary image for measurement
        temp_img = Image.new('RGB', (1000, 1000), color=(255, 255, 255))
        draw = ImageDraw.Draw(temp_img)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        return width, height

