"""
installer_app.py — Official Setup Wizard & Package Installer for Cryptex
Installs Cryptex to Program Files / AppData Programs, registers with Windows Control Panel,
creates Start Menu and Desktop shortcuts, and sets up dedicated user storage directories.
"""

import os
import sys
import shutil
import subprocess
import winreg
import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# High-DPI Awareness
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_NAME = "Cryptex"
APP_VERSION = "2.0.0"
PUBLISHER = "Ojas Purohit"
AUTHOR = "Ojas Purohit"
REG_SUBKEY = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def get_default_install_dir():
    if is_admin():
        prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        return os.path.join(prog_files, APP_NAME)
    else:
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser(r"~\AppData\Local"))
        return os.path.join(local_appdata, "Programs", APP_NAME)

def create_shortcut(target_path, shortcut_path, icon_path="", description=""):
    """Creates a standard Windows .lnk shortcut using PowerShell COM object."""
    try:
        os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
        ps_cmd = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{shortcut_path}"); '
            f'$s.TargetPath = "{target_path}"; '
            f'$s.WorkingDirectory = "{os.path.dirname(target_path)}"; '
        )
        if icon_path and os.path.exists(icon_path):
            ps_cmd += f'$s.IconLocation = "{icon_path},0"; '
        if description:
            ps_cmd += f'$s.Description = "{description}"; '
        ps_cmd += '$s.Save()'

        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        print(f"[Warning] Shortcut creation failed: {e}")
        return False

def register_in_control_panel(install_dir, exe_path, uninstaller_path, icon_path):
    """
    Registers the application in Windows Registry so it appears in
    Control Panel > Programs and Features and Windows 11 Settings > Installed apps.
    """
    hive = winreg.HKEY_LOCAL_MACHINE if is_admin() else winreg.HKEY_CURRENT_USER

    try:
        key = winreg.CreateKeyEx(hive, REG_SUBKEY, 0, winreg.KEY_WRITE)
        
        # Display Information
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Cryptex - Secure File Encryption")
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, f"{exe_path},0" if os.path.exists(exe_path) else icon_path)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
        
        # Uninstaller Information
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_path}"')
        winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, f'"{uninstaller_path}" /S')
        
        # Metadata
        winreg.SetValueEx(key, "InstallDate", 0, winreg.REG_SZ, datetime.datetime.now().strftime("%Y%m%d"))
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        
        # Calculate Estimated Size in KB
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(install_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, total_size // 1024)
        
        winreg.CloseKey(key)
        print("[Setup] Successfully registered in Windows Control Panel")
        return True
    except Exception as e:
        print(f"[Error] Failed to register in Control Panel: {e}")
        return False

class CryptexSetupWizard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cryptex - Secure File Encryption Setup")
        self.geometry("620x520")
        self.resizable(False, False)
        self.configure(fg_color="#000000")

        self.install_dir_var = tk.StringVar(value=get_default_install_dir())
        self.desktop_sc_var = tk.BooleanVar(value=True)
        self.start_sc_var = tk.BooleanVar(value=True)
        self.launch_after_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        # Header Banner
        header = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#0D0D0E",
                              border_width=1, border_color="#1E1E22")
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = ctk.CTkLabel(header, text="⚡ Cryptex Setup", font=("Segoe UI Variable Display", 20, "bold"),
                             text_color="#FFFFFF")
        title.pack(anchor="w", padx=24, pady=(16, 2))

        sub = ctk.CTkLabel(header, text="Cryptex - Secure File Encryption Installation",
                           font=("Segoe UI", 11), text_color="#94949C")
        sub.pack(anchor="w", padx=24)

        # Body Container
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)

        # Destination Folder Card
        dst_card = ctk.CTkFrame(body, corner_radius=10, fg_color="#0D0D0E",
                                border_width=1, border_color="#1E1E22")
        dst_card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=12)

        ctk.CTkLabel(dst_card, text="INSTALLATION DIRECTORY", font=("Segoe UI", 10, "bold"),
                     text_color="#94949C").pack(anchor="w", padx=14, pady=(6, 6))

        dir_row = ctk.CTkFrame(dst_card, fg_color="transparent")
        dir_row.pack(fill="x", padx=14, pady=(0, 6))

        dir_entry = ctk.CTkEntry(dir_row, textvariable=self.install_dir_var, font=("Segoe UI", 11),
                                 height=36, corner_radius=6, fg_color="#141416",
                                 border_width=1, border_color="#1E1E22")
        dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(dir_row, text="Browse...", width=80, height=36, font=("Segoe UI", 11, "bold"),
                                   corner_radius=6, fg_color="#171719", hover_color="#242428",
                                   text_color="#E4E4E7", border_width=1, border_color="#27272A",
                                   command=self.browse_dir)
        browse_btn.pack(side="right")

        # Shortcuts & Options Card
        opt_card = ctk.CTkFrame(body, corner_radius=10, fg_color="#0D0D0E",
                                border_width=1, border_color="#1E1E22")
        opt_card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=12)

        ctk.CTkLabel(opt_card, text="INSTALLATION OPTIONS", font=("Segoe UI", 10, "bold"),
                     text_color="#94949C").pack(anchor="w", padx=14, pady=(6, 8))

        ctk.CTkCheckBox(opt_card, text="Create Desktop Shortcut", variable=self.desktop_sc_var,
                        font=("Segoe UI", 11), text_color="#FFFFFF", fg_color="#FFFFFF",
                        checkmark_color="#000000").pack(anchor="w", padx=14, pady=4)

        ctk.CTkCheckBox(opt_card, text="Create Start Menu Program Shortcut", variable=self.start_sc_var,
                        font=("Segoe UI", 11), text_color="#FFFFFF", fg_color="#FFFFFF",
                        checkmark_color="#000000").pack(anchor="w", padx=14, pady=4)

        ctk.CTkCheckBox(opt_card, text="Launch Cryptex after installation finishes", variable=self.launch_after_var,
                        font=("Segoe UI", 11), text_color="#FFFFFF", fg_color="#FFFFFF",
                        checkmark_color="#000000").pack(anchor="w", padx=14, pady=4)

        # Progress Bar & Status
        self.progress_bar = ctk.CTkProgressBar(body, height=6, corner_radius=3,
                                               fg_color="#141416", progress_color="#FFFFFF")
        self.progress_bar.pack(fill="x", pady=(10, 4))
        self.progress_bar.set(0)

        self.status_lbl = ctk.CTkLabel(body, text="Ready to install.", font=("Segoe UI", 10),
                                       text_color="#94949C")
        self.status_lbl.pack(anchor="w")

        # Footer Actions
        footer = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#060607",
                              border_width=1, border_color="#1E1E22")
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        author_lbl = ctk.CTkLabel(footer, text="Created by Ojas Purohit", font=("Segoe UI", 10), text_color="#52525B")
        author_lbl.pack(side="left", padx=24, pady=12)

        self.cancel_btn = ctk.CTkButton(footer, text="Cancel", width=90, height=36,
                                        font=("Segoe UI", 11, "bold"), corner_radius=6,
                                        fg_color="#171719", hover_color="#242428",
                                        text_color="#E4E4E7", border_width=1, border_color="#27272A",
                                        command=self.destroy)
        self.cancel_btn.pack(side="right", padx=(6, 24), pady=12)

        self.install_btn = ctk.CTkButton(footer, text="Install Now", width=120, height=36,
                                         font=("Segoe UI", 11, "bold"), corner_radius=6,
                                         fg_color="#FFFFFF", hover_color="#E4E4E7",
                                         text_color="#000000", command=self.start_install_thread)
        self.install_btn.pack(side="right", pady=12)

    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.install_dir_var.get())
        if d:
            self.install_dir_var.set(os.path.join(d, APP_NAME))

    def start_install_thread(self):
        self.install_btn.configure(state="disabled", text="Installing...")
        self.cancel_btn.configure(state="disabled")
        threading.Thread(target=self._run_installation, daemon=True).start()

    def _update_status(self, text, progress):
        self.after(0, lambda: (self.status_lbl.configure(text=text), self.progress_bar.set(progress)))

    def _run_installation(self):
        target_dir = self.install_dir_var.get()
        self._update_status("Creating installation directories...", 0.15)
        os.makedirs(target_dir, exist_ok=True)

        # Source payload location (where installer is running from or bundled files)
        if getattr(sys, 'frozen', False):
            payload_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable)))
        else:
            payload_dir = os.path.dirname(os.path.abspath(__file__))

        # Assets folder
        dst_assets = os.path.join(target_dir, "assets")
        os.makedirs(dst_assets, exist_ok=True)
        src_assets = os.path.join(payload_dir, "assets")
        if os.path.exists(src_assets):
            try:
                shutil.copytree(src_assets, dst_assets, dirs_exist_ok=True)
            except Exception:
                pass

        icon_file = os.path.join(dst_assets, "icon.ico")
        if not os.path.exists(icon_file) and os.path.exists(os.path.join("assets", "icon.ico")):
            try:
                shutil.copy2(os.path.join("assets", "icon.ico"), icon_file)
            except Exception:
                pass

        self._update_status("Copying application binaries...", 0.45)
        # Look for Cryptex.exe and Uninstall.exe
        exe_src = os.path.join(payload_dir, "Cryptex.exe")
        if not os.path.exists(exe_src):
            exe_src = os.path.join("dist", "Cryptex.exe")

        exe_dst = os.path.join(target_dir, "Cryptex.exe")
        if os.path.exists(exe_src):
            shutil.copy2(exe_src, exe_dst)

        uninst_src = os.path.join(payload_dir, "Uninstall.exe")
        if not os.path.exists(uninst_src):
            uninst_src = os.path.join("dist", "Uninstall.exe")

        uninst_dst = os.path.join(target_dir, "Uninstall.exe")
        if os.path.exists(uninst_src):
            shutil.copy2(uninst_src, uninst_dst)

        self._update_status("Initializing dedicated user storage directories...", 0.65)
        try:
            from security import get_storage_dirs
            get_storage_dirs()
        except Exception:
            user_cryptex = os.path.join(os.path.expanduser("~"), "Cryptex")
            for sub_f in ["Encrypted", "Decrypted", "Vault"]:
                os.makedirs(os.path.join(user_cryptex, sub_f), exist_ok=True)

        self._update_status("Creating desktop & start menu shortcuts...", 0.80)
        if self.desktop_sc_var.get():
            dt_path = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop", f"{APP_NAME}.lnk")
            create_shortcut(exe_dst, dt_path, icon_file, "Cryptex Cryptographic Security Suite")

        if self.start_sc_var.get():
            sm_path = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs", f"{APP_NAME}.lnk")
            create_shortcut(exe_dst, sm_path, icon_file, "Cryptex Cryptographic Security Suite")

        self._update_status("Registering in Windows Control Panel (Programs and Features)...", 0.92)
        register_in_control_panel(target_dir, exe_dst, uninst_dst, icon_file)

        self._update_status("Installation completed successfully!", 1.0)

        if self.launch_after_var.get() and os.path.exists(exe_dst):
            try:
                subprocess.Popen([exe_dst], cwd=target_dir)
            except Exception:
                pass

        self.after(500, self._show_complete_dialog)

    def _show_complete_dialog(self):
        messagebox.showinfo("Setup Completed", f"{APP_NAME} has been installed successfully!\n\n"
                                               f"Installed to: {self.install_dir_var.get()}\n"
                                               f"Storage Directory: ~/Cryptex\n\n"
                                               f"You can now access Cryptex via Start Menu, Desktop, and Windows Control Panel.")
        self.destroy()

if __name__ == "__main__":
    app = CryptexSetupWizard()
    app.mainloop()

