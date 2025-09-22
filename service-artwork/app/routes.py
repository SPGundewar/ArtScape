from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import models, schemas, database, auth_utils
from database import SessionLocal

router = APIRouter()

def get_db():
    """
    Dependency that provides a SQLAlchemy database session.

    Yields:
        Session: A SQLAlchemy session connected to the configured database.
    Ensures:
        The session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/artworks", response_model=schemas.ArtworkOut)
def create_artwork(
    art: schemas.ArtworkCreate,
    user: dict = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new artwork in the system.

    Only users with role `artist` or `admin` are allowed to create artworks.
    The owner of the artwork is automatically set from the authenticated user.

    Args:
        art (schemas.ArtworkCreate): Artwork creation payload including title, description, and price.
        user (dict): The authenticated user payload decoded from the token.
        db (Session): Database session.

    Raises:
        HTTPException: 403 if the authenticated user is not an artist or admin.

    Returns:
        schemas.ArtworkOut: The newly created artwork record.
    """
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
    """
    Retrieve a paginated list of artworks.

    Args:
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        db (Session): Database session.

    Returns:
        list[schemas.ArtworkOut]: A list of artworks stored in the database.
    """
    items = db.query(models.Artwork).offset(skip).limit(limit).all()
    return items

@router.get("/artworks/{art_id}", response_model=schemas.ArtworkOut)
def get_art(art_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single artwork by its ID.

    Args:
        art_id (int): The ID of the artwork to retrieve.
        db (Session): Database session.

    Raises:
        HTTPException: 404 if the artwork is not found.

    Returns:
        schemas.ArtworkOut: The artwork record.
    """
    item = db.query(models.Artwork).filter(models.Artwork.id == art_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return item

@router.post("/artworks/{art_id}/mark_sold", response_model=schemas.ArtworkOut)
def mark_sold(
    art_id: int,
    user: dict = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an artwork as sold.

    Any authenticated user may perform this operation (demo logic).
    In production, this should be restricted to authorized roles or services.

    Args:
        art_id (int): The ID of the artwork to mark as sold.
        user (dict): The authenticated user payload decoded from the token.
        db (Session): Database session.

    Raises:
        HTTPException: 404 if the artwork is not found.
        HTTPException: 400 if the artwork is already sold.

    Returns:
        schemas.ArtworkOut: The updated artwork record with `is_sold=True`.
    """
    art = db.query(models.Artwork).filter(models.Artwork.id == art_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artwork not found")
    if art.is_sold:
        raise HTTPException(status_code=400, detail="Artwork already sold")
    art.is_sold = True
    db.commit()
    db.refresh(art)
    return art
