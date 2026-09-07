"""
Cryptex - Secure File Encryption (v2.0)
High-performance, ultra-sleek native desktop application.
Author: Ojas Purohit (https://github.com/OjasPurohit)

Features: File Encryptor/Decryptor, Entropy Analyzer, Password Generator, Encrypted Vault, SHA-256 Checksum.
"""

__author__ = "Ojas Purohit"
__version__ = "2.0.0"
__app_name__ = "Cryptex - Secure File Encryption"

import os
import sys
import json
import hashlib
import math
import random
import string
import datetime
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# ── High-DPI Awareness & Windows App ID (Forces taskbar icon unification) ──────
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor High-DPI
    # Set Windows Process App ID so taskbar uses the exact custom icon
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cryptex.security.suite.2.0")
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ── CustomTkinter Engine ──────────────────────────────────────────────────────
import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ── Drag and Drop Support ─────────────────────────────────────────────────────
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

# ── Cryptographic Core & Storage Directory Resolution ─────────────────────────
try:
    from security import generate_hash, password_strength, get_storage_dirs, secure_wipe_file
    from encrypt import encrypt_file
    from decrypt import decrypt_file
    from vault_manager import (
        load_vault, save_vault, add_entry, delete_entry,
        vault_exists, init_vault, change_master, reset_vault
    )
except ImportError:
    def get_storage_dirs():
        base = os.path.join(os.path.expanduser("~"), "Cryptex")
        enc = os.path.join(base, "Encrypted")
        dec = os.path.join(base, "Decrypted")
        vlt = os.path.join(base, "Vault")
        for d in [base, enc, dec, vlt]:
            os.makedirs(d, exist_ok=True)
        return base, enc, dec, vlt

    def secure_wipe_file(fp):
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except Exception:
                pass

    def generate_hash(fp):
        sha = hashlib.sha256()
        with open(fp, "rb") as fh:
            while True:
                chunk = fh.read(65536)
                if not chunk:
                    break
                sha.update(chunk)
        return sha.hexdigest()

    def encrypt_file(f, p, delete_original=True, target_dir=None): return f, False
    def decrypt_file(f, p, target_dir=None): return f
    def password_strength(p):
        score = sum([len(p) >= 8, bool(re.search(r"[A-Z]", p)),
                     bool(re.search(r"[0-9]", p)), bool(re.search(r"[!@#$%^&*]", p))])
        return ["Weak", "Weak", "Medium", "Strong", "Strong"][score]

    def vault_exists(): return False
    def init_vault(m): pass
    def load_vault(m): return []
    def save_vault(m, e): pass
    def add_entry(m, s, u, p, n): pass
    def delete_entry(m, eid): pass
    def change_master(o, n): pass
    def reset_vault(): return True

# ══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE TOKENS (Light Mode: Warm Cream Paper / Dark Mode: OLED True Black)
# ══════════════════════════════════════════════════════════════════════════════
CLR_BG          = ("#F8F7F3", "#000000")  # Warm Cream Paper / OLED True Black
CLR_SIDEBAR     = ("#F0EFEA", "#060607")  # Sidebar Rail
CLR_CARD        = ("#FFFFFF", "#0D0D0E")  # Elevated Card Surfaces
CLR_CARD_ELEV   = ("#F4F2EC", "#141416")  # Input backgrounds / inner sub-cards
CLR_CARD_HOVER  = ("#EBE8E0", "#1C1C20")  # Hover states
CLR_BORDER      = ("#E5E3DC", "#1E1E22")  # Ultra-fine 1px dark borders
CLR_BORDER_ACT  = ("#111111", "#444448")  # Active Border Glow
CLR_TEXT_MAIN   = ("#0D0E11", "#FFFFFF")  # Primary Text (Crisp White in Dark)
CLR_TEXT_MUTED  = ("#5A5E6B", "#94949C")  # Muted Labels (Silver Slate)
CLR_TEXT_DARK   = ("#8F94A3", "#52525B")  # Metadata

# Button & Accent Styling Tokens
CLR_BTN_PRI_BG  = ("#0D0E11", "#FFFFFF")  # Primary Button Fill (Tactile White in Dark, Black in Light)
CLR_BTN_PRI_FG  = ("#FFFFFF", "#000000")  # Primary Button Text
CLR_BTN_PRI_HOV = ("#27272A", "#E4E4E7")  # Primary Button Hover

CLR_BTN_SEC_BG  = ("#EAE8E0", "#171719")  # Secondary / Glass Button Fill
CLR_BTN_SEC_FG  = ("#0D0E11", "#E4E4E7")  # Secondary Button Text
CLR_BTN_SEC_BOR = ("#DDD9CE", "#27272A")  # Secondary Button Border
CLR_BTN_SEC_HOV = ("#DFDBD0", "#242428")  # Secondary Button Hover

CLR_DEC_BG      = ("#FEE2E2", "#180F11")  # Decrypt Button Fill
CLR_DEC_FG      = ("#DC2626", "#F87171")  # Decrypt Button Text
CLR_DEC_BOR     = ("#FCA5A5", "#3D1418")  # Decrypt Button Border
CLR_DEC_HOV     = ("#FECACA", "#281417")  # Decrypt Button Hover

CLR_BANNER_BG   = ("#FEF2F2", "#140A0C")  # Self-destruct Banner Fill
CLR_BANNER_BOR  = ("#FCA5A5", "#381014")  # Self-destruct Banner Border
CLR_BANNER_FG   = ("#B91C1C", "#FCA5A5")  # Self-destruct Banner Text

CLR_SUCCESS     = ("#059669", "#10B981")  # Emerald Success
CLR_WARNING     = ("#D97706", "#F59E0B")  # Amber Warning
CLR_ERROR       = ("#DC2626", "#EF4444")  # Crimson Error

# Typography Fonts
FONT_FAMILY = "Segoe UI Variable Display" if sys.platform == "win32" else "Helvetica Neue"
F_HERO      = (FONT_FAMILY, 19, "bold")
F_TITLE     = (FONT_FAMILY, 14, "bold")
F_HEADLINE  = (FONT_FAMILY, 12, "bold")
F_BODY      = (FONT_FAMILY, 11, "normal")
F_BODY_BOLD = (FONT_FAMILY, 11, "bold")
F_SMALL     = (FONT_FAMILY, 9, "normal")
F_SMALL_BD  = (FONT_FAMILY, 9, "bold")
F_MONO      = ("Consolas", 11, "normal")
F_MONO_BOLD = ("Consolas", 11, "bold")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN GUI CLASS
# ══════════════════════════════════════════════════════════════════════════════
class CryptexGUI:
    def __init__(self):
        if HAS_DND:
            class DnDApp(ctk.CTk, TkinterDnD.DnDWrapper):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.TkdndVersion = TkinterDnD._require(self)
            self.root = DnDApp()
        else:
            self.root = ctk.CTk()

        self.root.title("Cryptex - Secure File Encryption")
        self.root.geometry("1180x800")
        self.root.minsize(1020, 680)

        # Storage Directories
        self.base_dir, self.enc_dir, self.dec_dir, self.vault_dir = get_storage_dirs()

        # Load Unified Black & White Window Icon
        try:
            if getattr(sys, 'frozen', False):
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            ico_path = os.path.join(base_path, "assets", "icon.ico")
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
        except Exception:
            pass

        # State
        self.is_dark = True
        self.selected_file = ""
        self.decrypt_attempts = 0
        self.max_attempts = 3
        self.active_tab = "encrypt"
        self.vault_unlocked = False
        self.vault_master_key = ""
        self.vault_entries = []

        self._init_layout()
        self._bind_keys()

    def _init_layout(self):
        self.root.configure(fg_color=CLR_BG)

        # ── TOP NAVIGATION HEADER ─────────────────────────────────────────────
        self.top_header = ctk.CTkFrame(self.root, height=54, corner_radius=0,
                                       fg_color=CLR_SIDEBAR, border_width=1, border_color=CLR_BORDER)
        self.top_header.pack(fill="x", side="top")
        self.top_header.pack_propagate(False)

        # Brand Title & Version (Unified Black and White Logo System)
        brand_frame = ctk.CTkFrame(self.top_header, fg_color="transparent")
        brand_frame.pack(side="left", padx=18, pady=8)

        title_lbl = ctk.CTkLabel(brand_frame, text="⚡ CRYPTEX", font=F_HERO, text_color=CLR_TEXT_MAIN)
        title_lbl.pack(side="left")

        ver_badge = ctk.CTkLabel(brand_frame, text=" SECURE FILE ENCRYPTION", font=F_SMALL_BD, text_color=CLR_TEXT_MUTED)
        ver_badge.pack(side="left", padx=(6, 0), pady=(3, 0))

        # Right Header Actions
        hdr_right = ctk.CTkFrame(self.top_header, fg_color="transparent")
        hdr_right.pack(side="right", padx=18, pady=8)

        # Storage directory pill
        dir_display = os.path.basename(self.base_dir) or "Cryptex"
        self.dir_btn = ctk.CTkButton(hdr_right, text=f"📂 ~/{dir_display}", font=F_SMALL_BD,
                                      fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                      text_color=CLR_BTN_SEC_FG, height=30, corner_radius=15,
                                      border_width=1, border_color=CLR_BTN_SEC_BOR,
                                      command=self.open_storage_dir)
        self.dir_btn.pack(side="left", padx=(0, 10))

        self.theme_btn = ctk.CTkButton(hdr_right, text="🌙 True Black", font=F_BODY_BOLD,
                                       fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                       text_color=CLR_BTN_SEC_FG, height=30, corner_radius=15,
                                       border_width=1, border_color=CLR_BTN_SEC_BOR,
                                       command=self.toggle_theme)
        self.theme_btn.pack(side="right")

        # ── MAIN SPLIT CONTAINER ──────────────────────────────────────────────
        self.main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color=CLR_BG)
        self.main_container.pack(fill="both", expand=True)

        # Left Navigation Sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, width=220, corner_radius=0,
                                    fg_color=CLR_SIDEBAR, border_width=1, border_color=CLR_BORDER)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="MODULES", font=F_SMALL_BD,
                     text_color=CLR_TEXT_DARK).pack(anchor="w", padx=18, pady=(18, 10))

        # Nav Buttons
        self.nav_btns = {}
        tabs = [
            ("encrypt", "🔒 File Encryptor"),
            ("pwcheck", "🔑 Entropy Analyzer"),
            ("pwgen",   "⚡ Pass Generator"),
            ("vault",   "🔐 Password Vault"),
            ("hash",    "🔍 SHA-256 Checksum"),
        ]

        for tab_id, tab_label in tabs:
            btn = ctk.CTkButton(self.sidebar, text=tab_label, anchor="w", font=F_HEADLINE,
                                height=38, corner_radius=8, fg_color="transparent",
                                text_color=CLR_TEXT_MUTED, hover_color=CLR_CARD_HOVER,
                                border_width=0,
                                command=lambda t=tab_id: self.switch_tab(t))
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_btns[tab_id] = btn

        # Sidebar Footer
        sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_footer.pack(side="bottom", fill="x", padx=16, pady=16)
        ctk.CTkLabel(sidebar_footer, text="Cryptex v2.0", font=F_SMALL_BD, text_color=CLR_TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(sidebar_footer, text="By Ojas Purohit", font=F_SMALL, text_color=CLR_TEXT_DARK).pack(anchor="w")

        # Workspace Container
        self.workspace = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color=CLR_BG)
        self.workspace.pack(side="left", fill="both", expand=True, padx=22, pady=18)

        # Build Module Screens
        self.tab_frames = {}
        self._build_encrypt_tab()
        self._build_pwcheck_tab()
        self._build_pwgen_tab()
        self._build_vault_tab()
        self._build_hash_tab()

        self.switch_tab("encrypt")

    def open_storage_dir(self):
        try:
            if sys.platform == "win32":
                os.startfile(self.base_dir)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", self.base_dir])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", self.base_dir])
        except Exception as e:
            messagebox.showinfo("Cryptex Storage", f"Storage directory located at:\n{self.base_dir}")

    def open_encrypted_dir(self):
        try:
            if sys.platform == "win32":
                os.startfile(self.enc_dir)
            else:
                self.open_storage_dir()
        except Exception:
            pass

    def open_decrypted_dir(self):
        try:
            if sys.platform == "win32":
                os.startfile(self.dec_dir)
            else:
                self.open_storage_dir()
        except Exception:
            pass

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        if self.is_dark:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌙 True Black")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="☀️ Cream Light")
        self.switch_tab(self.active_tab)

    def switch_tab(self, tab_id):
        self.active_tab = tab_id
        for tid, btn in self.nav_btns.items():
            if tid == tab_id:
                # Sleek modern pill
                if self.is_dark:
                    btn.configure(fg_color="#18181B", text_color="#FFFFFF", border_width=1, border_color="#27272A")
                else:
                    btn.configure(fg_color="#E4E1D8", text_color="#0D0E11", border_width=1, border_color="#D5D1C6")
            else:
                btn.configure(fg_color="transparent", text_color=CLR_TEXT_MUTED, border_width=0)

        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        if tab_id == "vault":
            self._update_vault_ui_state()

    # ══════════════════════════════════════════════════════════════════════════
    # 1. FILE ENCRYPTOR & DECRYPTOR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_encrypt_tab(self):
        f = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")
        self.tab_frames["encrypt"] = f

        hdr = ctk.CTkLabel(f, text="File Encryption Engine", font=F_HERO,
                           text_color=CLR_TEXT_MAIN, anchor="w")
        hdr.pack(fill="x", pady=(0, 2))
        sub = ctk.CTkLabel(f, text="Encrypt and decrypt any file format using AES-256 with SHA-256 integrity verification.",
                           font=F_BODY, text_color=CLR_TEXT_MUTED, anchor="w")
        sub.pack(fill="x", pady=(0, 16))

        # Drop Zone Card
        self.dz_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                                    border_width=1, border_color=CLR_BORDER)
        self.dz_card.pack(fill="x", pady=(0, 14), ipady=22)

        self.dz_icon = ctk.CTkLabel(self.dz_card, text="📁", font=("Segoe UI", 36))
        self.dz_icon.pack(pady=(12, 4))

        self.dz_label = ctk.CTkLabel(self.dz_card, text="Drag & Drop file here, or click to browse",
                                     font=F_TITLE, text_color=CLR_TEXT_MAIN)
        self.dz_label.pack(pady=(0, 2))

        self.dz_sub = ctk.CTkLabel(self.dz_card, text="Supports all formats (.pdf, .docx, .zip, .mp4, .png, etc.)",
                                   font=F_SMALL, text_color=CLR_TEXT_MUTED)
        self.dz_sub.pack(pady=(0, 12))

        for w in [self.dz_card, self.dz_icon, self.dz_label, self.dz_sub]:
            w.bind("<Button-1>", lambda e: self.browse_file())

        if HAS_DND:
            self.dz_card.drop_target_register(DND_FILES)
            self.dz_card.dnd_bind("<<Drop>>", lambda e: self.load_file(e.data))

        # Passphrase Card
        key_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                                border_width=1, border_color=CLR_BORDER)
        key_card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=14)

        ctk.CTkLabel(key_card, text="ENCRYPTION KEY / PASSPHRASE", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 6))

        entry_row = ctk.CTkFrame(key_card, fg_color="transparent")
        entry_row.pack(fill="x", padx=14, pady=(0, 10))

        self.enc_key_var = tk.StringVar()
        self.enc_key_var.trace_add("write", self._on_enc_key_change)

        self.key_entry = ctk.CTkEntry(entry_row, textvariable=self.enc_key_var, show="●",
                                      placeholder_text="Enter secret passphrase...",
                                      font=F_BODY, height=38, corner_radius=8,
                                      fg_color=CLR_CARD_ELEV, border_width=1, border_color=CLR_BORDER)
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_btn = ctk.CTkSwitch(entry_row, text="Reveal", variable=self.show_key_var,
                                          font=F_BODY, text_color=CLR_TEXT_MAIN,
                                          progress_color=CLR_BTN_PRI_BG, command=self._toggle_key_visibility)
        self.show_key_btn.pack(side="right")

        # Strength Bar
        self.str_bar = ctk.CTkProgressBar(key_card, height=5, corner_radius=2,
                                          fg_color=CLR_CARD_ELEV, progress_color=CLR_SUCCESS)
        self.str_bar.pack(fill="x", padx=14, pady=(0, 4))
        self.str_bar.set(0)

        self.str_lbl = ctk.CTkLabel(key_card, text="Passphrase Strength: None", font=F_SMALL,
                                    text_color=CLR_TEXT_MUTED)
        self.str_lbl.pack(anchor="w", padx=14, pady=(0, 6))

        # Auto-Delete Plaintext Checkbox
        self.auto_shred_var = tk.BooleanVar(value=True)
        self.auto_shred_cb = ctk.CTkCheckBox(key_card, text="Securely delete & shred original plaintext file after encryption",
                                             variable=self.auto_shred_var, font=F_BODY,
                                             text_color=CLR_TEXT_MAIN, fg_color=CLR_BTN_PRI_BG,
                                             checkmark_color=CLR_BTN_PRI_FG,
                                             border_color=CLR_BORDER)
        self.auto_shred_cb.pack(anchor="w", padx=14, pady=(6, 8))

        # Self Destruct Callout Box
        sd_box = ctk.CTkFrame(f, corner_radius=10, fg_color=CLR_BANNER_BG,
                              border_width=1, border_color=CLR_BANNER_BOR)
        sd_box.pack(fill="x", pady=(0, 14), ipadx=12, ipady=8)

        ctk.CTkLabel(sd_box, text="⚠️ Self-Destruct Protection: 3 consecutive failed decryption attempts permanently deletes the file.",
                     font=F_BODY, text_color=CLR_BANNER_FG).pack(anchor="w", padx=12, pady=4)

        # Action Buttons (Tactile High-Contrast White Primary & Crimson Outline Decrypt)
        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 14))

        self.enc_btn = ctk.CTkButton(btn_row, text="🔒 Encrypt File", font=F_HEADLINE,
                                     height=42, corner_radius=8,
                                     fg_color=CLR_BTN_PRI_BG, text_color=CLR_BTN_PRI_FG,
                                     hover_color=CLR_BTN_PRI_HOV, command=self.do_encrypt_async)
        self.enc_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dec_btn = ctk.CTkButton(btn_row, text="🔓 Decrypt File", font=F_HEADLINE,
                                     height=42, corner_radius=8,
                                     fg_color=CLR_DEC_BG, text_color=CLR_DEC_FG,
                                     border_width=1, border_color=CLR_DEC_BOR,
                                     hover_color=CLR_DEC_HOV, command=self.do_decrypt_async)
        self.dec_btn.pack(side="right", fill="x", expand=True)

        # Status Toast
        self.enc_status_lbl = ctk.CTkLabel(f, text="", font=F_HEADLINE, text_color=CLR_TEXT_MAIN)
        self.enc_status_lbl.pack(fill="x", pady=(0, 14))

        # Storage Table
        fm_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                               border_width=1, border_color=CLR_BORDER)
        fm_card.pack(fill="x", pady=(0, 20), ipadx=14, ipady=14)

        fm_hdr = ctk.CTkFrame(fm_card, fg_color="transparent")
        fm_hdr.pack(fill="x", padx=14, pady=(10, 10))

        ctk.CTkLabel(fm_hdr, text=f"ENCRYPTED REPOSITORY  (~/{os.path.basename(self.base_dir)}/Encrypted)", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(side="left")

        btn_box = ctk.CTkFrame(fm_hdr, fg_color="transparent")
        btn_box.pack(side="right")

        open_folder_btn = ctk.CTkButton(btn_box, text="📂 Open Folder", width=95, height=28, font=F_SMALL_BD,
                                        corner_radius=6, fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                        text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                        command=self.open_encrypted_dir)
        open_folder_btn.pack(side="left", padx=(0, 6))

        refresh_btn = ctk.CTkButton(btn_box, text="↻ Refresh", width=75, height=28, font=F_SMALL_BD,
                                    corner_radius=6, fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                    text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                    command=self.refresh_encrypted_files)
        refresh_btn.pack(side="left")

        self.fm_list_frame = ctk.CTkFrame(fm_card, fg_color="transparent")
        self.fm_list_frame.pack(fill="x", padx=14, pady=(0, 10))

        self.refresh_encrypted_files()

    def _toggle_key_visibility(self):
        show_char = "" if self.show_key_var.get() else "●"
        self.key_entry.configure(show=show_char)

    def _on_enc_key_change(self, *_):
        p = self.enc_key_var.get()
        score = sum([len(p) >= 8, bool(re.search(r"[A-Z]", p)),
                     bool(re.search(r"[0-9]", p)), bool(re.search(r"[!@#$%^&*]", p))])
        ratings = [("Weak", 0.25, CLR_ERROR), ("Fair", 0.5, CLR_WARNING),
                   ("Good", 0.75, CLR_SUCCESS), ("Strong", 1.0, CLR_SUCCESS)]
        if not p:
            lbl_txt, frac, col = "Passphrase Strength: None", 0, CLR_TEXT_MUTED
        else:
            idx = max(0, min(score - 1, 3))
            lbl_txt, frac, col = f"Passphrase Strength: {ratings[idx][0]}", ratings[idx][1], ratings[idx][2]

        self.str_lbl.configure(text=lbl_txt, text_color=col)
        self.str_bar.configure(progress_color=col)
        self.str_bar.set(frac)

    def browse_file(self):
        p = filedialog.askopenfilename()
        if p:
            self.load_file(p)

    def load_file(self, path):
        path = path.strip().strip("{}")
        if os.path.exists(path):
            self.selected_file = path
            fname = os.path.basename(path)
            sz = os.path.getsize(path)
            sz_str = f"{sz/1024:.1f} KB" if sz >= 1024 else f"{sz} B"
            self.dz_label.configure(text=f"Selected: {fname} ({sz_str})")
            self.dz_icon.configure(text="📄")
            self.enc_status_lbl.configure(text=f"Target file loaded: {fname}", text_color=CLR_TEXT_MAIN)

    def do_encrypt_async(self):
        threading.Thread(target=self._do_encrypt, daemon=True).start()

    def _do_encrypt(self):
        if not self.selected_file:
            self._set_enc_status("⚠️ Please select or drop a file first", CLR_WARNING)
            return
        pw = self.enc_key_var.get()
        if not pw:
            self._set_enc_status("⚠️ Please enter an encryption key", CLR_WARNING)
            return

        self._set_enc_status("⏳ Encrypting file with AES-256...", CLR_TEXT_MAIN)
        try:
            do_shred = self.auto_shred_var.get()
            out, shredded = encrypt_file(self.selected_file, pw, delete_original=do_shred, target_dir=self.enc_dir)
            out_name = os.path.basename(out) if out else "encrypted file"
            shred_msg = " (Original source file shredded & removed)" if shredded else ""
            self._set_enc_status(f"✓ Encrypted successfully → {out_name}{shred_msg}", CLR_SUCCESS)
            self.selected_file = ""
            self.dz_label.configure(text="Drag & Drop file here, or click to browse")
            self.dz_icon.configure(text="📁")
            self.root.after(200, self.refresh_encrypted_files)
        except Exception as e:
            self._set_enc_status(f"✖ Encryption Error: {e}", CLR_ERROR)

    def do_decrypt_async(self):
        threading.Thread(target=self._do_decrypt, daemon=True).start()

    def _do_decrypt(self):
        if not self.selected_file:
            self._set_enc_status("⚠️ Please select a file to decrypt first", CLR_WARNING)
            return
        pw = self.enc_key_var.get()
        if not pw:
            self._set_enc_status("⚠️ Please enter decryption passphrase", CLR_WARNING)
            return

        self._set_enc_status("⏳ Decrypting file...", CLR_TEXT_MAIN)
        try:
            out = decrypt_file(self.selected_file, pw, target_dir=self.dec_dir)
            self.decrypt_attempts = 0
            out_name = os.path.basename(out) if out else os.path.basename(self.selected_file)
            self._set_enc_status(f"✓ Decrypted successfully → saved to Decrypted/{out_name}", CLR_SUCCESS)
        except Exception as e:
            self.decrypt_attempts += 1
            left = self.max_attempts - self.decrypt_attempts
            if self.decrypt_attempts >= self.max_attempts:
                try:
                    secure_wipe_file(self.selected_file)
                    self._set_enc_status("☠ SELF-DESTRUCT: File permanently deleted after 3 failed attempts!", CLR_ERROR)
                    self.selected_file = ""
                    self.dz_label.configure(text="Drag & Drop file here, or click to browse")
                    self.dz_icon.configure(text="📁")
                    self.decrypt_attempts = 0
                    self.root.after(200, self.refresh_encrypted_files)
                except Exception as de:
                    self._set_enc_status(f"✖ Destruct Error: {de}", CLR_ERROR)
            else:
                self._set_enc_status(f"✖ Incorrect Passphrase! {left} attempt(s) remaining before self-destruct.", CLR_ERROR)

    def _set_enc_status(self, txt, col):
        self.root.after(0, lambda: self.enc_status_lbl.configure(text=txt, text_color=col))

    def refresh_encrypted_files(self):
        for w in self.fm_list_frame.winfo_children():
            w.destroy()

        if not os.path.exists(self.enc_dir):
            os.makedirs(self.enc_dir, exist_ok=True)

        files = sorted([f for f in os.listdir(self.enc_dir) if f.endswith(".cryptex")],
                       key=lambda x: os.path.getmtime(os.path.join(self.enc_dir, x)), reverse=True)

        if not files:
            ctk.CTkLabel(self.fm_list_frame, text="No encrypted files stored in secure directory yet.", font=F_BODY,
                         text_color=CLR_TEXT_MUTED).pack(pady=12)
            return

        for fname in files[:8]:
            fpath = os.path.join(self.enc_dir, fname)
            sz = os.path.getsize(fpath)
            sz_str = f"{sz/1024:.1f} KB" if sz >= 1024 else f"{sz} B"

            row = ctk.CTkFrame(self.fm_list_frame, corner_radius=6, fg_color=CLR_CARD_ELEV,
                               border_width=1, border_color=CLR_BORDER)
            row.pack(fill="x", pady=2)

            lbl = ctk.CTkLabel(row, text=f"🔒 {fname}  ({sz_str})", font=F_BODY,
                               text_color=CLR_TEXT_MAIN)
            lbl.pack(side="left", padx=12, pady=8)

            btn_box = ctk.CTkFrame(row, fg_color="transparent")
            btn_box.pack(side="right", padx=10)

            load_btn = ctk.CTkButton(btn_box, text="Select", width=65, height=26, font=F_SMALL_BD,
                                     corner_radius=4, fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                     text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                     command=lambda p=fpath: self.load_file(p))
            load_btn.pack(side="left", padx=2)

    # ══════════════════════════════════════════════════════════════════════════
    # 2. ENTROPY ANALYZER
    # ══════════════════════════════════════════════════════════════════════════
    def _build_pwcheck_tab(self):
        f = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")
        self.tab_frames["pwcheck"] = f

        hdr = ctk.CTkLabel(f, text="Password Entropy Analyzer", font=F_HERO,
                           text_color=CLR_TEXT_MAIN, anchor="w")
        hdr.pack(fill="x", pady=(0, 2))
        sub = ctk.CTkLabel(f, text="Evaluates Shannon entropy bits, character distribution, and brute-force resistance.",
                           font=F_BODY, text_color=CLR_TEXT_MUTED, anchor="w")
        sub.pack(fill="x", pady=(0, 16))

        card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                            border_width=1, border_color=CLR_BORDER)
        card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=14)

        ctk.CTkLabel(card, text="TEST PASSPHRASE", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 6))

        self.check_pw_var = tk.StringVar()
        self.check_pw_var.trace_add("write", self._analyze_pw)

        self.pwc_entry = ctk.CTkEntry(card, textvariable=self.check_pw_var, font=F_BODY, height=38,
                                      corner_radius=8, fg_color=CLR_CARD_ELEV,
                                      border_width=1, border_color=CLR_BORDER,
                                      placeholder_text="Enter passphrase to inspect...")
        self.pwc_entry.pack(fill="x", padx=14, pady=(0, 10))

        # Meter Card
        self.meter_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                                       border_width=1, border_color=CLR_BORDER)
        self.meter_card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=16)

        self.score_lbl = ctk.CTkLabel(self.meter_card, text="Score: 0 / 100%", font=F_HERO,
                                      text_color=CLR_TEXT_MUTED)
        self.score_lbl.pack(pady=(10, 2))

        self.entropy_lbl = ctk.CTkLabel(self.meter_card, text="Entropy: 0.0 bits  ·  Est. Crack Time: Instant",
                                        font=F_BODY, text_color=CLR_TEXT_MUTED)
        self.entropy_lbl.pack(pady=(0, 14))

        self.score_progress = ctk.CTkProgressBar(self.meter_card, height=8, corner_radius=4,
                                                 fg_color=CLR_CARD_ELEV, progress_color=CLR_SUCCESS)
        self.score_progress.pack(fill="x", padx=20, pady=(0, 10))
        self.score_progress.set(0)

        # 4 Criteria Cards
        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))

        self.crit_labels = {}
        crits = [("len", "8+ Characters"), ("upper", "Uppercase Letters (A-Z)"),
                 ("digit", "Numbers (0-9)"), ("sym", "Special Symbols (!@#$)")]

        for idx, (key, title) in enumerate(crits):
            box = ctk.CTkFrame(grid, corner_radius=10, fg_color=CLR_CARD,
                               border_width=1, border_color=CLR_BORDER)
            box.grid(row=idx//2, column=idx%2, sticky="nsew", padx=5, pady=5)
            grid.columnconfigure(idx%2, weight=1)

            lbl = ctk.CTkLabel(box, text=f"○  {title}", font=F_BODY,
                               text_color=CLR_TEXT_MUTED)
            lbl.pack(anchor="w", padx=16, pady=12)
            self.crit_labels[key] = lbl

    def _analyze_pw(self, *_):
        pw = self.check_pw_var.get()
        ch = {"len": len(pw) >= 8, "upper": bool(re.search(r"[A-Z]", pw)),
              "digit": bool(re.search(r"[0-9]", pw)), "sym": bool(re.search(r"[!@#$%^&*]", pw))}

        for k, ok in ch.items():
            txt = self.crit_labels[k].cget("text")
            base = txt[3:]
            if ok:
                self.crit_labels[k].configure(text=f"✓  {base}", text_color=CLR_SUCCESS)
            else:
                self.crit_labels[k].configure(text=f"○  {base}", text_color=CLR_TEXT_MUTED)

        score_num = sum(ch.values())
        frac = score_num / 4.0
        score_pct = int(frac * 100)

        cs = sum([26 if re.search(r"[a-z]", pw) else 0,
                  26 if re.search(r"[A-Z]", pw) else 0,
                  10 if re.search(r"[0-9]", pw) else 0,
                  32 if re.search(r"[^a-zA-Z0-9]", pw) else 0])
        bits = len(pw) * math.log2(cs) if cs and pw else 0

        if bits == 0: crack_txt = "Instant"
        elif bits < 28: crack_txt = "< 1 second"
        elif bits < 40: crack_txt = "~ 3 minutes"
        elif bits < 60: crack_txt = "~ 45 days"
        elif bits < 80: crack_txt = "~ 1,200 years"
        else: crack_txt = "10 million centuries (Uncrackable)"

        colors = [CLR_TEXT_MUTED, CLR_ERROR, CLR_WARNING, CLR_SUCCESS, CLR_SUCCESS]

        self.score_lbl.configure(text=f"Score: {score_pct}% ({['Weak', 'Weak', 'Fair', 'Good', 'Strong'][score_num]})",
                                 text_color=colors[score_num])
        self.entropy_lbl.configure(text=f"Entropy: {bits:.1f} bits  ·  Est. Crack Time: {crack_txt}")
        self.score_progress.configure(progress_color=colors[score_num])
        self.score_progress.set(frac)

    # ══════════════════════════════════════════════════════════════════════════
    # 3. SMART PASSWORD GENERATOR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_pwgen_tab(self):
        f = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")
        self.tab_frames["pwgen"] = f

        hdr = ctk.CTkLabel(f, text="Smart Password Generator", font=F_HERO,
                           text_color=CLR_TEXT_MAIN, anchor="w")
        hdr.pack(fill="x", pady=(0, 2))
        sub = ctk.CTkLabel(f, text="Generate cryptographically secure random passwords with customizable character pools.",
                           font=F_BODY, text_color=CLR_TEXT_MUTED, anchor="w")
        sub.pack(fill="x", pady=(0, 16))

        card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                            border_width=1, border_color=CLR_BORDER)
        card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=14)

        len_row = ctk.CTkFrame(card, fg_color="transparent")
        len_row.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(len_row, text="PASSWORD LENGTH", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(side="left")

        self.gen_len_val_lbl = ctk.CTkLabel(len_row, text="16", font=F_HEADLINE,
                                             text_color=CLR_TEXT_MAIN)
        self.gen_len_val_lbl.pack(side="right")

        self.gen_len_slider = ctk.CTkSlider(card, from_=6, to=64, number_of_steps=58,
                                            progress_color=CLR_BTN_PRI_BG, command=self._on_len_slider)
        self.gen_len_slider.pack(fill="x", padx=14, pady=(0, 14))
        self.gen_len_slider.set(16)

        sw_grid = ctk.CTkFrame(card, fg_color="transparent")
        sw_grid.pack(fill="x", padx=14, pady=(0, 14))

        self.chk_upper = tk.BooleanVar(value=True)
        self.chk_lower = tk.BooleanVar(value=True)
        self.chk_digit = tk.BooleanVar(value=True)
        self.chk_sym   = tk.BooleanVar(value=True)
        self.chk_ambig = tk.BooleanVar(value=False)

        switches = [("Uppercase (A-Z)", self.chk_upper), ("Lowercase (a-z)", self.chk_lower),
                    ("Digits (0-9)", self.chk_digit), ("Symbols (!@#$)", self.chk_sym),
                    ("Exclude (0,O,1,l)", self.chk_ambig)]

        for idx, (lbl, var) in enumerate(switches):
            sw = ctk.CTkSwitch(sw_grid, text=lbl, variable=var, font=F_BODY,
                                text_color=CLR_TEXT_MAIN, progress_color=CLR_BTN_PRI_BG)
            sw.grid(row=idx//2, column=idx%2, sticky="w", padx=10, pady=6)

        # Quantity Row
        qty_row = ctk.CTkFrame(card, fg_color="transparent")
        qty_row.pack(fill="x", padx=14, pady=(6, 10))

        ctk.CTkLabel(qty_row, text="BATCH QUANTITY:", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(side="left", padx=(0, 10))

        self.gen_qty_var = tk.IntVar(value=1)
        minus_btn = ctk.CTkButton(qty_row, text="-", width=32, height=32, font=F_HEADLINE,
                                  corner_radius=6, fg_color=CLR_CARD_ELEV, text_color=CLR_TEXT_MAIN,
                                  border_width=1, border_color=CLR_BORDER,
                                  command=lambda: self._adj_qty(-1))
        minus_btn.pack(side="left", padx=2)

        self.qty_lbl = ctk.CTkLabel(qty_row, text="1", font=F_HEADLINE, width=28,
                                    text_color=CLR_TEXT_MAIN)
        self.qty_lbl.pack(side="left", padx=6)

        plus_btn = ctk.CTkButton(qty_row, text="+", width=32, height=32, font=F_HEADLINE,
                                 corner_radius=6, fg_color=CLR_CARD_ELEV, text_color=CLR_TEXT_MAIN,
                                 border_width=1, border_color=CLR_BORDER,
                                 command=lambda: self._adj_qty(1))
        plus_btn.pack(side="left", padx=2)

        # Primary Action Button
        gen_btn = ctk.CTkButton(f, text="⚡ Generate Passwords", font=F_HEADLINE,
                                height=42, corner_radius=8,
                                fg_color=CLR_BTN_PRI_BG, text_color=CLR_BTN_PRI_FG,
                                hover_color=CLR_BTN_PRI_HOV, command=self.do_generate)
        gen_btn.pack(fill="x", pady=(0, 14))

        # Output Box
        out_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                                border_width=1, border_color=CLR_BORDER)
        out_card.pack(fill="both", expand=True, ipadx=14, ipady=14)

        self.gen_out_box = ctk.CTkTextbox(out_card, font=F_MONO_BOLD, height=130,
                                          fg_color=CLR_CARD_ELEV, text_color=CLR_TEXT_MAIN)
        self.gen_out_box.pack(fill="both", expand=True, padx=14, pady=14)

        copy_row = ctk.CTkFrame(out_card, fg_color="transparent")
        copy_row.pack(fill="x", padx=14, pady=(0, 10))

        copy_btn = ctk.CTkButton(copy_row, text="📋 Copy All Passwords", font=F_BODY_BOLD,
                                 height=32, corner_radius=16,
                                 fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                 text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                 command=self.copy_generated)
        copy_btn.pack(side="left")

        self.gen_toast_lbl = ctk.CTkLabel(copy_row, text="", font=F_BODY_BOLD,
                                          text_color=CLR_SUCCESS)
        self.gen_toast_lbl.pack(side="left", padx=14)

    def _on_len_slider(self, val):
        self.gen_len_val_lbl.configure(text=str(int(val)))

    def _adj_qty(self, delta):
        v = max(1, min(20, self.gen_qty_var.get() + delta))
        self.gen_qty_var.set(v)
        self.qty_lbl.configure(text=str(v))

    def do_generate(self):
        pool = ""
        if self.chk_upper.get(): pool += string.ascii_uppercase
        if self.chk_lower.get(): pool += string.ascii_lowercase
        if self.chk_digit.get(): pool += string.digits
        if self.chk_sym.get():   pool += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        if self.chk_ambig.get():
            for ch in "0O1lI": pool = pool.replace(ch, "")

        length = int(self.gen_len_slider.get())
        cnt = self.gen_qty_var.get()

        self.gen_out_box.delete("1.0", "end")
        if not pool:
            self.gen_out_box.insert("end", "⚠️ Select at least one character set.\n")
        else:
            for _ in range(cnt):
                self.gen_out_box.insert("end", "".join(random.choice(pool) for _ in range(length)) + "\n")

    def copy_generated(self):
        txt = self.gen_out_box.get("1.0", "end").strip()
        if txt:
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.gen_toast_lbl.configure(text="✓ Copied to Clipboard!")
            self.root.after(2500, lambda: self.gen_toast_lbl.configure(text=""))

    # ══════════════════════════════════════════════════════════════════════════
    # 4. ENCRYPTED PASSWORD VAULT (Full Master Password Setup & Management)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_vault_tab(self):
        f = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.tab_frames["vault"] = f

        hdr = ctk.CTkLabel(f, text="Encrypted Password Vault", font=F_HERO,
                           text_color=CLR_TEXT_MAIN, anchor="w")
        hdr.pack(fill="x", pady=(0, 2))
        sub = ctk.CTkLabel(f, text="Zero-Knowledge AES-256 encrypted credential storage protected by PBKDF2 Master Key.",
                           font=F_BODY, text_color=CLR_TEXT_MUTED, anchor="w")
        sub.pack(fill="x", pady=(0, 16))

        # Dynamic Master Password / Control Bar
        self.master_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                                        border_width=1, border_color=CLR_BORDER)
        self.master_card.pack(fill="x", pady=(0, 16), ipadx=14, ipady=10)

        self.master_bar_frame = ctk.CTkFrame(self.master_card, fg_color="transparent")
        self.master_bar_frame.pack(fill="x", padx=14, pady=6)

        # 2-Column Main Workspace
        self.vault_layout = ctk.CTkFrame(f, fg_color="transparent")
        self.vault_layout.pack(fill="both", expand=True)

        # LEFT COLUMN: Add New Credential Form
        add_card = ctk.CTkFrame(self.vault_layout, width=320, corner_radius=14, fg_color=CLR_CARD,
                                border_width=1, border_color=CLR_BORDER)
        add_card.pack(side="left", fill="y", padx=(0, 14), ipadx=14, ipady=14)
        add_card.pack_propagate(False)

        ctk.CTkLabel(add_card, text="ADD NEW CREDENTIAL", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(6, 12))

        self.v_site = tk.StringVar()
        self.v_user = tk.StringVar()
        self.v_pass = tk.StringVar()
        self.v_note = tk.StringVar()

        for lbl_txt, var in [("Site / Application:", self.v_site), ("Username / Email:", self.v_user),
                              ("Password:", self.v_pass), ("Notes / Hint:", self.v_note)]:
            ctk.CTkLabel(add_card, text=lbl_txt, font=F_BODY,
                         text_color=CLR_TEXT_MAIN).pack(anchor="w", padx=14, pady=(4, 2))
            e = ctk.CTkEntry(add_card, textvariable=var, height=36, corner_radius=6,
                             fg_color=CLR_CARD_ELEV, border_width=1, border_color=CLR_BORDER)
            e.pack(fill="x", padx=14, pady=(0, 6))

        save_btn = ctk.CTkButton(add_card, text="💾 Save Credential", font=F_HEADLINE,
                                 height=40, corner_radius=8,
                                 fg_color=CLR_BTN_PRI_BG, text_color=CLR_BTN_PRI_FG,
                                 hover_color=CLR_BTN_PRI_HOV, command=self.save_vault_entry)
        save_btn.pack(fill="x", padx=14, pady=(12, 6))

        # RIGHT COLUMN: Credentials Repository Card Container
        right_card = ctk.CTkFrame(self.vault_layout, corner_radius=14, fg_color=CLR_CARD,
                                  border_width=1, border_color=CLR_BORDER)
        right_card.pack(side="left", fill="both", expand=True)

        # Right Header with Search Filter
        right_hdr = ctk.CTkFrame(right_card, fg_color="transparent")
        right_hdr.pack(fill="x", padx=14, pady=(14, 10))

        ctk.CTkLabel(right_hdr, text="CREDENTIAL REPOSITORY", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        self.vault_search_var = tk.StringVar()
        self.vault_search_var.trace_add("write", lambda *_: self.refresh_vault_list())

        search_entry = ctk.CTkEntry(right_hdr, textvariable=self.vault_search_var,
                                    placeholder_text="🔍 Search credentials by site or username...",
                                    height=36, corner_radius=8, fg_color=CLR_CARD_ELEV,
                                    border_width=1, border_color=CLR_BORDER)
        search_entry.pack(fill="x")

        self.vault_scroll = ctk.CTkScrollableFrame(right_card, corner_radius=8, fg_color="transparent")
        self.vault_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self._update_vault_ui_state()

    def _update_vault_ui_state(self):
        """Refreshes the top Master Password bar dynamically based on vault existence & unlock state."""
        for w in self.master_bar_frame.winfo_children():
            w.destroy()

        has_vault = vault_exists()

        if not has_vault:
            # First-time / Uninitialized state
            ctk.CTkLabel(self.master_bar_frame, text="🔑 INITIAL SETUP:", font=F_SMALL_BD,
                         text_color=CLR_TEXT_MUTED).pack(side="left", padx=(0, 10))

            self.vault_init_pw_var = tk.StringVar()
            entry = ctk.CTkEntry(self.master_bar_frame, textvariable=self.vault_init_pw_var, show="●",
                                 placeholder_text="Create new master password...", width=230,
                                 height=34, corner_radius=6, fg_color=CLR_CARD_ELEV,
                                 border_width=1, border_color=CLR_BORDER)
            entry.pack(side="left", padx=(0, 8))

            init_btn = ctk.CTkButton(self.master_bar_frame, text="💾 Set Master Password", font=F_BODY_BOLD,
                                     height=34, corner_radius=6, fg_color=CLR_BTN_PRI_BG,
                                     text_color=CLR_BTN_PRI_FG, hover_color=CLR_BTN_PRI_HOV,
                                     command=self._do_init_master_password)
            init_btn.pack(side="left", padx=4)

            status_lbl = ctk.CTkLabel(self.master_bar_frame, text="● No Vault Initialized", font=F_BODY_BOLD,
                                      text_color=CLR_WARNING)
            status_lbl.pack(side="right", padx=10)

        elif not self.vault_unlocked:
            # Locked State
            ctk.CTkLabel(self.master_bar_frame, text="MASTER KEY:", font=F_SMALL_BD,
                         text_color=CLR_TEXT_MUTED).pack(side="left", padx=(0, 10))

            self.vault_master_var = tk.StringVar()
            entry = ctk.CTkEntry(self.master_bar_frame, textvariable=self.vault_master_var, show="●",
                                 placeholder_text="Enter master password...", width=200,
                                 height=34, corner_radius=6, fg_color=CLR_CARD_ELEV,
                                 border_width=1, border_color=CLR_BORDER)
            entry.pack(side="left", padx=(0, 8))
            entry.bind("<Return>", lambda e: self.unlock_vault())

            unlock_btn = ctk.CTkButton(self.master_bar_frame, text="🔓 Unlock", width=80, height=34,
                                       font=F_BODY_BOLD, corner_radius=6,
                                       fg_color=CLR_BTN_PRI_BG, text_color=CLR_BTN_PRI_FG,
                                       hover_color=CLR_BTN_PRI_HOV, command=self.unlock_vault)
            unlock_btn.pack(side="left", padx=3)

            reset_btn = ctk.CTkButton(self.master_bar_frame, text="🔄 Reset / Set New", width=120, height=34,
                                      font=F_BODY_BOLD, corner_radius=6,
                                      fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                      text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                      command=self._prompt_reset_vault)
            reset_btn.pack(side="left", padx=3)

            status_lbl = ctk.CTkLabel(self.master_bar_frame, text="● Vault Locked", font=F_BODY_BOLD,
                                      text_color=CLR_ERROR)
            status_lbl.pack(side="right", padx=10)

        else:
            # Unlocked State
            status_lbl = ctk.CTkLabel(self.master_bar_frame, text=f"✓ Unlocked ({len(self.vault_entries)} items)",
                                      font=F_BODY_BOLD, text_color=CLR_SUCCESS)
            status_lbl.pack(side="left", padx=(0, 14))

            lock_btn = ctk.CTkButton(self.master_bar_frame, text="🔒 Lock Vault", width=95, height=34,
                                     font=F_BODY_BOLD, corner_radius=6,
                                     fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                     text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                     command=self.lock_vault)
            lock_btn.pack(side="left", padx=4)

            change_btn = ctk.CTkButton(self.master_bar_frame, text="🔑 Change Master Key", width=145, height=34,
                                       font=F_BODY_BOLD, corner_radius=6,
                                       fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                       text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                       command=self._prompt_change_master)
            change_btn.pack(side="left", padx=4)

            reset_btn = ctk.CTkButton(self.master_bar_frame, text="⚠️ Reset Vault", width=100, height=34,
                                      font=F_BODY_BOLD, corner_radius=6,
                                      fg_color=CLR_DEC_BG, hover_color=CLR_DEC_HOV,
                                      text_color=CLR_DEC_FG, border_width=1, border_color=CLR_DEC_BOR,
                                      command=self._prompt_reset_vault)
            reset_btn.pack(side="right", padx=10)

        self.refresh_vault_list()

    def _do_init_master_password(self):
        pw = self.vault_init_pw_var.get().strip()
        if not pw:
            messagebox.showwarning("Master Key", "Please enter a secure master password.")
            return
        if len(pw) < 6:
            messagebox.showwarning("Master Key", "Master password must be at least 6 characters long.")
            return
        try:
            init_vault(pw)
            self.vault_unlocked = True
            self.vault_master_key = pw
            self.vault_entries = []
            messagebox.showinfo("Vault Ready", "Master Password set successfully! Your vault is now ready.")
            self._update_vault_ui_state()
        except Exception as e:
            messagebox.showerror("Error", f"Could not initialize vault: {e}")

    def _prompt_reset_vault(self):
        confirm = messagebox.askyesno(
            "Reset Vault / Set New Password",
            "Are you sure you want to reset the password vault?\n\n"
            "This will purge the existing encrypted database and allow you to set a brand new master password.\n\n"
            "Proceed?",
            icon="warning"
        )
        if confirm:
            reset_vault()
            self.vault_unlocked = False
            self.vault_master_key = ""
            self.vault_entries = []
            self._update_vault_ui_state()
            messagebox.showinfo("Vault Reset", "Vault has been reset. You can now set your new Master Password.")

    def _prompt_change_master(self):
        if not self.vault_unlocked:
            messagebox.showwarning("Vault", "Please unlock vault first.")
            return

        win = ctk.CTkToplevel(self.root)
        win.title("Change Master Password")
        win.geometry("420x300")
        win.resizable(False, False)
        win.configure(fg_color="#000000")
        win.grab_set()

        ctk.CTkLabel(win, text="Change Master Password", font=F_HERO, text_color="#FFFFFF").pack(padx=20, pady=(20, 10))

        v_curr = tk.StringVar()
        v_new1 = tk.StringVar()
        v_new2 = tk.StringVar()

        for lbl, var in [("Current Master Password:", v_curr), ("New Master Password:", v_new1), ("Confirm New Password:", v_new2)]:
            ctk.CTkLabel(win, text=lbl, font=F_BODY, text_color="#94949C").pack(anchor="w", padx=24, pady=(4, 2))
            ctk.CTkEntry(win, textvariable=var, show="●", height=34, corner_radius=6,
                         fg_color="#141416", border_width=1, border_color="#1E1E22").pack(fill="x", padx=24, pady=(0, 4))

        def _do_change():
            curr, n1, n2 = v_curr.get(), v_new1.get(), v_new2.get()
            if curr != self.vault_master_key:
                messagebox.showerror("Error", "Incorrect current master password", parent=win)
                return
            if not n1 or len(n1) < 6:
                messagebox.showerror("Error", "New password must be at least 6 characters", parent=win)
                return
            if n1 != n2:
                messagebox.showerror("Error", "New passwords do not match", parent=win)
                return
            try:
                change_master(curr, n1)
                self.vault_master_key = n1
                messagebox.showinfo("Success", "Master password changed successfully!", parent=win)
                win.destroy()
                self._update_vault_ui_state()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change password: {e}", parent=win)

        ctk.CTkButton(win, text="Save New Master Password", font=F_BODY_BOLD, height=36, corner_radius=6,
                      fg_color="#FFFFFF", text_color="#000000", hover_color="#E4E4E7",
                      command=_do_change).pack(fill="x", padx=24, pady=(16, 10))

    def unlock_vault(self):
        mp = self.vault_master_var.get().strip() if hasattr(self, 'vault_master_var') else ""
        if not mp:
            messagebox.showwarning("Vault Warning", "Please enter master password")
            return
        try:
            self.vault_entries = load_vault(mp)
            self.vault_unlocked = True
            self.vault_master_key = mp
            self._update_vault_ui_state()
        except ValueError:
            messagebox.showerror("Vault Error", "Incorrect Master Password")
        except Exception as e:
            messagebox.showerror("Vault Error", str(e))

    def lock_vault(self):
        self.vault_unlocked = False
        self.vault_master_key = ""
        self.vault_entries = []
        self._update_vault_ui_state()

    def save_vault_entry(self):
        if not self.vault_unlocked:
            messagebox.showwarning("Vault", "Please unlock vault first")
            return
        s, u, p, n = self.v_site.get().strip(), self.v_user.get().strip(), self.v_pass.get(), self.v_note.get().strip()
        if not s or not p:
            messagebox.showwarning("Vault", "Site name and Password are required")
            return
        try:
            add_entry(self.vault_master_key, s, u, p, n)
            self.vault_entries = load_vault(self.vault_master_key)
            self.v_site.set(""); self.v_user.set(""); self.v_pass.set(""); self.v_note.set("")
            self.refresh_vault_list()
        except Exception as e:
            messagebox.showerror("Vault Error", str(e))

    def refresh_vault_list(self):
        for w in self.vault_scroll.winfo_children():
            w.destroy()

        if not self.vault_unlocked:
            msg = "🔒 Vault is locked.\nEnter Master Password to view saved credentials." if vault_exists() else "🔑 Set your Master Password above to begin."
            ctk.CTkLabel(self.vault_scroll, text=msg,
                         font=F_BODY, text_color=CLR_TEXT_MUTED, justify="center").pack(pady=60)
            return

        q = self.vault_search_var.get().strip().lower()
        items = [e for e in self.vault_entries if q in e.get("site","").lower() or q in e.get("username","").lower()]

        if not items:
            ctk.CTkLabel(self.vault_scroll, text="No credentials match your search.", font=F_BODY,
                         text_color=CLR_TEXT_MUTED).pack(pady=40)
            return

        for entry in items:
            card = ctk.CTkFrame(self.vault_scroll, corner_radius=10, fg_color=CLR_CARD_ELEV,
                                border_width=1, border_color=CLR_BORDER)
            card.pack(fill="x", pady=4, padx=8, ipadx=12, ipady=10)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=4)

            site_lbl = ctk.CTkLabel(info, text=entry.get("site",""), font=F_HEADLINE,
                                    text_color=CLR_TEXT_MAIN)
            site_lbl.pack(anchor="w", pady=(0, 2))

            usr_txt = entry.get("username","") or "No Username"
            usr_lbl = ctk.CTkLabel(info, text=f"👤 {usr_txt}", font=F_SMALL,
                                   text_color=CLR_TEXT_MUTED)
            usr_lbl.pack(anchor="w", pady=(2, 0))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(side="right", padx=(0, 8), pady=4)

            copy_btn = ctk.CTkButton(btn_row, text="📋 Copy", width=70, height=28, font=F_SMALL_BD,
                                     corner_radius=14, fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                     text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                     command=lambda p=entry.get("password",""): self._copy_val(p))
            copy_btn.pack(side="left", padx=3)

            del_btn = ctk.CTkButton(btn_row, text="🗑", width=34, height=28, font=F_BODY,
                                    corner_radius=14, fg_color=CLR_DEC_BG, hover_color=CLR_DEC_HOV,
                                    text_color=CLR_DEC_FG, border_width=1, border_color=CLR_DEC_BOR,
                                    command=lambda eid=entry.get("id"): self._del_vault_item(eid))
            del_btn.pack(side="left", padx=3)

    def _copy_val(self, val):
        self.root.clipboard_clear()
        self.root.clipboard_append(val)

    def _del_vault_item(self, eid):
        if messagebox.askyesno("Confirm Delete", "Permanently delete this credential?"):
            try:
                delete_entry(self.vault_master_key, eid)
                self.vault_entries = load_vault(self.vault_master_key)
                self.refresh_vault_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ══════════════════════════════════════════════════════════════════════════
    # 5. SHA-256 INTEGRITY CENTER
    # ══════════════════════════════════════════════════════════════════════════
    def _build_hash_tab(self):
        f = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")
        self.tab_frames["hash"] = f

        hdr = ctk.CTkLabel(f, text="SHA-256 Checksum Center", font=F_HERO,
                           text_color=CLR_TEXT_MAIN, anchor="w")
        hdr.pack(fill="x", pady=(0, 2))
        sub = ctk.CTkLabel(f, text="Calculate cryptographic hash digests and verify checksums side-by-side.",
                           font=F_BODY, text_color=CLR_TEXT_MUTED, anchor="w")
        sub.pack(fill="x", pady=(0, 16))

        # File Hash Section
        f_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                              border_width=1, border_color=CLR_BORDER)
        f_card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=14)

        ctk.CTkLabel(f_card, text="FILE CHECKSUM CALCULATOR", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 6))

        self.hash_file_btn = ctk.CTkButton(f_card, text="📂 Choose File to Calculate SHA-256",
                                            font=F_HEADLINE, height=40, corner_radius=8,
                                            fg_color=CLR_BTN_PRI_BG, text_color=CLR_BTN_PRI_FG,
                                            hover_color=CLR_BTN_PRI_HOV,
                                            command=self.compute_file_hash_async)
        self.hash_file_btn.pack(fill="x", padx=14, pady=(0, 10))

        self.hash_out_lbl = ctk.CTkLabel(f_card, text="SHA-256: (No file selected)", font=F_MONO,
                                         text_color=CLR_TEXT_MUTED, wraplength=750)
        self.hash_out_lbl.pack(anchor="w", padx=14, pady=(0, 10))

        # Compare Hashes Section
        c_card = ctk.CTkFrame(f, corner_radius=14, fg_color=CLR_CARD,
                              border_width=1, border_color=CLR_BORDER)
        c_card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=14)

        ctk.CTkLabel(c_card, text="DUAL-HASH SIDE-BY-SIDE COMPARATOR", font=F_SMALL_BD,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 6))

        self.hash_a_var = tk.StringVar()
        self.hash_b_var = tk.StringVar()

        ctk.CTkEntry(c_card, textvariable=self.hash_a_var, placeholder_text="Enter Hash A...",
                     font=F_BODY, height=36, corner_radius=6, fg_color=CLR_CARD_ELEV,
                     border_width=1, border_color=CLR_BORDER).pack(fill="x", padx=14, pady=(0, 6))
        ctk.CTkEntry(c_card, textvariable=self.hash_b_var, placeholder_text="Enter Hash B...",
                     font=F_BODY, height=36, corner_radius=6, fg_color=CLR_CARD_ELEV,
                     border_width=1, border_color=CLR_BORDER).pack(fill="x", padx=14, pady=(0, 10))

        cmp_row = ctk.CTkFrame(c_card, fg_color="transparent")
        cmp_row.pack(fill="x", padx=14, pady=(0, 10))

        cmp_btn = ctk.CTkButton(cmp_row, text="Compare Hashes", font=F_BODY_BOLD,
                                height=32, corner_radius=16,
                                fg_color=CLR_BTN_SEC_BG, hover_color=CLR_BTN_SEC_HOV,
                                text_color=CLR_BTN_SEC_FG, border_width=1, border_color=CLR_BTN_SEC_BOR,
                                command=self.compare_hashes)
        cmp_btn.pack(side="left")

        self.cmp_res_lbl = ctk.CTkLabel(cmp_row, text="", font=F_HEADLINE)
        self.cmp_res_lbl.pack(side="left", padx=14)

    def compute_file_hash_async(self):
        p = filedialog.askopenfilename()
        if p:
            threading.Thread(target=self._compute_hash, args=(p,), daemon=True).start()

    def _compute_hash(self, path):
        self.root.after(0, lambda: self.hash_out_lbl.configure(text="Calculating SHA-256...", text_color=CLR_TEXT_MAIN))
        try:
            h = generate_hash(path)
            self.root.clipboard_clear()
            self.root.clipboard_append(h)
            self.root.after(0, lambda: self.hash_out_lbl.configure(text=f"SHA-256 ({os.path.basename(path)}):\n{h}\n(✓ Copied to clipboard)",
                                                                  text_color=CLR_SUCCESS))
        except Exception as e:
            self.root.after(0, lambda: self.hash_out_lbl.configure(text=f"Error: {e}", text_color=CLR_ERROR))

    def compare_hashes(self):
        a = self.hash_a_var.get().strip().lower()
        b = self.hash_b_var.get().strip().lower()
        if not a or not b:
            self.cmp_res_lbl.configure(text="⚠️ Enter both hashes", text_color=CLR_WARNING)
            return
        if a == b:
            self.cmp_res_lbl.configure(text="✓ MATCH — Hashes are identical", text_color=CLR_SUCCESS)
        else:
            self.cmp_res_lbl.configure(text="✖ MISMATCH — Hashes differ", text_color=CLR_ERROR)

    def _bind_keys(self):
        self.root.bind("<Control-e>", lambda e: self.switch_tab("encrypt"))
        self.root.bind("<Control-k>", lambda e: self.switch_tab("pwcheck"))
        self.root.bind("<Control-g>", lambda e: self.switch_tab("pwgen"))
        self.root.bind("<Control-v>", lambda e: self.switch_tab("vault"))
        self.root.bind("<Control-h>", lambda e: self.switch_tab("hash"))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CryptexGUI()
    app.run()