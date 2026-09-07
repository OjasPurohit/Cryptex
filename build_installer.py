"""
build_installer.py — Master Build Script for Cryptex - Secure File Encryption Suite
Author: Ojas Purohit (https://github.com/OjasPurohit)

Compiles:
  1. dist/Cryptex.exe       (Standalone Cryptographic GUI Client)
  2. dist/Uninstall.exe     (Standalone Clean Uninstaller)
  3. dist/Cryptex_Setup.exe (Standalone Setup Wizard for Windows with Control Panel & Program Files integration)
"""

import os
import sys
import shutil
import subprocess

# Ensure safe console output encoding on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def terminate_running_instances():
    if sys.platform.startswith("win"):
        for exe in ["Cryptex.exe", "Uninstall.exe", "Cryptex_Setup.exe"]:
            try:
                subprocess.run(["taskkill", "/F", "/IM", exe],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

def build_cryptex_main():
    print("\n[1/3] Compiling Cryptex.exe...")
    sep = ";" if sys.platform.startswith("win") else ":"
    icon_path = os.path.join("assets", "icon.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=Cryptex",
        "--clean",
        "--collect-all", "customtkinter",
        "--collect-all", "tkinterdnd2",
        "--collect-all", "PIL",
        "--collect-all", "cryptography",
    ]
    if os.path.exists("assets"):
        cmd.extend(["--add-data", f"assets{sep}assets"])
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    cmd.append("gui.py")

    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError("Failed to build Cryptex.exe")
    print("[+] Successfully built dist/Cryptex.exe")

def build_uninstaller():
    print("\n[2/3] Compiling Uninstall.exe...")
    icon_path = os.path.join("assets", "icon.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=Uninstall",
        "--clean",
    ]
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    cmd.append("uninstall_app.py")

    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError("Failed to build Uninstall.exe")
    print("[+] Successfully built dist/Uninstall.exe")

def build_setup_installer():
    print("\n[3/3] Compiling Cryptex_Setup.exe (Windows Setup Installer)...")
    sep = ";" if sys.platform.startswith("win") else ":"
    icon_path = os.path.join("assets", "icon.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=Cryptex_Setup",
        "--clean",
        "--collect-all", "customtkinter",
        "--add-data", f"dist/Cryptex.exe{sep}.",
        "--add-data", f"dist/Uninstall.exe{sep}.",
    ]
    if os.path.exists("assets"):
        cmd.extend(["--add-data", f"assets{sep}assets"])
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    cmd.append("installer_app.py")

    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError("Failed to build Cryptex_Setup.exe")
    print("[+] Successfully built dist/Cryptex_Setup.exe")

def main():
    print("=" * 70)
    print("  CRYPTEX MASTER WINDOWS BINARY & SETUP INSTALLER BUILDER")
    print("=" * 70)

    terminate_running_instances()

    # Build sequence
    build_cryptex_main()
    build_uninstaller()
    build_setup_installer()

    print("\n" + "=" * 70)
    print("  ALL BUILDS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    for exe in ["Cryptex.exe", "Uninstall.exe", "Cryptex_Setup.exe"]:
        p = os.path.join("dist", exe)
        if os.path.exists(p):
            sz_mb = os.path.getsize(p) / (1024 * 1024)
            print(f"  - {exe:20} -> {os.path.abspath(p)} ({sz_mb:.2f} MB)")
    print("=" * 70)

if __name__ == "__main__":
    main()


