from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routes import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Artwork Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)




# ask gpt to -
# This is intentionally minimal but correct: create artworks, list, get, and mark_sold. 
# For demo authentication, create_artwork expects X-Username header (easier than decoding JWT here).
# You can replace with JWT decode if you want full enforcement. But Orders will call mark_sold 
# without auth in the demo — acceptable for A2. 
# If you prefer, later we can add token verification by decoding JWT using SECRET_KEY.