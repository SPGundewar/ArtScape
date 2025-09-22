from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import models, schemas, database, auth_utils
from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/artworks", response_model=schemas.ArtworkOut)
def create_artwork(art: schemas.ArtworkCreate, user: dict = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    # Only artist or admin can create artworks
    role = user.get("role")
    if role not in ("artist", "admin"):
        raise HTTPException(status_code=403, detail="Only artists/admins can create artworks")
    owner = user.get("sub")
    new = models.Artwork(title=art.title, description=art.description, price=art.price, owner=owner)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get("/artworks", response_model=list[schemas.ArtworkOut])
def list_artworks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Artwork).offset(skip).limit(limit).all()
    return items

@router.get("/artworks/{art_id}", response_model=schemas.ArtworkOut)
def get_art(art_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Artwork).filter(models.Artwork.id == art_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return item

@router.post("/artworks/{art_id}/mark_sold", response_model=schemas.ArtworkOut)
def mark_sold(art_id: int, user: dict = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    art = db.query(models.Artwork).filter(models.Artwork.id == art_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artwork not found")
    if art.is_sold:
        raise HTTPException(status_code=400, detail="Artwork already sold")
    # For demo: any authenticated user/service can mark sold; authorization logic can be stricter in production
    art.is_sold = True
    db.commit()
    db.refresh(art)
    return art
