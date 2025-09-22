from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import models, schemas, database, auth_utils
from database import SessionLocal
import os, requests

router = APIRouter()
ARTWORK_URL = os.getenv("ARTWORK_SERVICE_URL", "http://artwork:8000")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/orders", response_model=schemas.OrderOut)
def create_order(
    order_in: schemas.OrderCreate, 
    token: str = Depends(auth_utils.oauth2_scheme), 
    user: dict = Depends(auth_utils.get_current_user), 
    db: Session = Depends(get_db)
    ):
    # Only users (not artists) can place orders
    if user.get("role") not in ("user", "admin"):
        raise HTTPException(status_code=403, detail="Only users or admins can place orders")


    # Buyer pulled from token
    buyer = user.get("sub")
    # Check artwork exists and not sold (forward token)
    headers = {"Authorization": f"Bearer {token}"}
    art_resp = requests.get(f"{ARTWORK_URL}/artworks/{order_in.art_id}", headers=headers, timeout=5)
    if art_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Artwork not found")
    art = art_resp.json()
    if art.get("is_sold"):
        raise HTTPException(status_code=400, detail="Artwork already sold")

    # Try to mark it sold (forward token)
    mark_resp = requests.post(f"{ARTWORK_URL}/artworks/{order_in.art_id}/mark_sold", headers=headers, timeout=5)
    if mark_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to reserve artwork")

    # Create order in local DB
    new_order = models.Order(art_id=order_in.art_id, buyer=buyer, status="confirmed")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return o

@router.get("/orders", response_model=list[schemas.OrderOut])
def list_orders(
    token: str = Depends(auth_utils.oauth2_scheme),
    user: dict = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    role = user.get("role")
    username = user.get("sub")

    query = db.query(models.Order)

    if role == "user":
        # users see only their own orders
        query = query.filter(models.Order.buyer == username)
    elif role == "artist":
        # artists see only orders for their artworks
        # need to join with artwork table
        query = query.join(models.Artwork).filter(models.Artwork.owner == username)
    elif role == "admin":
        # admins see everything
        pass

    return query.all()

