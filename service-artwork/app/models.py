from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base

class Artwork(Base):
    __tablename__ = "artworks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    owner = Column(String, nullable=False)  # username
    is_sold = Column(Boolean, default=False)
