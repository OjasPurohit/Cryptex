"""
decrypt.py — AES-256 File Decryption Engine with Integrity Check & Self-Destruct Protection
Part of Cryptex - Secure File Encryption
Author: Ojas Purohit (https://github.com/OjasPurohit)
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import os
from security import generate_hash, get_storage_dirs

attempts = 0
MAX_ATTEMPTS = 3

def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def decrypt_file(filename, password, target_dir=None):
    global attempts

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Encrypted file not found: {filename}")

    key = generate_key(password)
    f = Fernet(key)

    try:
        with open(filename, "rb") as file:
            encrypted = file.read()

        decrypted = f.decrypt(encrypted)

        # Resolve target decrypted folder
        if not target_dir:
            _, _, target_dir, _ = get_storage_dirs()
        os.makedirs(target_dir, exist_ok=True)

        output_name = os.path.basename(filename).replace(".cryptex", "")
        output_path = os.path.join(target_dir, output_name)

        with open(output_path, "wb") as file:
            file.write(decrypted)

        # Verify integrity using hash file
        hash_file = filename + ".hash"
        integrity_ok = True
        if os.path.exists(hash_file):
            stored_hash = open(hash_file).read().strip()
            new_hash = generate_hash(output_path)
            if stored_hash == new_hash:
                print(f"Integrity verified — saved to {output_path}")
            else:
                integrity_ok = False
                print(f"Warning: file may have been modified — saved to {output_path}")
        else:
            print(f"File decrypted successfully — saved to {output_path}")

        attempts = 0
        return output_path

    except Exception as e:
        attempts += 1
        print(f"Wrong password attempt {attempts}")
        if attempts >= MAX_ATTEMPTS:
            print("Too many failed attempts. Access blocked.")
        raise