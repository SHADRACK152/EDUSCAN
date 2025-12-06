"""
Build script for creating Windows installer for EDUSCAN
Run this script to generate the standalone executable and installer
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
        return True

def check_nsis():
    """Check if NSIS is installed"""
    nsis_paths = [
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\Program Files (x86)\NSIS\makensis.exe",
    ]
    for path in nsis_paths:
        if os.path.exists(path):
            return path
    print("⚠️  NSIS not found. Please install it from: https://nsis.sourceforge.io/")
    print("   After installation, run this script again.")
    return None

def clean_build_dirs():
    """Clean previous build artifacts"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🗑️  Removing {dir_name}/...")
            shutil.rmtree(dir_name)

def build_executable():
    """Build standalone executable using PyInstaller"""
    print("\n🔨 Building executable with PyInstaller...")
    
    # Check if icon exists
    icon_file = 'assets/icon.ico'
    has_icon = os.path.exists(icon_file)
    
    if not has_icon:
        print("⚠️  Icon not found at assets/icon.ico - creating default icon...")
        try:
            from PIL import Image
            img = Image.new('RGB', (256, 256), (9, 105, 218))
            img.ellipse([(30, 30), (226, 226)], outline=(255, 255, 255), width=4)
            os.makedirs('assets', exist_ok=True)
            img.save(icon_file, 'ICO', sizes=[256])
            print("✅ Default icon created")
            has_icon = True
        except ImportError:
            print("⚠️  PIL not available - skipping custom icon")
    
    icon_param = f"'icon={icon_file}'" if has_icon else "None"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui', 'gui'),
        ('face_engine', 'face_engine'),
        ('voice_engine', 'voice_engine'),
        ('database', 'database'),
        ('assets', 'assets'),
        ('themes', 'themes'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'cv2',
        'face_recognition',
        'dlib',
        'sqlite3',
        'pyttsx3',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EDUSCAN',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_param},
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EDUSCAN',
)
'''
    
    # Write spec file
    with open('EDUSCAN.spec', 'w') as f:
        f.write(spec_content)
    
    # Run PyInstaller
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "EDUSCAN.spec", "--noconfirm"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Executable built successfully!")
        return True
    else:
        print("❌ Build failed:")
        print(result.stderr)
        return False

def create_nsis_installer(nsis_path):
    """Create NSIS installer script and build installer"""
    print("\n📦 Creating NSIS installer with wizard...")
    
    nsis_script = r'''
; ============================================================================
; EDUSCAN - Smart Attendance System Installer
; Professional Windows Installer with Full Wizard
; ============================================================================

!include "MUI2.nsh"
!include "x64.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"

; ============================================================================
; INSTALLER SETTINGS
; ============================================================================

Name "EDUSCAN - Smart Attendance System v1.0.0"
OutFile "dist\EDUSCAN-Installer.exe"
InstallDir "$PROGRAMFILES\EDUSCAN"
InstallDirRegKey HKLM "Software\EDUSCAN" "Install_Dir"

; Request admin privileges
RequestExecutionLevel admin

; Compression
SetCompress force
SetDatablockOptimize on
CRCCheck on

; ============================================================================
; MUI SETTINGS - WIZARD PAGES
; ============================================================================

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
Page custom nsDialogsPage nsDialogsPageLeave
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; ============================================================================
; CUSTOM INSTALLER DIALOG FOR OPTIONS
; ============================================================================

Var Dialog
Var CheckBoxDesktop
Var CheckBoxStartMenu
Var CheckBoxPath
Var CheckBoxAssociate

Function nsDialogsPage
  nsDialogs::Create 1018
  Pop $Dialog

  ${If} $Dialog == error
    Abort
  ${EndIf}

  ; Title
  ${NSD_CreateLabel} 0 0 100% 12u "Installation Options"
  Pop $0
  SendMessage $0 ${WM_SETFONT} -1 0

  ; Options
  ${NSD_CreateCheckBox} 0 15u 100% 10u "Create Desktop Shortcut"
  Pop $CheckBoxDesktop
  ${NSD_Check} $CheckBoxDesktop

  ${NSD_CreateCheckBox} 0 28u 100% 10u "Add to Start Menu"
  Pop $CheckBoxStartMenu
  ${NSD_Check} $CheckBoxStartMenu

  ${NSD_CreateCheckBox} 0 41u 100% 10u "Add EDUSCAN folder to System PATH (recommended)"
  Pop $CheckBoxPath
  ${NSD_Check} $CheckBoxPath

  ${NSD_CreateCheckBox} 0 54u 100% 10u "Associate .face files with EDUSCAN"
  Pop $CheckBoxAssociate

  nsDialogs::Show
FunctionEnd

Function nsDialogsPageLeave
  ${NSD_GetState} $CheckBoxDesktop $0
  StrCpy $CreateDesktopShortcut $0

  ${NSD_GetState} $CheckBoxStartMenu $0
  StrCpy $CreateStartMenuShortcut $0

  ${NSD_GetState} $CheckBoxPath $0
  StrCpy $AddToPath $0

  ${NSD_GetState} $CheckBoxAssociate $0
  StrCpy $AssociateFiles $0
FunctionEnd

; ============================================================================
; SECTION 1: CORE APPLICATION (MANDATORY)
; ============================================================================

Section "!EDUSCAN Application" SectionCore
  SectionIn RO  ; Read-only - mandatory
  
  SetOutPath "$INSTDIR"
  
  ; Display progress
  DetailPrint "Installing EDUSCAN application files..."
  File /r "dist\EDUSCAN\*.*"
  
  ; Create registry keys
  WriteRegStr HKLM "Software\EDUSCAN" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\EDUSCAN" "Version" "1.0.0"
  WriteRegStr HKLM "Software\EDUSCAN" "Date" "$%DATE%"
  
  ; Write uninstaller
  DetailPrint "Creating uninstaller..."
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Add to Programs list
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN" "DisplayName" "EDUSCAN - Smart Attendance System"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN" "Publisher" "EDUSCAN Team"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN" "Version" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN" "DisplayIcon" "$INSTDIR\EDUSCAN.exe,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN" "HelpLink" "https://github.com/SHADRACK152/EDUSCAN"
  
  DetailPrint "Application installation complete."
SectionEnd

; ============================================================================
; SECTION 2: START MENU SHORTCUTS
; ============================================================================

Section "Start Menu Shortcuts" SectionStartMenu
  ${If} $CreateStartMenuShortcut == 1
    DetailPrint "Creating Start Menu shortcuts..."
    CreateDirectory "$SMPROGRAMS\EDUSCAN"
    CreateShortcut "$SMPROGRAMS\EDUSCAN\EDUSCAN.lnk" "$INSTDIR\EDUSCAN.exe" "" "$INSTDIR\EDUSCAN.exe" 0
    CreateShortcut "$SMPROGRAMS\EDUSCAN\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateDirectory "$SMPROGRAMS\EDUSCAN\Documentation"
    CreateShortcut "$SMPROGRAMS\EDUSCAN\Documentation\README.lnk" "$INSTDIR\README.txt"
  ${EndIf}
SectionEnd

; ============================================================================
; SECTION 3: DESKTOP SHORTCUT
; ============================================================================

Section "Desktop Shortcut" SectionDesktop
  ${If} $CreateDesktopShortcut == 1
    DetailPrint "Creating desktop shortcut..."
    CreateShortcut "$DESKTOP\EDUSCAN.lnk" "$INSTDIR\EDUSCAN.exe" "" "$INSTDIR\EDUSCAN.exe" 0
  ${EndIf}
SectionEnd

; ============================================================================
; SECTION 4: ADD TO PATH
; ============================================================================

Section "Add to PATH" SectionPath
  ${If} $AddToPath == 1
    DetailPrint "Adding EDUSCAN to system PATH..."
    ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR"
    DetailPrint "PATH updated successfully. You may need to restart for changes to take effect."
  ${EndIf}
SectionEnd

; ============================================================================
; SECTION 5: FILE ASSOCIATIONS
; ============================================================================

Section "File Associations" SectionAssoc
  ${If} $AssociateFiles == 1
    DetailPrint "Setting up file associations..."
    WriteRegStr HKCR ".face" "" "EDUSCAN.FaceFile"
    WriteRegStr HKCR "EDUSCAN.FaceFile" "" "EDUSCAN Face Recognition File"
    WriteRegStr HKCR "EDUSCAN.FaceFile\DefaultIcon" "" "$INSTDIR\EDUSCAN.exe,0"
    WriteRegStr HKCR "EDUSCAN.FaceFile\shell\open\command" "" "$INSTDIR\EDUSCAN.exe ""%1"""
  ${EndIf}
SectionEnd

; ============================================================================
; SECTION DESCRIPTIONS
; ============================================================================

LangString DESC_SectionCore ${LANG_ENGLISH} "The EDUSCAN application and all required files."
LangString DESC_SectionStartMenu ${LANG_ENGLISH} "Add shortcuts to the Start Menu for easy access."
LangString DESC_SectionDesktop ${LANG_ENGLISH} "Create a shortcut on your desktop."
LangString DESC_SectionPath ${LANG_ENGLISH} "Add EDUSCAN to your system PATH for command-line access."
LangString DESC_SectionAssoc ${LANG_ENGLISH} "Associate EDUSCAN face files with this application."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionCore} $(DESC_SectionCore)
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionStartMenu} $(DESC_SectionStartMenu)
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionDesktop} $(DESC_SectionDesktop)
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionPath} $(DESC_SectionPath)
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionAssoc} $(DESC_SectionAssoc)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ============================================================================
; UNINSTALLER
; ============================================================================

Section "Uninstall"
  DetailPrint "Uninstalling EDUSCAN..."
  
  ; Remove from PATH if it was added
  ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR"
  
  ; Remove files
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  RMDir /r "$SMPROGRAMS\EDUSCAN"
  Delete "$DESKTOP\EDUSCAN.lnk"
  
  ; Remove registry entries
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EDUSCAN"
  DeleteRegKey HKLM "Software\EDUSCAN"
  DeleteRegKey HKCR ".face"
  DeleteRegKey HKCR "EDUSCAN.FaceFile"
  
  DetailPrint "Uninstallation complete."
SectionEnd

; ============================================================================
; INSTALLER INITIALIZATION
; ============================================================================

Function .onInit
  ; Set default checkbox states
  StrCpy $CreateDesktopShortcut 1
  StrCpy $CreateStartMenuShortcut 1
  StrCpy $AddToPath 1
  StrCpy $AssociateFiles 0
FunctionEnd

; ============================================================================
; FINISH FUNCTION - RUN APPLICATION
; ============================================================================

Function .onInstSuccess
  MessageBox MB_YESNO "EDUSCAN installed successfully.$\n$\nDo you want to launch EDUSCAN now?" IDNO +2
  Exec "$INSTDIR\EDUSCAN.exe"
FunctionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    # Ensure EnvVarUpdate macro is available
    macro_script = r'''
!define EnvVarUpdate "!insertmacro EnvVarUpdate"

!macro EnvVarUpdate un Path Strng Value WinVer
!insertmacro${un}EnvVarUpdateImpl ${Path} ${Strng} ${Value} ${WinVer}
!macroend

!macro un.EnvVarUpdate Path Strng Value WinVer
!insertmacro EnvVarUpdateImpl un ${Path} ${Strng} ${Value} ${WinVer}
!macroend

!macro EnvVarUpdateImpl un Path Strng Value WinVer
Push "${Path}"     ; Path
Push "${Strng}"    ; String
Push "${Value}"    ; Value (A=Append, P=Prepend, R=Remove, empty=Replace)
Push "${WinVer}"   ; Execution level
Call ${un}EnvVarUpdate_Impl
!macroend

Function un.EnvVarUpdate_Impl
Exch $3
Exch 1
Exch $2
Exch 2
Exch $1
Exch 3
Exch $0

  DetailPrint "Updating $1 environment variable..."
  
  ${If} $1 == "PATH"
    ${If} $2 == "A"
      WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH" "%PATH%;$3"
    ${ElseIf} $2 == "R"
      ReadRegStr $4 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH"
      ${StrReplace} $4 "$3;" "" $4
      WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH" "$4"
    ${EndIf}
  ${EndIf}
  
  SendMessage ${HWND_BROADCAST} ${WM_SETTINGCHANGE} 0 "STR:Environment" /TIMEOUT=5000
  
  Pop $0
  Pop $1
  Pop $2
  Pop $3
FunctionEnd

!macro StrReplace output string old new
  Push "${string}"
  Push "${old}"
  Push "${new}"
  Call StrReplace_Impl
  Pop "${output}"
!macroend

Function StrReplace_Impl
  Exch $2
  Exch 1
  Exch $1
  Exch 2
  Exch $0
  Push $3
  Push $4
  
  ${StrReplace} $0 $1 $2 $0
  
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0
FunctionEnd
'''
    
    # Append macro script to NSIS file
    with open('installer.nsi', 'a') as f:
        f.write('\n\n; Environment Variable Update Macro\n')
        f.write(macro_script)
    
    # Build installer
    result = subprocess.run(
        [nsis_path, 'installer.nsi'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Installer created successfully!")
        return True
    else:
        print("❌ Installer creation failed:")
        print(result.stderr)
        return False

def create_portable_zip():
    """Create a portable ZIP version"""
    print("\n📦 Creating portable ZIP...")
    
    if os.path.exists('dist/EDUSCAN'):
        shutil.make_archive(
            'dist/EDUSCAN-Portable',
            'zip',
            'dist',
            'EDUSCAN'
        )
        print("✅ Portable ZIP created: dist/EDUSCAN-Portable.zip")

def main():
    print("=" * 60)
    print("EDUSCAN Windows Installer Builder")
    print("=" * 60)
    
    # Check prerequisites
    if not check_pyinstaller():
        return False
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create portable ZIP
    create_portable_zip()
    
    # Check for NSIS and create installer
    nsis_path = check_nsis()
    if nsis_path:
        if create_nsis_installer(nsis_path):
            print("\n" + "=" * 60)
            print("✅ Build Complete!")
            print("=" * 60)
            print("📁 Output files:")
            print("  • Portable: dist/EDUSCAN-Portable.zip")
            print("  • Installer: dist/EDUSCAN-Installer.exe")
            print("  • Executable: dist/EDUSCAN/EDUSCAN.exe")
            print("\n🎯 Installer Features:")
            print("  ✓ Welcome wizard")
            print("  ✓ Custom installation options")
            print("  ✓ Desktop shortcut option")
            print("  ✓ Start Menu shortcuts")
            print("  ✓ Add to System PATH (recommended)")
            print("  ✓ File association support")
            print("  ✓ Progress tracking")
            print("  ✓ Uninstaller included")
            print("  ✓ Auto-launch after install")
            return True
    else:
        print("\n" + "=" * 60)
        print("⚠️  Partial Build Complete")
        print("=" * 60)
        print("📁 Available output files:")
        print("  • Portable: dist/EDUSCAN-Portable.zip")
        print("  • Executable: dist/EDUSCAN/EDUSCAN.exe")
        print("\n💡 To create the professional NSIS installer with wizard:")
        print("  1. Install NSIS from: https://nsis.sourceforge.io/")
        print("  2. Run this script again: python build_installer.py")
        print("\n🎯 The installer will include:")
        print("  ✓ Welcome wizard with system requirements")
        print("  ✓ Custom installation dialog")
        print("  ✓ Desktop & Start Menu shortcuts")
        print("  ✓ Add to System PATH option")
        print("  ✓ File association setup")
        print("  ✓ Auto-launch after installation")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
