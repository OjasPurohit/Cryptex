"""
build_exe.py — Standalone Binary Builder for Cryptex - Secure File Encryption
Author: Ojas Purohit (https://github.com/OjasPurohit)

Compiles gui.py into a standalone native Windows binary (dist/Cryptex.exe).
"""

import os
import sys
import subprocess
import shutil

def build():
    print("=" * 65)
    print("  CRYPTEX STANDALONE NATIVE EXECUTABLE BUILDER")
    print("=" * 65)

    sep = ";" if sys.platform.startswith("win") else ":"
    icon_path = os.path.join("assets", "icon.ico")

    # Terminate any running instance of Cryptex.exe if on Windows
    if sys.platform.startswith("win"):
        try:
            subprocess.run(["taskkill", "/F", "/IM", "Cryptex.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # Clean old build/dist directories
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"[Clean] Removed {folder}/")
            except Exception as e:
                print(f"[Warning] Could not remove {folder}/: {e}")

    # Build PyInstaller Command
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
        "--collect-all", "psutil",
    ]

    if os.path.exists("assets"):
        cmd.extend(["--add-data", f"assets{sep}assets"])

    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")

    # Entry point: gui.py (Native Desktop GUI)
    cmd.append("gui.py")

    print("\n[Build] Executing PyInstaller with options:")
    for arg in cmd[3:]:
        print(f"   {arg}")

    print("\nPackaging standalone binary in progress (this may take ~30-60s)...")
    res = subprocess.run(cmd)

    if res.returncode == 0:
        exe_name = "Cryptex.exe" if sys.platform.startswith("win") else "Cryptex"
        exe_path = os.path.join("dist", exe_name)
        if os.path.exists(exe_path):
            sz_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print("\n" + "=" * 65)
            print("  BUILD SUCCESSFUL!")
            print(f"  Binary:   {os.path.abspath(exe_path)}")
            print(f"  Size:     {sz_mb:.2f} MB")
            print("=" * 65)
            return True

    print("\n[!] BUILD FAILED! Please inspect errors above.")
    return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)


