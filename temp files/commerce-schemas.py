from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .models import OrderStatus

# Wishlist schemas
class WishlistItemResponse(BaseModel):
    id: int
    user_id: int
    artwork_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WishlistItemWithArtwork(BaseModel):
    id: int
    artwork_id: int
    artwork_title: str
    artwork_price: Optional[float]
    artwork_image_url: Optional[str]
    artist_id: int
    created_at: datetime

# Order schemas
class OrderCreate(BaseModel):
    artwork_id: int
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = "credit_card"

class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    artwork_id: int
    artist_id: int
    amount: float
    status: OrderStatus
    shipping_address: Optional[str]
    payment_method: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class OrderWithDetails(OrderResponse):
    artwork_title: str
    artwork_image_url: Optional[str]