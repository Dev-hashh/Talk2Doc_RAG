

# -------------------------
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import User
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BCRYPT_MAX_BYTES = 72

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


# 🔐 Password utils
def _validate_password_for_bcrypt(password: str) -> None:
    if len(password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError("Password must be 72 bytes or fewer.")


def hash_password(password: str) -> str:
    _validate_password_for_bcrypt(password)
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    if len(plain.encode("utf-8")) > BCRYPT_MAX_BYTES:
        return False
    return pwd_context.verify(plain, hashed)


# 🔑 JWT
def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.auth_token_minutes))
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.auth_secret, algorithm=ALGORITHM)


# 👤 User queries
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.strip().lower()).first()


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
    normalized_email = email.strip().lower()
    existing = get_user_by_email(db, normalized_email)
    if existing:
        raise ValueError("Email already registered")
    _validate_password_for_bcrypt(password)
    user = User(
        name=name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
