import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret_demo_key_change_me")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token (str): The JWT token string, typically passed in the Authorization header.

    Returns:
        dict: The decoded payload of the token containing user claims
              (e.g., `sub`, `role`, `exp`).

    Raises:
        HTTPException:
            - 401 if the token is expired.
            - 401 if the token is invalid or cannot be decoded.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency to retrieve the current authenticated user.

    This function extracts the OAuth2 token from the request using the
    `oauth2_scheme`, decodes it, and returns the user payload.

    Args:
        token (str): The JWT token automatically provided by FastAPI's dependency injection.

    Returns:
        dict: The decoded user payload, including claims like username (`sub`)
              and role (`role`).

    Raises:
        HTTPException: If the token is expired or invalid.
    """
    return decode_token(token)
