# 🎯 EDUSCAN Professional Installer - Complete Guide

## Overview

The EDUSCAN installer includes a **professional Windows wizard** with multiple customization options for end-users. This guide explains what happens during installation.

---

## 📦 Installer Features

### 1. Welcome Wizard
- Professional branding
- System requirements display
- License agreement option
- Next/Back/Cancel navigation

### 2. Custom Installation Dialog
Users can select:
- ✅ **Desktop Shortcut** - Quick access from desktop
- ✅ **Start Menu Shortcuts** - Windows Start Menu integration
- ✅ **Add to System PATH** - Command-line access (recommended)
- ✅ **File Association** - Open .face files with EDUSCAN

### 3. Installation Options
- **Installation Location** - Choose where to install (default: C:\Program Files\EDUSCAN)
- **Component Selection** - Select what to install
- **Installation Progress** - Real-time progress tracking

### 4. After Installation
- Option to launch EDUSCAN immediately
- Desktop and Start Menu shortcuts created
- Registry entries for uninstall
- Optional PATH configuration

---

## 🚀 Installation Flow

### Step 1: User Runs Installer
```
User double-clicks: EDUSCAN-Installer.exe
↓
Admin prompt appears (Windows security)
```

### Step 2: Welcome Screen
```
┌─────────────────────────────────────┐
│  Welcome to EDUSCAN Setup Wizard    │
│                                     │
│  This will install EDUSCAN on your  │
│  computer.                          │
│                                     │
│  System Requirements:               │
│  • Windows 10 or later              │
│  • 2GB RAM                          │
│  • 1GB disk space                   │
│  • Webcam (for attendance)          │
│                                     │
│  [Next] [Cancel]                    │
└─────────────────────────────────────┘
```

### Step 3: License (Optional)
```
User reviews license agreement
Clicks "I Agree" and "Next"
```

### Step 4: Custom Installation Options
```
┌─────────────────────────────────────┐
│     Installation Options            │
│                                     │
│ ☑ Create Desktop Shortcut           │
│ ☑ Add to Start Menu                 │
│ ☑ Add EDUSCAN to System PATH        │
│ ☐ Associate .face files             │
│                                     │
│  [Next] [Back] [Cancel]             │
└─────────────────────────────────────┘
```

### Step 5: Installation Location
```
User selects installation folder
Default: C:\Program Files\EDUSCAN
Can change to any location
```

### Step 6: Installation Progress
```
┌─────────────────────────────────────┐
│  Installing EDUSCAN...              │
│                                     │
│  ████████░░░░░░░░░░░  45%           │
│                                     │
│  Extracting files...                │
│  Creating shortcuts...              │
│  Updating system PATH...            │
│                                     │
└─────────────────────────────────────┘
```

### Step 7: Completion
```
┌─────────────────────────────────────┐
│  Installation Complete!             │
│                                     │
│  EDUSCAN has been successfully      │
│  installed on your computer.        │
│                                     │
│  Installed to:                      │
│  C:\Program Files\EDUSCAN           │
│                                     │
│  [Finish]                           │
└─────────────────────────────────────┘

"Launch EDUSCAN now?" Yes/No
```

---

## 🔧 Installation Options Explained

### 1. Desktop Shortcut
**What it does:**
- Creates a shortcut icon on the desktop
- Double-click to launch EDUSCAN

**Benefit:** Quick access without navigating menus

### 2. Start Menu Shortcuts
**What it does:**
- Adds EDUSCAN folder to Windows Start Menu
- Creates launch and uninstall shortcuts
- Adds documentation shortcuts

**Benefit:** Professional Windows integration

**Location after install:**
```
Start Menu → EDUSCAN
├── EDUSCAN
├── Uninstall
└── Documentation
    └── README
```

### 3. Add to System PATH
**What it does:**
- Adds installation folder to Windows PATH environment variable
- Allows running EDUSCAN from command line anywhere
- Updates registry and broadcasts changes

**Commands available after:**
```powershell
eduscan              # Launch from anywhere in PowerShell
cd C:\Users\...
EDUSCAN.exe         # Run from any folder
```

**Benefit:** 
- Developer-friendly
- Batch script compatibility
- System-wide access

**Note:** User may need to restart for full PATH effect

### 4. File Association
**What it does:**
- Associates .face files with EDUSCAN
- Double-clicking .face files opens in EDUSCAN
- EDUSCAN appears in file type options

**Benefit:** Seamless file handling in Windows Explorer

---

## 📍 What Gets Installed Where

### Default Installation Structure
```
C:\Program Files\EDUSCAN\
├── EDUSCAN.exe              ← Main executable
├── _internal\               ← Runtime libraries
│   ├── python39.dll
│   ├── PyQt5
│   ├── cv2
│   └── ...
├── database/                ← Local database files
├── themes/                  ← Light/dark themes
├── uninstall.exe           ← Uninstaller
└── [other files]
```

### Registry Entries
**Installation info:**
```
HKEY_LOCAL_MACHINE\Software\EDUSCAN
├── Install_Dir = C:\Program Files\EDUSCAN
├── Version = 1.0.0
└── Date = [installation date]
```

**Uninstall info:**
```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\
  CurrentVersion\Uninstall\EDUSCAN
├── DisplayName = EDUSCAN - Smart Attendance System
├── UninstallString = C:\Program Files\EDUSCAN\uninstall.exe
├── InstallLocation = C:\Program Files\EDUSCAN
├── Publisher = EDUSCAN Team
└── Version = 1.0.0
```

**File association:**
```
HKEY_CLASSES_ROOT
├── .face
└── EDUSCAN.FaceFile
    └── shell\open\command = EDUSCAN.exe "%1"
```

---

## 🗑️ Uninstallation

### Method 1: Start Menu
```
Start Menu → EDUSCAN → Uninstall
↓
Uninstall wizard appears
↓
Complete → Application removed
```

### Method 2: Settings
```
Settings → Apps → Apps & Features
↓
Search "EDUSCAN"
↓
Click → Uninstall
↓
Follow prompts
```

### Method 3: Direct
```
C:\Program Files\EDUSCAN\uninstall.exe
↓
Wizard appears
↓
Complete
```

### What Gets Removed
- ✅ All application files
- ✅ Start Menu shortcuts
- ✅ Desktop shortcut
- ✅ System PATH entry (if added)
- ✅ Registry entries
- ✅ File associations
- ✅ Uninstaller itself

### What Stays (User Data)
- Database files (user choice)
- Configuration files
- Attendance logs (if stored externally)

---

## 🎨 Customization Options

### Change Installation Location
**During Installation:**
1. Step 5: "Installation Location"
2. Click "Browse"
3. Select new folder
4. Continue

**Examples:**
```
C:\Users\[Username]\AppData\Local\EDUSCAN
D:\School\EDUSCAN
E:\PortableApps\EDUSCAN
```

### Selective Installation
**During Installation:**
1. Step 4: Uncheck unwanted options
   - Don't want desktop shortcut? Uncheck
   - Don't want Start Menu? Uncheck
   - Don't want PATH? Uncheck

### Silent Installation
**For IT Departments (Advanced):**
```powershell
EDUSCAN-Installer.exe /S /D=C:\EDUSCAN
```

Parameters:
- `/S` - Silent mode
- `/D=` - Installation directory

---

## 🔐 Security & Permissions

### Admin Rights Required
- Writing to `Program Files` folder
- Modifying Windows registry
- Updating system PATH
- File associations

**Why?** System-wide integration requires elevated privileges.

### UAC Prompt
Windows shows "User Account Control" prompt:
```
Do you want to allow this app to make changes to your device?

Publisher: Unknown (self-signed)
Application: EDUSCAN-Installer.exe

[Yes] [No]
```

**User must click "Yes" to continue.**

---

## ⚠️ Troubleshooting

### "Setup failed to initialize"
- Check disk space (need 1GB minimum)
- Disable antivirus temporarily
- Run as Administrator
- Try from different location

### "Access denied" during installation
- Close EDUSCAN if running
- Ensure no files locked
- Restart installer
- Run as Administrator

### PATH not updating
- Restart computer for full effect
- Check "Add to System PATH" was selected
- Manually add path if needed:
  ```
  Control Panel → System → Environment Variables
  → New User Variable
  → Variable name: PATH
  → Value: C:\Program Files\EDUSCAN;%PATH%
  ```

### Uninstall fails
- Close EDUSCAN completely
- Delete locked files manually
- Use "Clean Registry" tool
- Reinstall and try again

---

## 📊 Installation Statistics

| Metric | Value |
|--------|-------|
| Installer Size | 450-550 MB |
| Installed Size | 450-550 MB |
| Installation Time | 2-5 minutes |
| Registry Entries | ~20 entries |
| System PATH Size | +55 characters |
| Disk Space After | ~500 MB minimum |

---

## 🎯 User Instructions

### For End-Users

**Installation:**
1. Download `EDUSCAN-Installer.exe`
2. Right-click → "Run as Administrator"
3. Click "Yes" on UAC prompt
4. Click "Next" through wizard
5. Select your options
6. Click "Install"
7. Wait for completion
8. Launch EDUSCAN

**Uninstallation:**
1. Go to Start Menu → Settings → Apps
2. Search "EDUSCAN"
3. Click "Uninstall"
4. Confirm

**Troubleshooting:**
- If admin prompt doesn't appear: Right-click installer, "Run as Administrator"
- If antivirus blocks: Add to whitelist
- If PATH doesn't work: Restart computer

---

## 🔗 Advanced Configuration

### Batch Installation Script
```powershell
# install_eduscan.ps1
$installer = "EDUSCAN-Installer.exe"
$installDir = "C:\Program Files\EDUSCAN"

# Run silent installation
& $installer /S /D=$installDir

# Verify installation
if (Test-Path "$installDir\EDUSCAN.exe") {
    Write-Host "✅ Installation successful"
    & "$installDir\EDUSCAN.exe"
} else {
    Write-Host "❌ Installation failed"
}
```

### Uninstall Script
```powershell
# uninstall_eduscan.ps1
$uninstaller = "C:\Program Files\EDUSCAN\uninstall.exe"

if (Test-Path $uninstaller) {
    & $uninstaller /S
    Write-Host "✅ Uninstall complete"
}
```

---

## 📝 Summary

The EDUSCAN installer provides:
- ✅ Professional wizard interface
- ✅ Customizable installation options
- ✅ System integration (PATH, shortcuts, registry)
- ✅ File association support
- ✅ Clean uninstallation
- ✅ User-friendly prompts
- ✅ Progress tracking
- ✅ Auto-launch capability

This makes distribution to schools, labs, and individual users seamless and professional.

