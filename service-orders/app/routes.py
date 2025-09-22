from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import models, schemas, database, auth_utils
from database import SessionLocal
import os, requests

router = APIRouter()
ARTWORK_URL = os.getenv("ARTWORK_SERVICE_URL", "http://artwork:8000")

def get_db():
    """
    Dependency that provides a SQLAlchemy database session.

    Yields:
        Session: A SQLAlchemy session connected to the orders database.
    Ensures:
        The session is closed after use.
    """
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
    """
    Create a new order for an artwork.

    Only users with role `user` or `admin` may place orders. The buyer
    is automatically taken from the authenticated token. The function
    verifies that the artwork exists and is not already sold by calling
    the artwork service, and then attempts to mark the artwork as sold.

    Args:
        order_in (schemas.OrderCreate): The incoming order request payload containing the artwork ID.
        token (str): OAuth2 token for authenticating against the artwork service.
        user (dict): Authenticated user information from the token.
        db (Session): Database session.

    Raises:
        HTTPException: 403 if the user role is not permitted to place orders.
        HTTPException: 400 if the artwork does not exist, is already sold, or marking as sold fails.

    Returns:
        schemas.OrderOut: The newly created order record with status "confirmed".
    """
    if user.get("role") not in ("user", "admin"):
        raise HTTPException(status_code=403, detail="Only users or admins can place orders")

    buyer = user.get("sub")
    headers = {"Authorization": f"Bearer {token}"}

    # Validate artwork
    art_resp = requests.get(f"{ARTWORK_URL}/artworks/{order_in.art_id}", headers=headers, timeout=5)
    if art_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Artwork not found")
    art = art_resp.json()
    if art.get("is_sold"):
        raise HTTPException(status_code=400, detail="Artwork already sold")

    # Mark artwork as sold
    mark_resp = requests.post(f"{ARTWORK_URL}/artworks/{order_in.art_id}/mark_sold", headers=headers, timeout=5)
    if mark_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to reserve artwork")

    # Create order in DB
    new_order = models.Order(art_id=order_in.art_id, buyer=buyer, status="confirmed")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an order by its ID.

    Args:
        order_id (int): The ID of the order to retrieve.
        db (Session): Database session.

    Raises:
        HTTPException: 404 if the order does not exist.

    Returns:
        models.Order: The order record.
    """
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
    """
    Retrieve a list of orders, filtered by the role of the authenticated user.

    Behavior by role:
        - user: Sees only their own orders.
        - artist: Sees orders for artworks they own. Ownership is resolved by calling the artwork service.
        - admin: Sees all orders.

    Args:
        token (str): OAuth2 token used for authorization when querying the artwork service.
        user (dict): The authenticated user payload, containing role and username.
        db (Session): Database session.

    Raises:
        HTTPException: 400 if the artwork service fails when fetching artist-owned artworks.

    Returns:
        list[schemas.OrderOut]: A list of orders visible to the user according to their role.
    """
    role = user.get("role")
    username = user.get("sub")

    query = db.query(models.Order)

    if role == "user":
        return query.filter(models.Order.buyer == username).all()
    
    elif role == "artist":
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{ARTWORK_URL}/artworks", headers=headers, timeout=5)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch artworks")

        artworks = resp.json()
        artist_art_ids = [a["id"] for a in artworks if a["owner"] == username]
        return query.filter(models.Order.art_id.in_(artist_art_ids)).all()
        
    elif role == "admin":
        return query.all()

    return []
