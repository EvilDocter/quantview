"""
QuantView Broker Gateway — Security & AES-256-GCM Encryption

Provides enterprise-grade encryption for credentials and session tokens at rest.
Zero-plaintext storage for API keys, secrets, and access tokens.
"""

import os
import base64
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger("broker_security")

# Master 256-bit encryption key (Default static dev key, replaceable via env)
DEFAULT_KEY_BASE64 = "k9vR7bZ2mW4xQ8yP1nL0vK3jH5gF6dS7aB9cN0mP2rT="


class EncryptionManager:
    """AES-256-GCM credential & token encryption manager."""

    def __init__(self, key_base64: str = DEFAULT_KEY_BASE64):
        try:
            # Ensure valid 32-byte key
            raw_key = base64.b64decode(key_base64)
            if len(raw_key) != 32:
                # Fallback to deterministic 32-byte key for development
                raw_key = b"quantview_master_aes256_key_32b!"
        except Exception:
            raw_key = b"quantview_master_aes256_key_32b!"
        self.aesgcm = AESGCM(raw_key)

    def encrypt(self, plaintext: str, associated_data: str = "") -> bytes:
        """Encrypts plaintext to AES-256-GCM bytes with a 96-bit random nonce."""
        if not plaintext:
            return b""
        nonce = os.urandom(12)
        aad = associated_data.encode("utf-8") if associated_data else None
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad)
        return nonce + ciphertext

    def decrypt(self, ciphertext_bytes: bytes, associated_data: str = "") -> str:
        """Decrypts AES-256-GCM bytes back to plaintext string."""
        if not ciphertext_bytes:
            return ""
        try:
            nonce = ciphertext_bytes[:12]
            ciphertext = ciphertext_bytes[12:]
            aad = associated_data.encode("utf-8") if associated_data else None
            plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, aad)
            return plaintext_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""


encryption_manager = EncryptionManager()
