from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .auth_dependency import verify_token, require_artist, require_user

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ArtScape Artwork Service",
    description="Artwork management and auction system for ArtScape platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "ArtScape Artwork Service is running"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "artwork"}

@app.post("/artworks", response_model=schemas.ArtworkResponse, tags=["Artworks"])
def create_artwork(
    artwork: schemas.ArtworkCreate,
    current_user: dict = Depends(require_artist),
    db: Session = Depends(get_db)
):
    """Create a new artwork (artist only)"""
    return crud.create_artwork(db=db, artwork=artwork, artist_id=current_user["user_id"])

@app.get("/artworks", response_model=List[schemas.ArtworkResponse], tags=["Artworks"])
def get_artworks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    artist_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all active artworks"""
    return crud.get_artworks(db=db, skip=skip, limit=limit, artist_id=artist_id)

@app.get("/artworks/{artwork_id}", response_model=schemas.ArtworkResponse, tags=["Artworks"])
def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Get specific artwork by ID"""
    artwork = crud.get_artwork(db=db, artwork_id=artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork

@app.put("/artworks/{artwork_id}", response_model=schemas.ArtworkResponse, tags=["Artworks"])
def update_artwork(
    artwork_id: int,
    artwork_update: schemas.ArtworkUpdate,
    current_user: dict = Depends(require_artist),
    db: Session = Depends(get_db)
):
    """Update artwork (artist only, own artworks)"""
    artwork = crud.update_artwork(
        db=db, 
        artwork_id=artwork_id, 
        artwork_update=artwork_update,
        artist_id=current_user["user_id"]
    )
    if not artwork:
        raise HTTPException(
            status_code=404, 
            detail="Artwork not found or access denied"
        )
    return artwork

@app.delete("/artworks/{artwork_id}", response_model=schemas.ArtworkResponse, tags=["Artworks"])
def delete_artwork(
    artwork_id: int,
    current_user: dict = Depends(require_artist),
    db: Session = Depends(get_db)
):
    """Archive artwork (artist only, own artworks)"""
    artwork = crud.delete_artwork(
        db=db, 
        artwork_id=artwork_id, 
        artist_id=current_user["user_id"]
    )
    if not artwork:
        raise HTTPException(
            status_code=404, 
            detail="Artwork not found or access denied"
        )
    return artwork

@app.post("/artworks/{artwork_id}/bids", response_model=schemas.BidResponse, tags=["Auctions"])
def create_bid(
    artwork_id: int,
    bid: schemas.BidCreate,
    current_user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Place a bid on an artwork auction"""
    db_bid = crud.create_bid(
        db=db, 
        bid=bid, 
        artwork_id=artwork_id, 
        bidder_id=current_user["user_id"]
    )
    if not db_bid:
        raise HTTPException(
            status_code=400, 
            detail="Invalid bid: artwork not found, not an auction, or bid too low"
        )
    return db_bid

@app.get("/artworks/{artwork_id}/bids", response_model=List[schemas.BidResponse], tags=["Auctions"])
def get_bids(artwork_id: int, db: Session = Depends(get_db)):
    """Get all bids for an artwork (highest first)"""
    # Verify artwork exists
    artwork = crud.get_artwork(db=db, artwork_id=artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    return crud.get_bids(db=db, artwork_id=artwork_id)

# Internal endpoint for other services
@app.get("/internal/artworks/{artwork_id}", response_model=schemas.ArtworkResponse, tags=["Internal"])
def get_artwork_internal(artwork_id: int, db: Session = Depends(get_db)):
    """Internal endpoint for other services to get artwork details"""
    artwork = crud.get_artwork(db=db, artwork_id=artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork