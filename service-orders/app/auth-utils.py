import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret_demo_key_change_me")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return decode_token(token)
