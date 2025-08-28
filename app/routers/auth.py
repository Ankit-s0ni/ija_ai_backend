from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from datetime import timedelta

from app.core.security import create_access_token, get_current_user
from app.core.config import settings
from app.schemas.token import AuthResponse
from app.schemas.user import UserOut, UserCreate
from app.crud.user import get_user_by_google_id, create_user

router = APIRouter()

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID


@router.post("/google", response_model=AuthResponse)
async def google_login(request: dict):
    """
    Authenticate user with Google ID token
    Expects: {"id_token": "google_id_token_string"}
    """
    print(f"[DEBUG] Google login request received: {list(request.keys())}")
    
    try:
        google_id_token = request.get("id_token")
        if not google_id_token:
            print("[DEBUG] No id_token in request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID token is required",
            )

        print(f"[DEBUG] Verifying token with client ID: {GOOGLE_CLIENT_ID}")
        
        try:
            # Verify the Google ID token
            id_info = id_token.verify_oauth2_token(
                google_id_token, requests.Request(), GOOGLE_CLIENT_ID
            )

            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Wrong issuer")

            google_id_val = id_info["sub"]
            email = id_info["email"]
            name = id_info.get("name", "")
            picture = id_info.get("picture", "")
            
            print(f"[DEBUG] Token verified successfully for user: {email}")
            
        except Exception as e:
            print(f"[DEBUG] Token verification failed: {e}")
            raise ValueError(f"Invalid Google token: {str(e)}")

        # Check if user exists
        user = await get_user_by_google_id(google_id_val)

        if not user:
            # Create new user
            user_create = UserCreate(
                email=email,
                full_name=name,
                google_id=google_id_val,
                profile_picture_url=picture,
            )
            user = await create_user(user_create)

        # Create access token
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        # Build response with token and user info
        user_out = UserOut(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            google_id=user.google_id,
            profile_picture_url=user.profile_picture_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_out,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
        )
    except GoogleAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}",
        )

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout user (client should delete the token)
    """
    return {"message": "Successfully logged out"}
