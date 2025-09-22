from sqlalchemy import Column, Integer, String
from database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    art_id = Column(Integer, nullable=False)
    buyer = Column(String, nullable=False)
    status = Column(String, default="created")  # created | confirmed | failed
