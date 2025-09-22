from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .auth_dependency import verify_token, require_user
from .external_services import get_artwork_details

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ArtScape Commerce Service", 
    description="Wishlist and order management for ArtScape platform",
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
    return {"message": "ArtScape Commerce Service is running"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "commerce"}

# Wishlist endpoints
@app.get("/users/{user_id}/wishlist", response_model=List[schemas.WishlistItemWithArtwork], tags=["Wishlist"])
async def get_user_wishlist(
    user_id: int,
    current_user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get user's wishlist with artwork details"""
    # Ensure user can only access their own wishlist
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    wishlist_items = crud.get_user_wishlist(db, user_id)
    
    # Enrich with artwork details
    enriched_items = []
    for item in wishlist_items:
        artwork_details = await get_artwork_details(item.artwork_id)
        if artwork_details:
            enriched_items.append(schemas.WishlistItemWithArtwork(
                id=item.id,
                artwork_id=item.artwork_id,
                artwork_title=artwork_details["title"],
                artwork_price=artwork_details["price"],
                artwork_image_url=artwork_details["image_url"],
                artist_id=artwork_details["artist_id"],
                created_at=item.created_at
            ))
    
    return enriched_items

@app.post("/users/{user_id}/wishlist/{artwork_id}", response_model=schemas.WishlistItemResponse, tags=["Wishlist"])
async def add_to_wishlist(
    user_id: int,
    artwork_id: int,
    current_user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Add artwork to user's wishlist"""
    # Ensure user can only modify their own wishlist
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify artwork exists
    artwork = await get_artwork_details(artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    wishlist_item = crud.add_to_wishlist(db, user_id, artwork_id)
    if not wishlist_item:
        raise HTTPException(status_code=400, detail="Artwork already in wishlist")
    
    return wishlist_item

@app.delete("/users/{user_id}/wishlist/{artwork_id}", tags=["Wishlist"])
def remove_from_wishlist(
    user_id: int,
    artwork_id: int,
    current_user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Remove artwork from user's wishlist"""
    # Ensure user can only modify their own wishlist
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = crud.remove_from_wishlist(db, user_id, artwork_id)
    if not success:
        raise HTTPException(status_code=404, detail="Artwork not found in wishlist")
    
    return {"message": "Artwork removed from wishlist"}

# Order endpoints  
@app.post("/orders", response_model=schemas.OrderResponse, tags=["Orders"])
async def create_order(
    order: schemas.OrderCreate,
    current_user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Create a new order for artwork purchase"""
    # Get artwork details
    artwork = await get_artwork_details(order.artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    if artwork["status"] == "sold":
        raise HTTPException(status_code=400, detail="Artwork already sold")
    
    # For auction items, use highest bid; for fixed price, use artwork price
    amount = artwork["price"] if artwork["price"] else 0
    if artwork["is_auction"]:
        # In a real system, you'd get the winning bid amount
        # For now, we'll use the artwork's base price
        pass
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid artwork price")
    
    # Create order
    db_order = crud.create_order(
        db=db,
        order=order,
        buyer_id=current_user["user_id"],
        artist_id=artwork["artist_id"],
        amount=amount
    )
    
    return db_order

@app.get("/orders/{order_id}", response_model=schemas.OrderWithDetails, tags=["Orders"])
async def get_order(
    order_id: int,
    current_user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get order details"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Ensure user can only access their own orders
    if order.buyer_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Enrich with artwork details
    artwork = await get_artwork_details(order.artwork_id)
    
    return schemas.OrderWithDetails(
        **order.__dict__,
        artwork_title=artwork["title"] if artwork else "Unknown",
        artwork_image_url=artwork["image_url"] if artwork else None
    )

@app.get("/users/{user_id}/orders", response_model=List[schemas.OrderResponse], tags=["Orders"])
def get_user_orders(
    user_id: int,
    current_user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get all orders for a user"""
    # Ensure user can only access their own orders
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return crud.get_user_orders(db, user_id)