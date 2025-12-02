"""
Quality Verification Module
Automatically checks image quality for EC standards
"""
import cv2
import numpy as np
import logging
from PIL import Image
from typing import Dict, List, Tuple, Optional
from config import Config

logger = logging.getLogger(__name__)

class QualityChecker:
    """Checks image quality against EC standards"""
    
    def __init__(self):
        """Initialize quality checker"""
        self.thresholds = Config.QUALITY_THRESHOLDS
        logger.info("QualityChecker initialized")
        logger.debug(f"Quality thresholds: {self.thresholds}")
    
    def check_all(
        self,
        image: Image.Image,
        platform: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Run all quality checks
        
        Args:
            image: Image to check
            platform: Optional platform name for platform-specific checks
            
        Returns:
            Dictionary with all check results
        """
        logger.info("Running comprehensive quality checks")
        results = {
            'resolution': self.check_resolution(image, platform),
            'color_saturation': self.check_color_saturation(image),
            'text_contrast': self.check_text_contrast(image),
            'character_collapse': self.check_character_collapse(image) if self.thresholds['check_character_collapse'] else {'passed': True, 'message': 'Skipped'},
            'overall': {'passed': True, 'score': 0.0}
        }
        
        # Calculate overall score
        passed_checks = sum(1 for r in results.values() if isinstance(r, dict) and r.get('passed', False))
        total_checks = len([r for r in results.values() if isinstance(r, dict) and 'passed' in r])
        results['overall']['score'] = passed_checks / total_checks if total_checks > 0 else 0.0
        results['overall']['passed'] = results['overall']['score'] >= 0.8
        
        logger.info(f"Quality check completed. Score: {results['overall']['score']:.2%}, Passed: {results['overall']['passed']}")
        return results
    
    def check_resolution(
        self,
        image: Image.Image,
        platform: Optional[str] = None
    ) -> Dict:
        """
        Check if image meets minimum resolution requirements
        
        Args:
            image: Image to check
            platform: Optional platform name
            
        Returns:
            Dictionary with check results
        """
        width, height = image.size
        min_res = self.thresholds['min_resolution']
        
        if platform:
            try:
                platform_config = Config.get_platform_config(platform)
                min_res = platform_config.min_resolution
                logger.debug(f"Using platform-specific resolution requirement: {min_res}")
            except:
                pass
        
        passed = width >= min_res[0] and height >= min_res[1]
        
        result = {
            'passed': passed,
            'actual': (width, height),
            'required': min_res,
            'message': f"Resolution: {width}x{height} (required: {min_res[0]}x{min_res[1]})" if passed 
                      else f"Resolution too low: {width}x{height} (required: {min_res[0]}x{min_res[1]})"
        }
        
        logger.debug(f"Resolution check: {result['message']}")
        return result
    
    def check_color_saturation(
        self,
        image: Image.Image
    ) -> Dict:
        """
        Check color saturation levels
        
        Args:
            image: Image to check
            
        Returns:
            Dictionary with check results
        """
        logger.debug("Checking color saturation")
        # Convert to numpy array
        img_array = np.array(image.convert('RGB'))
        
        # Convert to HSV
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1].astype(np.float32) / 255.0
        
        # Calculate max saturation
        max_saturation = np.max(saturation)
        threshold = self.thresholds['max_color_saturation']
        
        passed = max_saturation <= threshold
        
        result = {
            'passed': passed,
            'max_saturation': float(max_saturation),
            'threshold': threshold,
            'message': f"Max saturation: {max_saturation:.2f} (threshold: {threshold})" if passed
                      else f"Saturation too high: {max_saturation:.2f} (threshold: {threshold})"
        }
        
        logger.debug(f"Color saturation check: {result['message']}")
        return result
    
    def check_text_contrast(
        self,
        image: Image.Image,
        text_regions: Optional[List[Tuple[int, int, int, int]]] = None
    ) -> Dict:
        """
        Check text contrast in image
        
        Args:
            image: Image to check
            text_regions: Optional list of (x, y, width, height) text regions
            
        Returns:
            Dictionary with check results
        """
        logger.debug("Checking text contrast")
        img_array = np.array(image.convert('RGB'))
        
        if text_regions:
            # Check contrast in specific text regions
            contrasts = []
            for x, y, w, h in text_regions:
                region = img_array[y:y+h, x:x+w]
                if region.size > 0:
                    # Calculate contrast (standard deviation of grayscale)
                    gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
                    contrast = np.std(gray) / 255.0
                    contrasts.append(contrast)
            
            min_contrast = min(contrasts) if contrasts else 0.0
        else:
            # Check overall image contrast
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            min_contrast = np.std(gray) / 255.0
        
        threshold = self.thresholds['min_text_contrast']
        passed = min_contrast >= threshold
        
        result = {
            'passed': passed,
            'min_contrast': float(min_contrast),
            'threshold': threshold,
            'message': f"Text contrast: {min_contrast:.2f} (threshold: {threshold})" if passed
                      else f"Text contrast too low: {min_contrast:.2f} (threshold: {threshold})"
        }
        
        logger.debug(f"Text contrast check: {result['message']}")
        return result
    
    def check_character_collapse(
        self,
        image: Image.Image
    ) -> Dict:
        """
        Check for character collapse (blurred/unreadable text)
        
        Args:
            image: Image to check
            
        Returns:
            Dictionary with check results
        """
        logger.debug("Checking for character collapse (blur detection)")
        img_array = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Use Laplacian to detect blur
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Low variance indicates blur (character collapse)
        # Threshold: images with variance < 100 are likely blurred
        blur_threshold = 100.0
        passed = laplacian_var >= blur_threshold
        
        result = {
            'passed': passed,
            'sharpness': float(laplacian_var),
            'threshold': blur_threshold,
            'message': f"Image sharpness: {laplacian_var:.2f} (threshold: {blur_threshold})" if passed
                      else f"Possible character collapse detected (sharpness: {laplacian_var:.2f})"
        }
        
        logger.debug(f"Character collapse check: {result['message']}")
        return result
    
    def generate_quality_report(
        self,
        image: Image.Image,
        platform: Optional[str] = None
    ) -> str:
        """
        Generate human-readable quality report
        
        Args:
            image: Image to check
            platform: Optional platform name
            
        Returns:
            Formatted quality report string
        """
        logger.info("Generating quality report")
        results = self.check_all(image, platform)
        
        report_lines = ["=== Image Quality Report ===\n"]
        
        for check_name, check_result in results.items():
            if check_name == 'overall':
                continue
            
            status = "✓ PASS" if check_result.get('passed', False) else "✗ FAIL"
            report_lines.append(f"{check_name.upper()}: {status}")
            report_lines.append(f"  {check_result.get('message', 'No message')}")
            report_lines.append("")
        
        # Overall score
        overall = results['overall']
        score_pct = overall['score'] * 100
        report_lines.append(f"Overall Score: {score_pct:.1f}%")
        report_lines.append(f"Status: {'PASS' if overall['passed'] else 'FAIL'}")
        
        report = "\n".join(report_lines)
        logger.debug("Quality report generated")
        return report
    
    def fix_common_issues(
        self,
        image: Image.Image,
        issues: Dict
    ) -> Image.Image:
        """
        Attempt to fix common quality issues
        
        Args:
            image: Image to fix
            issues: Dictionary of detected issues
            
        Returns:
            Fixed image
        """
        logger.info("Attempting to fix quality issues")
        fixed_image = image.copy()
        
        # Fix resolution if too low
        if not issues.get('resolution', {}).get('passed', True):
            required = issues['resolution'].get('required', (800, 800))
            logger.info(f"Fixing resolution: upscaling to {required}")
            fixed_image = fixed_image.resize(required, Image.Resampling.LANCZOS)
        
        # Fix saturation if too high
        if not issues.get('color_saturation', {}).get('passed', True):
            logger.info("Fixing color saturation: reducing by 20%")
            # Reduce saturation
            img_array = np.array(fixed_image.convert('RGB'))
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            hsv[:, :, 1] = (hsv[:, :, 1] * 0.8).astype(np.uint8)  # Reduce saturation by 20%
            fixed_array = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            fixed_image = Image.fromarray(fixed_array)
        
        logger.info("Quality fixes applied")
        return fixed_image

