# from __future__ import annotations

# import base64
# import hashlib
# import hmac
# import json
# import secrets
# import time
# from sqlite3 import IntegrityError, Row

# from app.config import settings
# from sqlalchemy.orm import Session
# from app.db import SessionLocal
# from app.db import User


# def _b64url_encode(raw: bytes) -> str:
#     return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


# def _b64url_decode(value: str) -> bytes:
#     padding = "=" * (-len(value) % 4)
#     return base64.urlsafe_b64decode(value + padding)


# def hash_password(password: str) -> str:
#     salt = secrets.token_bytes(16)
#     digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
#     return f"pbkdf2_sha256${_b64url_encode(salt)}${_b64url_encode(digest)}"


# def verify_password(password: str, stored_hash: str) -> bool:
#     try:
#         algorithm, salt_text, digest_text = stored_hash.split("$", 2)
#     except ValueError:
#         return False

#     if algorithm != "pbkdf2_sha256":
#         return False

#     salt = _b64url_decode(salt_text)
#     expected = _b64url_decode(digest_text)
#     actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
#     return hmac.compare_digest(actual, expected)


# def create_access_token(user_id: int) -> str:
#     payload = {
#         "sub": user_id,
#         "exp": int(time.time()) + settings.auth_token_minutes * 60,
#     }
#     payload_text = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
#     signature = hmac.new(
#         settings.auth_secret.encode("utf-8"),
#         payload_text.encode("ascii"),
#         hashlib.sha256,
#     ).digest()
#     return f"{payload_text}.{_b64url_encode(signature)}"


# def verify_access_token(token: str) -> int | None:
#     try:
#         payload_text, signature_text = token.split(".", 1)
#         expected = hmac.new(
#             settings.auth_secret.encode("utf-8"),
#             payload_text.encode("ascii"),
#             hashlib.sha256,
#         ).digest()
#         actual = _b64url_decode(signature_text)

#         if not hmac.compare_digest(actual, expected):
#             return None

#         payload = json.loads(_b64url_decode(payload_text))
#         if int(payload.get("exp", 0)) < int(time.time()):
#             return None

#         return int(payload["sub"])
#     except Exception:
#         return None



# def create_user(db: Session, name: str, email: str, password_hash: str):
#     user = User(name=name, email=email, password_hash=password_hash)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user


# def authenticate_user(db: Session, email: str, password: str):
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         return None

#     if not verify_password(password, user.password_hash):
#         return None

#     return user


# def get_user(db: Session, email: str):
#     return db.query(User).filter(User.email == email).first()

# def get_user_by_id(db: Session, user_id: int):
#     return db.query(User).filter(User.id == user_id).first()


# -------------------------
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import User
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


# 🔐 Password utils
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# 🔑 JWT
def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.auth_token_minutes))
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.auth_secret, algorithm=ALGORITHM)


# 👤 User queries
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:  # ✅ takes Session, not module
    return db.query(User).filter(User.id == user_id).first()


# 🔓 Auth
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# 📝 Register
def create_user(db: Session, name: str, email: str, password: str) -> User:
    existing = get_user_by_email(db, email)
    if existing:
        raise ValueError("Email already registered")
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user