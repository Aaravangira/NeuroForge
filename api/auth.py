"""
AI Invoice Extractor
Google Authentication API
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from jose import jwt
from sqlalchemy.orm import Session

from config import (
    GOOGLE_REDIRECT_URI,
    JWT_ALGORITHM,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

from database import get_db
from models.user_model import User
from services.auth_service import oauth


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


def create_access_token(user_id: int) -> str:
    """Create JWT access token for authenticated user."""

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


@router.get("/google")
async def google_login(request: Request):
    """Start Google OAuth login."""

    return await oauth.google.authorize_redirect(
        request,
        GOOGLE_REDIRECT_URI,
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle Google OAuth callback."""

    try:
        token = await oauth.google.authorize_access_token(
            request
        )

        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(
                status_code=401,
                detail="Google user information unavailable.",
            )

        google_id = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")

        if not google_id or not email:
            raise HTTPException(
                status_code=401,
                detail="Google account information incomplete.",
            )

        # --------------------------------------------------
        # Find existing user
        # --------------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.google_id == google_id
            )
            .first()
        )

        # --------------------------------------------------
        # If Google ID doesn't exist, check email
        # --------------------------------------------------

        if user is None:

            user = (
                db.query(User)
                .filter(
                    User.email == email
                )
                .first()
            )

        # --------------------------------------------------
        # Create new user
        # --------------------------------------------------

        if user is None:

            user = User(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture,
                plan="trial",
                trial_used=0,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        # --------------------------------------------------
        # Update existing user
        # --------------------------------------------------

        else:

            user.google_id = google_id
            user.name = name
            user.picture = picture

            db.commit()
            db.refresh(user)

        # --------------------------------------------------
        # Create JWT
        # --------------------------------------------------

        access_token = create_access_token(
            user.id
        )

        return {
            "success": True,
            "message": "Google authentication successful.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "plan": user.plan,
                "trial_used": user.trial_used,
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Google authentication failed.",
        ) from exc


@router.get("/me")
def get_current_user_info(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Temporary user information endpoint.

    We will replace the user_id parameter with
    JWT authentication middleware in the next step.
    """

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "plan": user.plan,
            "trial_used": user.trial_used,
        },
    }