from pydantic import BaseModel

class OrderCreate(BaseModel):
    art_id: int

class OrderOut(BaseModel):
    id: int
    art_id: int
    buyer: str
    status: str

    class Config:
        orm_mode = True
