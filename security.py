"""
security.py — Cryptographic Helper Functions & Dedicated Storage Manager
Part of Cryptex - Secure File Encryption
Author: Ojas Purohit (https://github.com/OjasPurohit)
"""

import hashlib
import os
import re
import secrets

def get_storage_dirs():
    """
    Returns standard dedicated storage directories for Cryptex:
    Base: %USERPROFILE%/Cryptex (or fallback to local folder)
    """
    try:
        user_home = os.path.expanduser("~")
        base_dir = os.path.join(user_home, "Cryptex")
    except Exception:
        base_dir = os.path.abspath("Cryptex_Data")

    enc_dir = os.path.join(base_dir, "Encrypted")
    dec_dir = os.path.join(base_dir, "Decrypted")
    vault_dir = os.path.join(base_dir, "Vault")

    for d in [base_dir, enc_dir, dec_dir, vault_dir]:
        os.makedirs(d, exist_ok=True)

    return base_dir, enc_dir, dec_dir, vault_dir

def secure_wipe_file(file_path: str):
    """
    Securely shred/wipes a file by overwriting its content with random bytes and zeros
    before removing it from the filesystem.
    """
    if not os.path.exists(file_path):
        return
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, "wb") as f:
            # Overwrite with random bytes
            if file_size > 0:
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())
                # Overwrite with zeros
                f.seek(0)
                f.write(b"\x00" * file_size)
                f.flush()
                os.fsync(f.fileno())
    except Exception:
        pass

    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not remove file {file_path}: {e}")

def generate_hash(file_path: str) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

def password_strength(password: str) -> str:
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[!@#$%^&*]", password):
        score += 1

    if score <= 1:
        return "Weak"
    elif score == 2:
        return "Medium"
    else:
        return "Strong"