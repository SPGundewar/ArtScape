import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database, auth, utils
from .database import SessionLocal, engine
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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
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
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth.create_access_token(subject=user.username, data={"role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserOut)
def read_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    try:
        payload = auth.decode_token(token)
        return {"sub": payload.get("sub"), "role": payload.get("role")}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
