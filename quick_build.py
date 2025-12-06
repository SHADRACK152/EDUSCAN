#!/usr/bin/env python3
"""
Simple builder script for EDUSCAN
Run: python quick_build.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show progress"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def create_icon_if_missing():
    """Create application icon if it doesn't exist"""
    icon_path = Path("assets/icon.ico")
    if not icon_path.exists():
        print("\n🎨 Creating application icon...")
        try:
            from PIL import Image, ImageDraw
            
            # Create simple professional icon
            size = (256, 256)
            img = Image.new('RGB', size, (9, 105, 218))  # GitHub blue
            draw = ImageDraw.Draw(img)
            
            # Draw circle border
            draw.ellipse([(30, 30), (226, 226)], outline=(255, 255, 255), width=4)
            
            # Create assets folder if needed
            Path("assets").mkdir(exist_ok=True)
            img.save(str(icon_path), 'ICO', sizes=[256])
            print("✅ Icon created successfully")
            return True
        except ImportError:
            print("⚠️  PIL not found - icon won't be custom")
            print("   Install with: pip install Pillow")
            return False
    else:
        print(f"✅ Icon found: {icon_path}")
        return True

def main():
    os.chdir(Path(__file__).parent)
    
    print("\n" + "="*60)
    print("🚀 EDUSCAN Windows Installer Builder")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create icon if missing
    create_icon_if_missing()
    
    # Install PyInstaller if missing
    print("\n📦 Checking dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "PyInstaller"],
        capture_output=True
    )
    if result.returncode != 0:
        print("❌ Failed to install PyInstaller")
        return False
    print("✅ PyInstaller ready")
    
    # Clean previous builds
    print("\n🗑️  Cleaning previous builds...")
    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed: {folder}/")
    
    # Build with PyInstaller
    if not run_command(
        f"{sys.executable} -m PyInstaller main.py --onedir --windowed --name EDUSCAN --icon assets/icon.ico --add-data \"gui;gui\" --add-data \"face_engine;face_engine\" --add-data \"voice_engine;voice_engine\" --add-data \"database;database\" --add-data \"assets;assets\" --add-data \"themes;themes\" --add-data \"config.json;.\"",
        "Building executable with PyInstaller"
    ):
        print("❌ Build failed")
        return False
    
    # Create portable ZIP
    print("\n📦 Creating portable ZIP...")
    if os.path.exists("dist/EDUSCAN"):
        shutil.make_archive("dist/EDUSCAN-Portable", "zip", "dist", "EDUSCAN")
        print("✅ Created: dist/EDUSCAN-Portable.zip")
    
    # Summary
    print("\n" + "="*60)
    print("✅ BUILD COMPLETE!")
    print("="*60)
    print("\n📁 Output files:")
    print("  • Portable ZIP: dist/EDUSCAN-Portable.zip")
    print("  • Executable:   dist/EDUSCAN/EDUSCAN.exe")
    print("\n▶ Next steps:")
    print("  1. Test: Run dist/EDUSCAN/EDUSCAN.exe")
    print("  2. Share: Use EDUSCAN-Portable.zip or full dist/EDUSCAN/ folder")
    print("  3. Install: Extract and run, or copy executable")
    print("\n💡 For NSIS installer support:")
    print("  1. Install NSIS: https://nsis.sourceforge.io/")
    print("  2. Use: python build_installer.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
