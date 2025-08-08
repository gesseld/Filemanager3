import uuid
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.src.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from pydantic import BaseModel, EmailStr

from backend.src.auth.jwt import (Token, create_access_token,
                                  create_refresh_token, get_password_hash,
                                  rotate_refresh_token, verify_password,
                                  verify_token)
from backend.src.models import RefreshToken, User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool


class TokenResponse(Token):
    user: UserResponse


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=str(user.id),
        username=str(user.username),
        email=str(user.email),
        is_active=bool(user.is_active),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    refresh_token = create_refresh_token(str(user.id))

    # Store refresh token in database
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(db_refresh_token)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=datetime.utcnow() + timedelta(minutes=30),
        refresh_token=refresh_token,
        user=UserResponse(
            id=str(user.id),
            username=str(user.username),
            email=str(user.email),
            is_active=bool(user.is_active),
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = verify_token(refresh_token)
        user_id = payload.user_id
        new_refresh_token = rotate_refresh_token(db, user_id, refresh_token)

        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
            )

        new_access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )

        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            refresh_token=new_refresh_token,
            user=UserResponse(
                id=str(user.id),
                username=str(user.username),
                email=str(user.email),
                is_active=bool(user.is_active),
            ),
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    # Delete refresh token from database
    db.query(RefreshToken).filter(RefreshToken.token == refresh_token).delete()
    db.commit()
    return {"message": "Successfully logged out"}
