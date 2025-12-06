#!/usr/bin/env python3
"""
EDUSCAN Production Build Script
Complete packaging for Windows distribution
Ensures all dependencies and files are ready
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

# Fix Unicode output for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class EDUSCANBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.venv_dir = self.project_dir / ".venv"
        self.dist_dir = self.project_dir / "dist"
        self.python_exe = self.venv_dir / "Scripts" / "python.exe"
        
    def log_step(self, step_num, title, description=""):
        """Log build step"""
        print(f"\n{'='*70}")
        print(f"STEP {step_num}: {title}")
        print(f"{'='*70}")
        if description:
            print(f"  {description}")
    
    def log_success(self, message):
        """Log success"""
        print(f"✅ {message}")
    
    def log_error(self, message):
        """Log error"""
        print(f"❌ {message}")
    
    def log_warning(self, message):
        """Log warning"""
        print(f"⚠️  {message}")
    
    def log_info(self, message):
        """Log info"""
        print(f"ℹ️  {message}")
    
    def run_command(self, cmd, description=""):
        """Run a shell command"""
        if description:
            print(f"  Running: {description}...")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  Error output: {result.stderr}")
                return False
            if result.stdout:
                print(f"  {result.stdout.strip()}")
            return True
        except Exception as e:
            self.log_error(f"Command failed: {e}")
            return False
    
    def step1_verify_python(self):
        """Step 1: Verify Python installation"""
        self.log_step(1, "Verify Python Installation")
        
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            self.log_error("Python not installed or not in PATH")
            return False
        
        version = result.stdout.strip()
        self.log_success(f"Python found: {version}")
        
        # Check version
        if sys.version_info < (3, 8):
            self.log_error("Python 3.8+ required")
            return False
        
        self.log_success("Python version OK")
        return True
    
    def step2_setup_venv(self):
        """Step 2: Setup virtual environment"""
        self.log_step(2, "Setup Virtual Environment")
        
        if self.venv_dir.exists():
            self.log_success("Virtual environment already exists")
        else:
            self.log_info("Creating virtual environment...")
            if not self.run_command(f"{sys.executable} -m venv .venv", "Create venv"):
                self.log_error("Failed to create virtual environment")
                return False
            self.log_success("Virtual environment created")
        
        # Verify python.exe in venv
        if not self.python_exe.exists():
            self.log_error(f"Python executable not found at {self.python_exe}")
            return False
        
        self.log_success("Virtual environment is ready")
        return True
    
    def step3_install_dependencies(self):
        """Step 3: Install all dependencies"""
        self.log_step(3, "Install Dependencies")
        
        # Upgrade pip first
        self.log_info("Upgrading pip...")
        self.run_command(f"{self.python_exe} -m pip install --upgrade pip", "Upgrade pip")
        
        # Read requirements.txt
        req_file = self.project_dir / "requirements.txt"
        if not req_file.exists():
            self.log_error("requirements.txt not found")
            return False
        
        # Install build tools
        build_tools = ["PyInstaller", "Pillow"]
        for tool in build_tools:
            self.log_info(f"Installing {tool}...")
            if not self.run_command(f"{self.python_exe} -m pip install -q {tool}", f"Install {tool}"):
                self.log_warning(f"Failed to install {tool}, continuing...")
        
        # Install all requirements
        self.log_info("Installing application dependencies...")
        if not self.run_command(f"{self.python_exe} -m pip install -q -r requirements.txt", 
                               "Install requirements"):
            self.log_error("Failed to install requirements")
            return False
        
        self.log_success("All dependencies installed")
        return True
    
    def step4_verify_assets(self):
        """Step 4: Verify all asset files exist"""
        self.log_step(4, "Verify Asset Files")
        
        required_files = [
            "main.py",
            "config.json",
            "setup.py",
            "gui/dashboard.py",
            "gui/login.py",
            "database/student_db.py",
            "face_engine/recognizer.py",
            "voice_engine/recognizer.py",
            "themes/light.qss",
            "themes/dark.qss",
        ]
        
        missing = []
        for file_path in required_files:
            full_path = self.project_dir / file_path
            if not full_path.exists():
                missing.append(file_path)
                self.log_error(f"Missing: {file_path}")
            else:
                self.log_info(f"Found: {file_path}")
        
        if missing:
            self.log_error(f"Missing {len(missing)} required files")
            return False
        
        self.log_success("All required files present")
        return True
    
    def step5_create_icon(self):
        """Step 5: Create application icon"""
        self.log_step(5, "Create Application Icon")
        
        icon_file = self.project_dir / "assets" / "icon.ico"
        
        if icon_file.exists():
            self.log_success(f"Icon already exists: {icon_file}")
            return True
        
        # Create assets directory
        (self.project_dir / "assets").mkdir(exist_ok=True)
        
        # Create icon
        self.log_info("Generating default icon...")
        if not self.run_command(f"{self.python_exe} create_icon.py", "Create icon"):
            self.log_warning("Icon creation failed, continuing without custom icon")
            return True
        
        if icon_file.exists():
            self.log_success(f"Icon created: {icon_file}")
            return True
        else:
            self.log_warning("Icon file not created, continuing...")
            return True
    
    def step6_verify_database(self):
        """Step 6: Verify and initialize database"""
        self.log_step(6, "Verify Database")
        
        self.log_info("Initializing database...")
        if not self.run_command(f"{self.python_exe} setup.py", "Initialize database"):
            self.log_warning("Database initialization may have issues")
        
        db_file = self.project_dir / "database" / "students.db"
        if db_file.exists():
            self.log_success(f"Database ready: {db_file}")
        else:
            self.log_warning("Database file not created yet (will be created on first run)")
        
        return True
    
    def step7_test_import(self):
        """Step 7: Test application imports"""
        self.log_step(7, "Test Application Imports")
        
        test_script = """
import sys
sys.path.insert(0, '.')

try:
    import main
    print("✓ main.py imports OK")
except Exception as e:
    print(f"✗ main.py import failed: {e}")
    sys.exit(1)

try:
    from gui import dashboard
    print("✓ gui.dashboard imports OK")
except Exception as e:
    print(f"✗ gui.dashboard import failed: {e}")
    sys.exit(1)

try:
    from database import student_db
    print("✓ database.student_db imports OK")
except Exception as e:
    print(f"✗ database.student_db import failed: {e}")
    sys.exit(1)

try:
    import PyQt5
    print("✓ PyQt5 imports OK")
except Exception as e:
    print(f"✗ PyQt5 import failed: {e}")
    sys.exit(1)

print("✓ All imports successful")
"""
        
        test_file = self.project_dir / "test_imports.py"
        test_file.write_text(test_script)
        
        if self.run_command(f"{self.python_exe} test_imports.py", "Test imports"):
            self.log_success("All imports successful")
            test_file.unlink()
            return True
        else:
            self.log_error("Some imports failed")
            test_file.unlink()
            return False
    
    def step8_clean_build(self):
        """Step 8: Clean previous builds"""
        self.log_step(8, "Clean Previous Builds")
        
        dirs_to_clean = ["build", "dist", "__pycache__"]
        for dir_name in dirs_to_clean:
            dir_path = self.project_dir / dir_name
            if dir_path.exists():
                self.log_info(f"Removing {dir_name}/...")
                shutil.rmtree(dir_path)
                self.log_success(f"Removed {dir_name}/")
        
        return True
    
    def step9_build_executable(self):
        """Step 9: Build executable with PyInstaller"""
        self.log_step(9, "Build Executable with PyInstaller")
        
        icon_path = self.project_dir / "assets" / "icon.ico"
        icon_param = f'--icon "{icon_path}"' if icon_path.exists() else ""
        
        cmd = f"""{self.python_exe} -m PyInstaller main.py \\
            --onedir \\
            --windowed \\
            --name EDUSCAN \\
            {icon_param} \\
            --add-data "gui;gui" \\
            --add-data "face_engine;face_engine" \\
            --add-data "voice_engine;voice_engine" \\
            --add-data "database;database" \\
            --add-data "assets;assets" \\
            --add-data "themes;themes" \\
            --add-data "config.json;." \\
            --hidden-import=PyQt5.QtCore \\
            --hidden-import=PyQt5.QtGui \\
            --hidden-import=PyQt5.QtWidgets \\
            --hidden-import=cv2 \\
            --hidden-import=face_recognition \\
            --hidden-import=dlib \\
            --hidden-import=sqlite3 \\
            --hidden-import=pyttsx3 \\
            --noconfirm"""
        
        self.log_info("Building executable (this may take 3-5 minutes)...")
        if not self.run_command(cmd, "PyInstaller compilation"):
            self.log_error("PyInstaller build failed")
            return False
        
        exe_file = self.dist_dir / "EDUSCAN" / "EDUSCAN.exe"
        if not exe_file.exists():
            self.log_error("Executable not created")
            return False
        
        exe_size = exe_file.stat().st_size / (1024 * 1024)
        self.log_success(f"Executable created: {exe_file} ({exe_size:.1f}MB)")
        return True
    
    def step10_create_portable_zip(self):
        """Step 10: Create portable ZIP"""
        self.log_step(10, "Create Portable ZIP")
        
        self.log_info("Creating portable ZIP...")
        
        import zipfile
        
        zip_path = self.dist_dir / "EDUSCAN-Portable.zip"
        eduscan_dir = self.dist_dir / "EDUSCAN"
        
        if zip_path.exists():
            zip_path.unlink()
        
        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.dist_dir)
                    ziph.write(file_path, arcname)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipdir(eduscan_dir, zipf)
            
            zip_size = zip_path.stat().st_size / (1024 * 1024)
            self.log_success(f"Portable ZIP created: {zip_path} ({zip_size:.1f}MB)")
            return True
        except Exception as e:
            self.log_error(f"ZIP creation failed: {e}")
            return False
    
    def step11_create_installer(self):
        """Step 11: Create NSIS installer (if available)"""
        self.log_step(11, "Create Professional Installer")
        
        nsis_paths = [
            r"C:\Program Files\NSIS\makensis.exe",
            r"C:\Program Files (x86)\NSIS\makensis.exe",
        ]
        
        nsis_exe = None
        for path in nsis_paths:
            if os.path.exists(path):
                nsis_exe = path
                break
        
        if not nsis_exe:
            self.log_warning("NSIS not installed - skipping professional installer")
            self.log_info("To create installer: https://nsis.sourceforge.io/")
            return True
        
        self.log_info(f"Found NSIS: {nsis_exe}")
        self.log_info("Running NSIS compilation...")
        
        if self.run_command(f'"{nsis_exe}" installer.nsi', "NSIS compilation"):
            installer_file = self.dist_dir / "EDUSCAN-Installer.exe"
            if installer_file.exists():
                installer_size = installer_file.stat().st_size / (1024 * 1024)
                self.log_success(f"Installer created: {installer_file} ({installer_size:.1f}MB)")
                return True
        
        self.log_warning("NSIS compilation may have failed")
        return True
    
    def step12_final_summary(self):
        """Step 12: Final summary and verification"""
        self.log_step(12, "Final Summary")
        
        print("\n📦 BUILD ARTIFACTS:\n")
        
        artifacts = [
            ("Executable", self.dist_dir / "EDUSCAN" / "EDUSCAN.exe"),
            ("Portable ZIP", self.dist_dir / "EDUSCAN-Portable.zip"),
            ("Installer", self.dist_dir / "EDUSCAN-Installer.exe"),
        ]
        
        for name, path in artifacts:
            if path.exists():
                size = path.stat().st_size / (1024 * 1024)
                self.log_success(f"{name}: {path} ({size:.1f}MB)")
            else:
                if "Installer" in name:
                    self.log_info(f"{name}: Not created (NSIS not installed)")
                else:
                    self.log_warning(f"{name}: Not found")
        
        print("\n📋 DISTRIBUTION OPTIONS:\n")
        
        dist_zip = self.dist_dir / "EDUSCAN-Portable.zip"
        if dist_zip.exists():
            print(f"  Option 1 - Portable ZIP:")
            print(f"    File: {dist_zip.name}")
            print(f"    Use: Extract and run EDUSCAN.exe")
            print(f"    For: End users, USB drives, cloud storage\n")
        
        installer = self.dist_dir / "EDUSCAN-Installer.exe"
        if installer.exists():
            print(f"  Option 2 - Professional Installer:")
            print(f"    File: {installer.name}")
            print(f"    Use: Run installer, follow wizard")
            print(f"    For: Schools, IT deployment\n")
        
        folder = self.dist_dir / "EDUSCAN"
        if folder.exists():
            print(f"  Option 3 - Direct Folder:")
            print(f"    Path: {folder.name}/")
            print(f"    Use: Copy folder, run EDUSCAN.exe")
            print(f"    For: Network shares, CI/CD\n")
        
        print(f"{'='*70}")
        print("✨ BUILD COMPLETE - READY FOR DISTRIBUTION!")
        print(f"{'='*70}\n")
        
        return True
    
    def run_full_build(self):
        """Run complete build process"""
        print(f"\n{'='*70}")
        print("EDUSCAN PRODUCTION BUILD")
        print("Complete packaging for Windows distribution")
        print(f"{'='*70}\n")
        
        steps = [
            ("Verify Python Installation", self.step1_verify_python),
            ("Setup Virtual Environment", self.step2_setup_venv),
            ("Install Dependencies", self.step3_install_dependencies),
            ("Verify Asset Files", self.step4_verify_assets),
            ("Create Application Icon", self.step5_create_icon),
            ("Verify Database", self.step6_verify_database),
            ("Test Application Imports", self.step7_test_import),
            ("Clean Previous Builds", self.step8_clean_build),
            ("Build Executable", self.step9_build_executable),
            ("Create Portable ZIP", self.step10_create_portable_zip),
            ("Create Professional Installer", self.step11_create_installer),
            ("Final Summary", self.step12_final_summary),
        ]
        
        failed_steps = []
        
        for i, (title, step_func) in enumerate(steps, 1):
            try:
                if not step_func():
                    if "Optional" not in title and "Installer" not in title:
                        failed_steps.append((i, title))
                        print()
                        self.log_error(f"STEP {i} FAILED: {title}")
                        if i < len(steps):  # Don't stop for last step
                            response = input("\nContinue anyway? (y/n): ").lower()
                            if response != 'y':
                                break
            except Exception as e:
                failed_steps.append((i, title))
                self.log_error(f"STEP {i} ERROR: {e}")
        
        if failed_steps:
            print(f"\n⚠️  {len(failed_steps)} step(s) failed:")
            for step_num, title in failed_steps:
                print(f"    Step {step_num}: {title}")
        else:
            print("\n✅ All steps completed successfully!")
        
        return len(failed_steps) == 0

if __name__ == "__main__":
    builder = EDUSCANBuilder()
    success = builder.run_full_build()
    sys.exit(0 if success else 1)
