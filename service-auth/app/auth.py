import os
from datetime import datetime, timedelta
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret_demo_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def create_access_token(subject: str, data: dict | None = None, expires_delta: timedelta | None = None):
    to_encode = {"sub": subject}
    if data:
        to_encode.update(data)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except Exception:
        raise
