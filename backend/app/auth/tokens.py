"""
Encrypt/decrypt OAuth tokens before they touch the database.

We use Fernet (symmetric, authenticated encryption) rather than storing
tokens in plaintext. The key comes from TOKEN_ENCRYPTION_KEY, which must be
kept out of source control and rotated if ever exposed.
"""

from cryptography.fernet import Fernet

from app.config import get_settings


def _fernet() -> Fernet:
    settings = get_settings()
    return Fernet(settings.token_encryption_key.encode())


def encrypt_token(plaintext: str) -> bytes:
    return _fernet().encrypt(plaintext.encode())


def decrypt_token(ciphertext: bytes) -> str:
    return _fernet().decrypt(ciphertext).decode()
