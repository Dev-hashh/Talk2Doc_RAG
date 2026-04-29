from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from sqlite3 import IntegrityError, Row

from app.config import settings
from app.db import get_connection


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"pbkdf2_sha256${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt_text, digest_text = stored_hash.split("$", 2)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    salt = _b64url_decode(salt_text)
    expected = _b64url_decode(digest_text)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + settings.auth_token_minutes * 60,
    }
    payload_text = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        settings.auth_secret.encode("utf-8"),
        payload_text.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload_text}.{_b64url_encode(signature)}"


def verify_access_token(token: str) -> int | None:
    try:
        payload_text, signature_text = token.split(".", 1)
        expected = hmac.new(
            settings.auth_secret.encode("utf-8"),
            payload_text.encode("ascii"),
            hashlib.sha256,
        ).digest()
        actual = _b64url_decode(signature_text)

        if not hmac.compare_digest(actual, expected):
            return None

        payload = json.loads(_b64url_decode(payload_text))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None

        return int(payload["sub"])
    except Exception:
        return None


def create_user(name: str, email: str, password: str) -> Row:
    normalized_email = email.strip().lower()

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (name.strip(), normalized_email, hash_password(password)),
            )
            user_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    except IntegrityError as exc:
        raise ValueError("An account with this email already exists.") from exc

    if row is None:
        raise RuntimeError("User creation failed.")

    return row


def authenticate_user(email: str, password: str) -> Row | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()

    if row is None or not verify_password(password, row["password_hash"]):
        return None

    return row


def get_user(user_id: int) -> Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
