"""
vault_manager.py — AES-256 Encrypted Credential Vault Manager
Part of Cryptex - Secure File Encryption
Author: Ojas Purohit (https://github.com/OjasPurohit)

AES-256 via Fernet with PBKDF2 key derivation and secure salt management.
"""
import json, os, hashlib, base64
from cryptography.fernet import Fernet, InvalidToken

from security import get_storage_dirs

try:
    _, _, _, VAULT_DIR = get_storage_dirs()
except Exception:
    VAULT_DIR = "vault"

VAULT_FILE = os.path.join(VAULT_DIR, "passwords.vault")
SALT_FILE  = os.path.join(VAULT_DIR, "vault.salt")
META_FILE  = os.path.join(VAULT_DIR, "vault.meta")

# Migrate from legacy local vault/ folder if exists and new vault doesn't
legacy_vault = os.path.join("vault", "passwords.vault")
if os.path.exists(legacy_vault) and not os.path.exists(VAULT_FILE):
    try:
        import shutil
        for f_name in ["passwords.vault", "vault.salt", "vault.meta"]:
            src = os.path.join("vault", f_name)
            dst = os.path.join(VAULT_DIR, f_name)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
    except Exception:
        pass

ITERATIONS = 200_000


def _load_salt() -> bytes:
    """Load the vault's salt. Salt is NOT secret — it's stored in plaintext."""
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            return f.read()
    # Legacy fallback
    return b"cryptex_static_salt_v1"

def _make_key(master: str) -> bytes:
    """Derive a Fernet key from master password + stored salt."""
    salt = _load_salt()
    dk = hashlib.pbkdf2_hmac("sha256", master.encode("utf-8"), salt, ITERATIONS)
    return base64.urlsafe_b64encode(dk)

def vault_exists() -> bool:
    return os.path.exists(VAULT_FILE)

def get_hint() -> str:
    try:
        if os.path.exists(META_FILE):
            with open(META_FILE) as f:
                return json.load(f).get("hint", "")
    except:
        pass
    return ""

def init_vault(master: str, hint: str = "") -> bool:
    """Create brand-new vault. Generates and saves a fresh salt."""
    os.makedirs(VAULT_DIR, exist_ok=True)
    # Generate and persist the salt BEFORE deriving the key
    import secrets
    salt = secrets.token_bytes(32)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    # Now derive key and encrypt an empty entries list
    key = _make_key(master)
    token = Fernet(key).encrypt(json.dumps([]).encode())
    with open(VAULT_FILE, "wb") as f:
        f.write(token)
    if hint:
        os.makedirs(VAULT_DIR, exist_ok=True)
        with open(META_FILE, "w") as f:
            json.dump({"hint": hint}, f)
    return True

def load_vault(master: str) -> list:
    """Decrypt and return entries list. Raises ValueError on wrong password."""
    if not vault_exists():
        return []
    key = _make_key(master)
    with open(VAULT_FILE, "rb") as f:
        raw = f.read()
    try:
        decrypted = Fernet(key).decrypt(raw)
    except InvalidToken:
        raise ValueError("Wrong master password")
    data = json.loads(decrypted.decode())
    # Support both plain list (old) and dict format
    if isinstance(data, list):
        return data
    return data.get("entries", [])

def save_vault(master: str, entries: list) -> bool:
    """Encrypt and persist entries."""
    os.makedirs(VAULT_DIR, exist_ok=True)
    key = _make_key(master)
    token = Fernet(key).encrypt(json.dumps(entries, indent=2).encode())
    with open(VAULT_FILE, "wb") as f:
        f.write(token)
    return True

def add_entry(master: str, site: str, username: str,
              password: str, notes: str = "") -> bool:
    entries = load_vault(master)
    new_id  = max((e.get("id", 0) for e in entries), default=0) + 1
    entries.append({"id": new_id, "site": site.strip(),
                    "username": username.strip(),
                    "password": password,
                    "notes":    notes.strip()})
    return save_vault(master, entries)

def delete_entry(master: str, entry_id: int) -> bool:
    entries = [e for e in load_vault(master) if e.get("id") != entry_id]
    return save_vault(master, entries)

def reset_vault() -> bool:
    """Wipe vault completely — user confirmed they forgot the password."""
    for path in [VAULT_FILE, SALT_FILE, META_FILE]:
        if os.path.exists(path):
            os.remove(path)
    return True

def change_master(old_master: str, new_master: str) -> bool:
    """Re-encrypt with new master. Generates new salt too."""
    entries = load_vault(old_master)   # raises if old_master wrong
    # Overwrite salt with a fresh one
    import secrets
    with open(SALT_FILE, "wb") as f:
        f.write(secrets.token_bytes(32))
    return save_vault(new_master, entries)