# from __future__ import annotations

# from sqlite3 import Row

# from backend.app import db
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# from app.services.auth_service import get_user, verify_access_token, get_user_by_id

# bearer_scheme = HTTPBearer(auto_error=False)


# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
# ) -> Row:
#     if credentials is None or credentials.scheme.lower() != "bearer":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication required.",
#         )

#     user_id = verify_access_token(credentials.credentials)
#     if user_id is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token.",
#         )

#     user = get_user_by_id(db, user_id)
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User no longer exists.",
#         )

#     return user


# -------------
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import get_db                              # ✅ import the function, not the module
from app.services.auth_service import get_user_by_id
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),                     # ✅ FastAPI injects a real Session here
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    user = get_user_by_id(db, user_id)                 # ✅ db is a Session instance
    if user is None:
        raise credentials_exception
    return user