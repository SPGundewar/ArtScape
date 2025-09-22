from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
from typing import List, Optional

def create_artwork(db: Session, artwork: schemas.ArtworkCreate, artist_id: int):
    db_artwork = models.Artwork(
        **artwork.dict(),
        artist_id=artist_id
    )
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork

def get_artwork(db: Session, artwork_id: int):
    return db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()

def get_artworks(db: Session, skip: int = 0, limit: int = 100, artist_id: Optional[int] = None):
    query = db.query(models.Artwork).filter(models.Artwork.status == models.ArtworkStatus.ACTIVE)
    if artist_id:
        query = query.filter(models.Artwork.artist_id == artist_id)
    return query.offset(skip).limit(limit).all()

def update_artwork(db: Session, artwork_id: int, artwork_update: schemas.ArtworkUpdate, artist_id: int):
    db_artwork = db.query(models.Artwork).filter(
        models.Artwork.id == artwork_id,
        models.Artwork.artist_id == artist_id  # Ensure artist owns the artwork
    ).first()
    
    if db_artwork:
        update_data = artwork_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_artwork, field, value)
        db.commit()
        db.refresh(db_artwork)
    
    return db_artwork

def delete_artwork(db: Session, artwork_id: int, artist_id: int):
    db_artwork = db.query(models.Artwork).filter(
        models.Artwork.id == artwork_id,
        models.Artwork.artist_id == artist_id
    ).first()
    
    if db_artwork:
        db_artwork.status = models.ArtworkStatus.ARCHIVED
        db.commit()
        db.refresh(db_artwork)
    
    return db_artwork

def create_bid(db: Session, bid: schemas.BidCreate, artwork_id: int, bidder_id: int):
    # Check if artwork exists and is auction
    artwork = get_artwork(db, artwork_id)
    if not artwork or not artwork.is_auction or artwork.status != models.ArtworkStatus.ACTIVE:
        return None
    
    # Get highest bid to validate new bid
    highest_bid = get_highest_bid(db, artwork_id)
    min_bid = highest_bid.amount if highest_bid else (artwork.price or 0)
    
    if bid.amount <= min_bid:
        return None
    
    db_bid = models.Bid(
        artwork_id=artwork_id,
        bidder_id=bidder_id,
        amount=bid.amount
    )
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid

def get_bids(db: Session, artwork_id: int):
    return db.query(models.Bid).filter(
        models.Bid.artwork_id == artwork_id
    ).order_by(desc(models.Bid.amount)).all()

def get_highest_bid(db: Session, artwork_id: int):
    return db.query(models.Bid).filter(
        models.Bid.artwork_id == artwork_id
    ).order_by(desc(models.Bid.amount)).first()