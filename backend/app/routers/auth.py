from __future__ import annotations

from sqlite3 import Row

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user
from app.schemas.models import AuthResponse, LoginRequest, UserCreate, UserPublic
from app.services.auth_service import authenticate_user, create_access_token, create_user

router = APIRouter(prefix="/auth", tags=["Auth"])


def _public_user(row: Row) -> UserPublic:
    return UserPublic(id=row["id"], name=row["name"], email=row["email"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserCreate) -> AuthResponse:
    try:
        user = create_user(body.name, body.email, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return AuthResponse(
        access_token=create_access_token(user["id"]),
        user=_public_user(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest) -> AuthResponse:
    user = authenticate_user(body.email, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return AuthResponse(
        access_token=create_access_token(user["id"]),
        user=_public_user(user),
    )


@router.get("/me", response_model=UserPublic)
async def me(user: Row = Depends(get_current_user)) -> UserPublic:
    return _public_user(user)
