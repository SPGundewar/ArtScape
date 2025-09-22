import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database, auth, utils
from database import SessionLocal, engine
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# CORS - allow UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """
    Dependency that provides a SQLAlchemy session for database operations.

    Yields:
        Session: Active SQLAlchemy database session.
    Ensures:
        The session is closed once the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Checks whether the username is already taken. If available, hashes
    the provided password and creates a new user record in the database.

    Args:
        user_in (schemas.UserCreate): The incoming user registration data (username, password, role).
        db (Session): Database session dependency.

    Raises:
        HTTPException: 400 if the username is already registered.

    Returns:
        schemas.UserOut: The newly created user record (without password).
    """
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = utils.hash_password(user_in.password)
    user = models.User(username=user_in.username, hashed_password=hashed, role=user_in.role or "user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.

    Validates the provided username and password against the database.
    If valid, issues a JWT access token containing the username and role.

    Args:
        form_data (OAuth2PasswordRequestForm): OAuth2 form containing username and password.
        db (Session): Database session dependency.

    Raises:
        HTTPException: 401 if the username or password is incorrect.

    Returns:
        schemas.Token: Access token and token type.
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth.create_access_token(subject=user.username, data={"role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserOut)
def read_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieve the currently authenticated user's profile.

    Decodes the JWT token, extracts the username, and looks up the
    corresponding user in the database.

    Args:
        token (str): Bearer token extracted from the Authorization header.
        db (Session): Database session dependency.

    Raises:
        HTTPException: 401 if the token is invalid or expired.
        HTTPException: 404 if the user cannot be found in the database.

    Returns:
        schemas.UserOut: The authenticated user's data.
    """
    try:
        payload = auth.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/auth/verify")
def verify(token: str):
    """
    Verify the validity of a token and return its claims.

    Decodes the provided JWT token and returns the subject (username)
    and role encoded within it.

    Args:
        token (str): The JWT token string.

    Raises:
        HTTPException: 401 if the token is invalid.

    Returns:
        dict: A dictionary containing `sub` (username) and `role`.
    """
    try:
        payload = auth.decode_token(token)
        return {"sub": payload.get("sub"), "role": payload.get("role")}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
