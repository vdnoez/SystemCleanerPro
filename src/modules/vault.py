"""
Verschlüsselter Passwort-Speicher (Vault).
Nutzt AES-256 (Fernet) mit PBKDF2-Key-Derivation.
"""
import json
import os
import base64
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

from src.core.config import DATA_DIR


VAULT_FILE = DATA_DIR / "vault.enc"
META_FILE = DATA_DIR / "vault.meta"


# ═══════════════════════════════════════════════════════════════
# KEY-DERIVATION
# ═══════════════════════════════════════════════════════════════
def _derive_key(master_password: str, salt: bytes) -> bytes:
    """Erzeugt AES-Key aus Master-Passwort via PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


# ═══════════════════════════════════════════════════════════════
# VAULT-KLASSE
# ═══════════════════════════════════════════════════════════════
class Vault:
    """Verschlüsselter Passwort-Speicher."""

    def __init__(self):
        self._fernet = None
        self._entries: list = []
        self._unlocked = False

    # ─── Status ────────────────────────────────────────────
    def is_initialized(self) -> bool:
        return VAULT_FILE.exists() and META_FILE.exists()

    def is_unlocked(self) -> bool:
        return self._unlocked

    # ─── Master-Passwort setzen (neuer Vault) ──────────────
    def create(self, master_password: str) -> tuple:
        if not HAS_CRYPTO:
            return False, "cryptography-Bibliothek fehlt"
        if len(master_password) < 6:
            return False, "Master-Passwort muss min. 6 Zeichen haben"
        try:
            salt = secrets.token_bytes(16)
            key = _derive_key(master_password, salt)
            self._fernet = Fernet(key)
            self._entries = []
            self._unlocked = True

            # Salt speichern (ohne Passwort)
            META_FILE.write_text(
                json.dumps({
                    "salt": base64.b64encode(salt).decode(),
                    "created": datetime.now().isoformat(),
                    "version": 1,
                }, indent=2),
                encoding="utf-8",
            )
            self._save()
            return True, "Vault erstellt"
        except Exception as e:
            return False, str(e)

    # ─── Vault entsperren ──────────────────────────────────
    def unlock(self, master_password: str) -> tuple:
        if not HAS_CRYPTO:
            return False, "cryptography-Bibliothek fehlt"
        if not self.is_initialized():
            return False, "Kein Vault vorhanden"
        try:
            meta = json.loads(META_FILE.read_text(encoding="utf-8"))
            salt = base64.b64decode(meta["salt"])
            key = _derive_key(master_password, salt)
            self._fernet = Fernet(key)

            # Test-Entschlüsselung
            data = VAULT_FILE.read_bytes()
            if data:
                decrypted = self._fernet.decrypt(data)
                self._entries = json.loads(decrypted.decode("utf-8"))
            else:
                self._entries = []

            self._unlocked = True
            return True, "Entsperrt"
        except InvalidToken:
            self._fernet = None
            return False, "Falsches Master-Passwort"
        except Exception as e:
            self._fernet = None
            return False, str(e)

    # ─── Speichern ─────────────────────────────────────────
    def _save(self) -> bool:
        if not self._fernet:
            return False
        try:
            data = json.dumps(self._entries, ensure_ascii=False)
            encrypted = self._fernet.encrypt(data.encode("utf-8"))
            VAULT_FILE.write_bytes(encrypted)
            return True
        except Exception:
            return False

    def lock(self):
        self._fernet = None
        self._entries = []
        self._unlocked = False

    # ─── CRUD ──────────────────────────────────────────────
    def get_all(self) -> list:
        return list(self._entries)

    def add(self, name: str, username: str, password: str,
            url: str = "", category: str = "Sonstiges",
            notes: str = "") -> tuple:
        if not self._unlocked:
            return False, "Vault gesperrt"
        entry = {
            "id": secrets.token_hex(8),
            "name": name,
            "username": username,
            "password": password,
            "url": url,
            "category": category,
            "notes": notes,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
        }
        self._entries.append(entry)
        self._save()
        return True, entry["id"]

    def update(self, entry_id: str, **fields) -> tuple:
        if not self._unlocked:
            return False, "Vault gesperrt"
        for e in self._entries:
            if e["id"] == entry_id:
                for k, v in fields.items():
                    if k in e:
                        e[k] = v
                e["modified"] = datetime.now().isoformat()
                self._save()
                return True, "Aktualisiert"
        return False, "Eintrag nicht gefunden"

    def delete(self, entry_id: str) -> tuple:
        if not self._unlocked:
            return False, "Vault gesperrt"
        before = len(self._entries)
        self._entries = [e for e in self._entries if e["id"] != entry_id]
        if len(self._entries) == before:
            return False, "Eintrag nicht gefunden"
        self._save()
        return True, "Gelöscht"

    def get_categories(self) -> list:
        cats = set()
        for e in self._entries:
            cats.add(e.get("category", "Sonstiges"))
        return sorted(cats)


# Globale Vault-Instanz
vault = Vault()