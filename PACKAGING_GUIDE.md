# 📦 EDUSCAN Windows Installer & Packaging Guide

## Overview
This guide covers creating a professional Windows installer for the EDUSCAN application with three distribution options:
- **NSIS Installer** (`.exe` - Recommended for end-users)
- **Portable ZIP** (`.zip` - No installation required)
- **Standalone Executable** (`.exe` - Direct run)

---

## 📋 Prerequisites

### System Requirements
- Windows 10 or later
- Python 3.8+
- Administrator access (for NSIS installer)
- At least 2GB disk space
- Webcam (for runtime use)

### Software to Install
1. **Python** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **NSIS** (for creating the Windows installer)
   - Download from: https://nsis.sourceforge.io/Download
   - Install to default location: `C:\Program Files\NSIS\`

---

## 🚀 Quick Build Steps

### Step 1: Prepare the Project
```powershell
cd C:\Users\waina\OneDrive\Documents\EDUSCAN

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Update pip
python -m pip install --upgrade pip

# Install build dependencies
pip install PyInstaller
```

### Step 2: Build the Installer
```powershell
# Run the build script
python build_installer.py
```

This will:
1. ✅ Clean previous build artifacts
2. ✅ Compile the application with PyInstaller
3. ✅ Create a portable ZIP version
4. ✅ Create an NSIS Windows installer (if installed)

### Step 3: Locate Output Files
After successful build, find the installers in the `dist/` folder:
```
dist/
├── EDUSCAN-Installer.exe        (Windows Installer - 400-500MB)
├── EDUSCAN-Portable.zip         (Portable Version - 400-500MB)
└── EDUSCAN/                      (Executable Directory)
    └── EDUSCAN.exe              (Standalone Executable)
```

---

## 📊 Distribution Options

### Option 1: NSIS Installer (Recommended for End-Users)
**File:** `EDUSCAN-Installer.exe`

**Advantages:**
- Professional Windows installer with uninstaller
- Start Menu shortcuts
- Desktop shortcut
- Registry entries
- Add/Remove Programs support
- ~400-500MB download

**Installation:**
1. Run `EDUSCAN-Installer.exe`
2. Follow the installation wizard
3. Click "Install"
4. Application automatically opens or check Start Menu

**Uninstallation:**
- Control Panel → Programs → EDUSCAN → Uninstall
- Or use Start Menu shortcut

---

### Option 2: Portable ZIP (No Installation)
**File:** `EDUSCAN-Portable.zip`

**Advantages:**
- No installation required
- No registry modifications
- Portable across USB drives
- No admin rights needed
- ~400-500MB download

**Usage:**
1. Extract `EDUSCAN-Portable.zip` anywhere
2. Navigate to extracted folder
3. Double-click `EDUSCAN.exe`
4. Application starts immediately

**Remove:**
- Simply delete the folder

---

### Option 3: Direct Executable (Manual Distribution)
**File:** `EDUSCAN.exe` (in `dist/EDUSCAN/`)

**Advantages:**
- Smallest footprint option
- Can be included in other installers
- Works standalone

**Usage:**
- Copy the entire `EDUSCAN/` folder
- Run `EDUSCAN.exe` directly

---

## 🔧 Advanced Build Options

### Rebuild Only the Executable (faster)
```powershell
python -m PyInstaller EDUSCAN.spec --noconfirm
```

### Clean Build
```powershell
# Remove all build artifacts
Remove-Item -Path build, dist, __pycache__ -Recurse -Force

# Rebuild
python build_installer.py
```

### Custom Build with Icon
1. Place `icon.ico` in the `assets/` folder
2. The build script will automatically use it
3. Rebuild the installer

---

## 📝 Distribution Checklist

Before distributing, verify:
- [ ] All dependencies in `requirements.txt`
- [ ] Database initialized (students.db created)
- [ ] Theme files included (light.qss, dark.qss)
- [ ] Assets folder complete
- [ ] Icon file present (optional)
- [ ] Test the installer on a clean Windows system
- [ ] Create `EDUSCAN-vX.X.X-Installer.exe` (version numbered)
- [ ] Create release notes

---

## 🛠️ Troubleshooting

### Error: "PyInstaller not found"
```powershell
pip install PyInstaller
python build_installer.py
```

### Error: "NSIS not found"
1. Install NSIS from: https://nsis.sourceforge.io/Download
2. Run installer with default settings
3. Rerun build script

### Executable won't launch
- Check Windows Defender/antivirus (may quarantine new executable)
- Try running with Admin privileges
- Run from unpacked `EDUSCAN/` folder instead

### Large file size (400-500MB)
This is normal due to:
- Python runtime (~50-70MB)
- PyQt5 libraries (~150MB)
- OpenCV & face_recognition (~100-150MB)
- To reduce: Use PyInstaller's UPX compression option

### Missing database on startup
The database is initialized automatically, but ensure:
- `database/` folder exists
- `student_db.py` is included in build

---

## 📤 Release Preparation

### Create a Release Package
```powershell
# Create version-numbered installer
$version = "1.0.0"
Copy-Item "dist/EDUSCAN-Installer.exe" "dist/EDUSCAN-v$version-Installer.exe"
Copy-Item "dist/EDUSCAN-Portable.zip" "dist/EDUSCAN-v$version-Portable.zip"
```

### Create Release Notes
```markdown
# EDUSCAN v1.0.0 Release Notes

## Features
- ✅ Facial recognition attendance
- ✅ Voice confirmation fallback
- ✅ Professional dashboard
- ✅ Dark/Light theme support
- ✅ Excel export

## Installation
Download and run EDUSCAN-Installer.exe

## System Requirements
- Windows 10 or later
- Webcam
- 2GB RAM minimum
```

---

## 🔗 References

- **PyInstaller Documentation:** https://pyinstaller.org/
- **NSIS Documentation:** https://nsis.sourceforge.io/Docs/
- **PyQt5:** https://www.riverbankcomputing.com/software/pyqt/

---

## 📞 Support

For issues with the installer:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Run build script with verbose output
4. Check Windows Event Viewer for errors

