import uuid
from datetime import datetime, timedelta
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.config import Config

from backend.src.auth.jwt import create_access_token, create_refresh_token
from backend.src.database import SessionLocal
from backend.src.models import OAuthAccount, RefreshToken, User

router = APIRouter(prefix="/api/v1/oauth", tags=["oauth"])

config = Config(".env")
oauth = OAuth(config)

# Configure OAuth providers
oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=config("GOOGLE_REDIRECT_URI"),
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    client_id=config("GITHUB_CLIENT_ID"),
    client_secret=config("GITHUB_CLIENT_SECRET"),
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=config("GITHUB_REDIRECT_URI"),
    client_kwargs={"scope": "user:email"},
)

oauth.register(
    name="microsoft",
    client_id=config("MICROSOFT_CLIENT_ID"),
    client_secret=config("MICROSOFT_CLIENT_SECRET"),
    authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    authorize_params=None,
    access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=config("MICROSOFT_REDIRECT_URI"),
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login/{provider}")
async def login_via_provider(request: Request, provider: str):
    if provider not in ["google", "github", "microsoft"]:
        raise HTTPException(status_code=404, detail="Provider not supported")

    redirect_uri = request.url_for(f"auth_via_{provider}")
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@router.get("/auth/{provider}")
async def auth_via_provider(request: Request, provider: str):
    client = oauth.create_client(provider)
    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_info = await client.parse_id_token(request, token)
    if not user_info.get("email"):
        raise HTTPException(status_code=400, detail="Email not provided by provider")

    db = SessionLocal()
    try:
        # Find or create user
        user = db.query(User).filter(User.email == user_info["email"]).first()
        if not user:
            user = User(
                username=user_info.get("email"),
                email=user_info["email"],
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create or update OAuth account
        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_account_id == user_info.get("sub"),
            )
            .first()
        )

        if not oauth_account:
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_account_id=user_info.get("sub"),
                access_token=token.get("access_token"),
                refresh_token=token.get("refresh_token"),
                expires_at=int(token.get("expires_at"))
                if token.get("expires_at")
                else None,
                token_type=token.get("token_type"),
                scope=token.get("scope"),
            )
            db.add(oauth_account)
        else:
            oauth_account.access_token = token.get("access_token")
            oauth_account.refresh_token = token.get("refresh_token")
            oauth_account.expires_at = (
                int(token.get("expires_at")) if token.get("expires_at") else None
            )
            oauth_account.token_type = token.get("token_type")
            oauth_account.scope = token.get("scope")

        db.commit()

        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token(str(user.id))

        # Store refresh token
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(db_refresh_token)
        db.commit()

        # Redirect with tokens
        response = RedirectResponse(url="/")
        response.set_cookie(
            key="access_token", value=f"Bearer {access_token}", httponly=True
        )
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        return response

    finally:
        db.close()
