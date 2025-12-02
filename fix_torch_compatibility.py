"""
Script to fix PyTorch and diffusers compatibility issues
Run this script to check and fix version compatibility
"""
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_torch_version():
    """Check current PyTorch version"""
    try:
        import torch
        version = torch.__version__
        logger.info(f"Current PyTorch version: {version}")
        return version
    except ImportError:
        logger.error("PyTorch not installed")
        return None

def fix_compatibility():
    """Fix PyTorch and diffusers compatibility"""
    logger.info("=" * 60)
    logger.info("Fixing PyTorch and diffusers compatibility")
    logger.info("=" * 60)
    
    # Uninstall conflicting packages
    logger.info("Step 1: Uninstalling conflicting packages...")
    packages_to_uninstall = ['torch', 'torchvision', 'torchaudio', 'diffusers']
    for package in packages_to_uninstall:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', package], 
                         check=False, capture_output=True)
            logger.info(f"  Uninstalled {package}")
        except:
            pass
    
    # Install compatible versions
    logger.info("\nStep 2: Installing compatible versions...")
    logger.info("This may take several minutes...")
    
    # Install PyTorch 2.1.0 (compatible with diffusers)
    logger.info("Installing PyTorch 2.1.0...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'torch==2.1.0', 'torchvision==0.16.0', 'torchaudio==2.1.0',
            '--index-url', 'https://download.pytorch.org/whl/cu118'
        ], check=True)
        logger.info("  ✓ PyTorch installed (CUDA version)")
    except:
        # Fallback to CPU version
        logger.info("Installing PyTorch CPU version...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'torch==2.1.0', 'torchvision==0.16.0', 'torchaudio==2.1.0'
        ], check=True)
        logger.info("  ✓ PyTorch installed (CPU version)")
    
    # Install diffusers
    logger.info("Installing diffusers...")
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', 
        'diffusers>=0.21.0,<0.30.0'
    ], check=True)
    logger.info("  ✓ diffusers installed")
    
    # Install transformers
    logger.info("Installing transformers...")
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', 
        'transformers>=4.30.0,<5.0.0'
    ], check=True)
    logger.info("  ✓ transformers installed")
    
    # Install accelerate
    logger.info("Installing accelerate...")
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', 
        'accelerate>=0.20.0'
    ], check=True)
    logger.info("  ✓ accelerate installed")
    
    logger.info("\n" + "=" * 60)
    logger.info("Installation complete!")
    logger.info("=" * 60)
    
    # Verify installation
    logger.info("\nVerifying installation...")
    try:
        import torch
        import diffusers
        logger.info(f"✓ PyTorch {torch.__version__} installed")
        logger.info(f"✓ diffusers {diffusers.__version__} installed")
        logger.info("\n✓ All packages installed successfully!")
        return True
    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        return False

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("PyTorch Compatibility Fix Script")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Uninstall existing PyTorch/diffusers")
    print("2. Install compatible versions")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    
    success = fix_compatibility()
    
    if success:
        print("\n✓ Setup complete! You can now run the image generator.")
    else:
        print("\n✗ Setup failed. Please check the error messages above.")
        sys.exit(1)

