from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .models import ArtworkStatus

class ArtworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: str
    medium: Optional[str] = None
    dimensions: Optional[str] = None
    year_created: Optional[int] = None
    image_url: Optional[str] = None
    is_auction: bool = False

class ArtworkCreate(ArtworkBase):
    pass

class ArtworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    medium: Optional[str] = None
    dimensions: Optional[str] = None
    year_created: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[ArtworkStatus] = None

class ArtworkResponse(ArtworkBase):
    id: int
    artist_id: int
    status: ArtworkStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BidCreate(BaseModel):
    amount: float

class BidResponse(BaseModel):
    id: int
    artwork_id: int
    bidder_id: int
    amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class ArtworkWithBids(ArtworkResponse):
    bids: List[BidResponse] = []