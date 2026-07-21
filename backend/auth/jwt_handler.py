"""JWT helpers + password hashing.

Hashing uses scrypt from the standard library so the auth path has no
heavy dependency surface. Format: scrypt$N$r$p$salt_hex$dk_hex.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from config import get_settings


_SCRYPT_N = 2 ** 14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 32


def hash_password(plain: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(
        plain.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=_SCRYPT_DKLEN
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${dk.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        scheme, n, r, p, salt_hex, dk_hex = hashed.split("$")
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(dk_hex)
    candidate = hashlib.scrypt(
        plain.encode("utf-8"),
        salt=salt,
        n=int(n),
        r=int(r),
        p=int(p),
        dklen=len(expected),
    )
    return hmac.compare_digest(candidate, expected)


def create_access_token(subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=s.jwt_expire_minutes)).timestamp()),
        **(extra or {}),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_alg)


def decode_token(token: str) -> dict[str, Any]:
    s = get_settings()
    try:
        return jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_alg])
    except JWTError as e:
        raise ValueError(f"invalid token: {e}") from e
