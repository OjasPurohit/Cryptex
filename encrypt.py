"""
encrypt.py — AES-256 File Encryption Engine with Auto-Shredding & Integrity Hashing
Part of Cryptex - Secure File Encryption
Author: Ojas Purohit (https://github.com/OjasPurohit)
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import os
from security import generate_hash, get_storage_dirs, secure_wipe_file

def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_file(filename, password, delete_original=True, target_dir=None):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Source file not found: {filename}")

    key = generate_key(password)
    f = Fernet(key)

    with open(filename, "rb") as file:
        data = file.read()

    encrypted = f.encrypt(data)
    base_name = os.path.basename(filename)

    # Resolve target encrypted folder
    if not target_dir:
        _, target_dir, _, _ = get_storage_dirs()
    os.makedirs(target_dir, exist_ok=True)

    output_file = os.path.join(target_dir, base_name + ".cryptex")

    # Write encrypted file
    with open(output_file, "wb") as file:
        file.write(encrypted)

    # Compute & write hash
    file_hash = generate_hash(filename)
    with open(output_file + ".hash", "w") as h:
        h.write(file_hash)

    # Securely shred and delete original file if requested and distinct
    original_deleted = False
    if delete_original and os.path.abspath(filename) != os.path.abspath(output_file):
        try:
            secure_wipe_file(filename)
            original_deleted = True
            print(f"Original plaintext file securely deleted: {filename}")
        except Exception as e:
            print(f"Warning: Could not securely delete original file: {e}")

    print(f"File encrypted successfully — saved to {output_file}")
    return output_file, original_deleted