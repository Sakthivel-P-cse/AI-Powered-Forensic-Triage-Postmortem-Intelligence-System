"""Field-level AES-256-GCM for subject PII.

Spec: 'Database fields: field-level encryption for subject PII'.

Usage:
    from storage.encryption import encrypt_field, decrypt_field
    cipher = encrypt_field('Subject A real name')   # → 'v1:<b64nonce>:<b64ct>'
    plain  = decrypt_field(cipher)

The DEK is loaded from FORENSIC_FIELD_KEY (urlsafe-base64-encoded 32 bytes).
If unset, encryption is a no-op pass-through that prefixes 'plain:' so the
audit log can tell the difference. Production deployments MUST set the key.
"""
from __future__ import annotations

import base64
import logging
import os
import secrets

log = logging.getLogger(__name__)

_KEY_ENV = "FORENSIC_FIELD_KEY"
_PLAIN_PREFIX = "plain:"
_VERSION = "v1"


def _load_key() -> bytes | None:
    raw = os.environ.get(_KEY_ENV)
    if not raw:
        return None
    try:
        key = base64.urlsafe_b64decode(raw)
    except Exception:
        log.warning("FORENSIC_FIELD_KEY is not valid urlsafe-base64; PII encryption disabled")
        return None
    if len(key) != 32:
        log.warning("FORENSIC_FIELD_KEY must decode to 32 bytes (got %d); disabled", len(key))
        return None
    return key


def encrypt_field(plain: str) -> str:
    if plain is None:
        return plain  # type: ignore[return-value]
    key = _load_key()
    if key is None:
        return f"{_PLAIN_PREFIX}{plain}"

    # Lazy import — only required when a key is actually configured.
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    nonce = secrets.token_bytes(12)
    ct = AESGCM(key).encrypt(nonce, plain.encode("utf-8"), None)
    return f"{_VERSION}:{base64.urlsafe_b64encode(nonce).decode()}:{base64.urlsafe_b64encode(ct).decode()}"


def decrypt_field(cipher: str) -> str:
    if cipher is None:
        return cipher  # type: ignore[return-value]
    if cipher.startswith(_PLAIN_PREFIX):
        return cipher[len(_PLAIN_PREFIX):]
    try:
        version, b64_nonce, b64_ct = cipher.split(":", 2)
    except ValueError:
        return cipher  # not in our format — treat as opaque
    if version != _VERSION:
        raise ValueError(f"unsupported field-encryption version: {version}")
    key = _load_key()
    if key is None:
        raise RuntimeError("ciphertext present but FORENSIC_FIELD_KEY unset")

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    nonce = base64.urlsafe_b64decode(b64_nonce)
    ct = base64.urlsafe_b64decode(b64_ct)
    return AESGCM(key).decrypt(nonce, ct, None).decode("utf-8")
