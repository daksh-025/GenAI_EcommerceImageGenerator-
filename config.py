"""
Configuration management for EC Product Image Generator
"""
import os
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple
import yaml

logger = logging.getLogger(__name__)

@dataclass
class PlatformConfig:
    """Configuration for each EC platform"""
    name: str
    width: int
    height: int
    background_color: Tuple[int, int, int]
    margin_ratio: float
    text_position: Dict[str, Tuple[int, int]]
    min_resolution: Tuple[int, int]
    aspect_ratio: float

class Config:
    """Main configuration class"""
    
    # Default output size
    DEFAULT_SIZE = (1000, 1000)
    
    # Platform configurations
    PLATFORMS = {
        'rakuten': PlatformConfig(
            name='Rakuten',
            width=1000,
            height=1000,
            background_color=(255, 255, 255),
            margin_ratio=0.1,
            text_position={
                'title': (500, 150),
                'price': (500, 850),
                'tagline': (500, 200)
            },
            min_resolution=(800, 800),
            aspect_ratio=1.0
        ),
        'amazon': PlatformConfig(
            name='Amazon',
            width=1000,
            height=1000,
            background_color=(255, 255, 255),
            margin_ratio=0.15,
            text_position={
                'title': (500, 120),
                'price': (500, 880),
                'tagline': (500, 180)
            },
            min_resolution=(1000, 1000),
            aspect_ratio=1.0
        ),
        'yahoo': PlatformConfig(
            name='Yahoo Shopping',
            width=1000,
            height=1000,
            background_color=(255, 255, 255),
            margin_ratio=0.12,
            text_position={
                'title': (500, 140),
                'price': (500, 860),
                'tagline': (500, 190)
            },
            min_resolution=(800, 800),
            aspect_ratio=1.0
        ),
        'mercari': PlatformConfig(
            name='Mercari',
            width=1000,
            height=1000,
            background_color=(255, 255, 255),
            margin_ratio=0.1,
            text_position={
                'title': (500, 150),
                'price': (500, 870),
                'tagline': (500, 200)
            },
            min_resolution=(640, 640),
            aspect_ratio=1.0
        )
    }
    
    # Image generation settings
    IMAGE_GENERATION = {
        'model': 'stable_diffusion',  # Use stable_diffusion since LOVART has no API
        'default_size': DEFAULT_SIZE,
        'num_inference_steps': 50,
        'guidance_scale': 7.5,
    }
    
    # OpenAI settings
    OPENAI = {
        'model': 'gpt-4o-mini',  # Cost-effective model
        'temperature': 0.7,
        'max_tokens': 300,
    }
    
    # Text rendering settings
    TEXT_RENDERING = {
        'default_font': 'fonts/NotoSansCJK-Regular.ttc',
        'fallback_fonts': [
            'fonts/NotoSansJP-Regular.otf',
            'fonts/Meiryo.ttf'
        ],
        'default_font_size': 48,
        'title_font_size': 60,
        'price_font_size': 72,
        'tagline_font_size': 36,
        'text_color': (0, 0, 0),
        'outline_color': (255, 255, 255),
        'outline_width': 2
    }
    
    # Quality thresholds
    QUALITY_THRESHOLDS = {
        'min_resolution': (800, 800),
        'max_color_saturation': 0.95,
        'min_text_contrast': 0.7,
        'check_character_collapse': True
    }
    
    # Template patterns (for variation)
    TEMPLATE_PATTERNS = [
        {
            'name': 'centered',
            'product_position': (500, 500),
            'text_alignment': 'center'
        },
        {
            'name': 'left_aligned',
            'product_position': (300, 500),
            'text_alignment': 'left'
        },
        {
            'name': 'right_aligned',
            'product_position': (700, 500),
            'text_alignment': 'right'
        },
        {
            'name': 'top_heavy',
            'product_position': (500, 400),
            'text_alignment': 'center'
        },
        {
            'name': 'bottom_heavy',
            'product_position': (500, 600),
            'text_alignment': 'center'
        }
    ]
    
    @classmethod
    def get_platform_config(cls, platform: str) -> PlatformConfig:
        """Get configuration for a specific platform"""
        platform_lower = platform.lower()
        if platform_lower not in cls.PLATFORMS:
            logger.error(f"Unknown platform: {platform}. Available: {list(cls.PLATFORMS.keys())}")
            raise ValueError(f"Unknown platform: {platform}. Available: {list(cls.PLATFORMS.keys())}")
        logger.debug(f"Retrieved config for platform: {platform_lower}")
        return cls.PLATFORMS[platform_lower]
    
    @classmethod
    def load_from_yaml(cls, yaml_path: str = 'config.yaml'):
        """Load configuration from YAML file if it exists"""
        if os.path.exists(yaml_path):
            logger.info(f"Loading configuration from {yaml_path}")
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                return config_data
        else:
            logger.debug(f"Config file {yaml_path} not found, using defaults")
        return None

