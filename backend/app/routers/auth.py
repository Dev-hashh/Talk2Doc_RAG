# from __future__ import annotations

# from sqlite3 import Row

# from fastapi import APIRouter, Depends, HTTPException, status

# from sqlalchemy.orm import Session

# from app.db import get_db
# from app.db import User
# from app.deps import get_current_user
# from app.schemas.models import AuthResponse, LoginRequest, UserCreate, UserPublic
# from app.services.auth_service import authenticate_user, create_access_token, create_user

# router = APIRouter(prefix="/auth", tags=["Auth"])



# def _public_user(user: User) -> UserPublic:
#     return UserPublic(
#         id=user.id,
#         name=user.name,
#         email=user.email
#     )

# @router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
# async def signup(
#     body: UserCreate,
#     db: Session = Depends(get_db)
# ) -> AuthResponse:
#     try:
#         user = create_user(db, body.name, body.email, body.password)
#     except ValueError as exc:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

#     return AuthResponse(
#         access_token=create_access_token(user["id"]),
#         user=_public_user(user),
#     )


# @router.post("/login", response_model=AuthResponse)
# async def login(
#     body: LoginRequest,
#     db: Session = Depends(get_db)
# ) -> AuthResponse:
#     user = authenticate_user(db, body.email, body.password)
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password.",
#         )

#     return AuthResponse(
#         access_token=create_access_token(user.id),
#         user=_public_user(user),
#     )


# @router.get("/me", response_model=UserPublic)
# async def me(user: User = Depends(get_current_user)) -> UserPublic:
#     return _public_user(user) 


# --------------

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.db import get_db
from app.services.auth_service import authenticate_user, create_access_token, get_user_by_id, create_user
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str
    
    
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    try:
        user = create_user(db, body.name, body.email, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return {
        "access_token": create_access_token(user.id),  # ✅ dot notation
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    }
    
    
@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(user.id)   # ✅ dot notation, not user["id"]
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    }


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }