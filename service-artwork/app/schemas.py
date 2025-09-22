from pydantic import BaseModel

class ArtworkCreate(BaseModel):
    title: str
    description: str | None = None
    price: float

class ArtworkOut(BaseModel):
    id: int
    title: str
    description: str | None
    price: float
    owner: str
    is_sold: bool

    class Config:
        orm_mode = True
