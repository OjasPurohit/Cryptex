"""
uninstall_app.py — Official Uninstaller for Cryptex - Secure File Encryption
Part of Cryptex - Secure File Encryption
Author: Ojas Purohit (https://github.com/OjasPurohit)

Removes Cryptex binaries, Start Menu / Desktop shortcuts, and Windows Registry entries
from Windows Control Panel (Programs and Features).
"""

import os
import sys
import shutil
import subprocess
import winreg
import tkinter as tk
from tkinter import messagebox

APP_NAME = "Cryptex"
REG_SUBKEY = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"

def is_silent():
    return "/S" in [arg.upper() for arg in sys.argv]

def remove_registry_keys():
    for hive, hive_name in [(winreg.HKEY_CURRENT_USER, "HKCU"), (winreg.HKEY_LOCAL_MACHINE, "HKLM")]:
        try:
            winreg.DeleteKey(hive, REG_SUBKEY)
            print(f"[Uninstall] Removed registry key from {hive_name}")
        except Exception:
            pass

def remove_shortcuts():
    shortcut_locations = [
        os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs", f"{APP_NAME}.lnk"),
        os.path.join(os.environ.get("ALLUSERSPROFILE", ""), r"Microsoft\Windows\Start Menu\Programs", f"{APP_NAME}.lnk"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", f"{APP_NAME}.lnk"),
        os.path.join(os.environ.get("PUBLIC", ""), "Desktop", f"{APP_NAME}.lnk"),
    ]
    for sc in shortcut_locations:
        if os.path.exists(sc):
            try:
                os.remove(sc)
                print(f"[Uninstall] Removed shortcut: {sc}")
            except Exception as e:
                print(f"[Warning] Could not remove shortcut {sc}: {e}")

def terminate_running_instances():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "Cryptex.exe"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def perform_uninstall():
    if not is_silent():
        root = tk.Tk()
        root.withdraw()
        confirm = messagebox.askyesno(
            "Uninstall Cryptex - Secure File Encryption",
            "Are you sure you want to completely uninstall Cryptex from your system?\n\n"
            "Note: Your encrypted files in ~/Cryptex will remain safe and will not be deleted.",
            icon="warning"
        )
        if not confirm:
            sys.exit(0)

    terminate_running_instances()
    remove_registry_keys()
    remove_shortcuts()

    # Determine install directory
    install_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

    # Spawn delayed self-deletion batch script to remove the installation directory
    batch_content = f'''@echo off
ping 127.0.0.1 -n 3 > nul
rmdir /s /q "{install_dir}"
del "%~f0"
'''
    temp_bat = os.path.join(os.environ.get("TEMP", "."), "cryptex_cleanup.bat")
    try:
        with open(temp_bat, "w") as f:
            f.write(batch_content)
        subprocess.Popen(["cmd.exe", "/c", temp_bat], shell=True)
    except Exception as e:
        print(f"[Warning] Could not create self-deletion bat: {e}")

    if not is_silent():
        messagebox.showinfo("Cryptex Uninstaller", "Cryptex has been successfully removed from your computer.")

    sys.exit(0)

if __name__ == "__main__":
    perform_uninstall()

