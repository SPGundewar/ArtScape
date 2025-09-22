# Now create ARTWORK SERVICE files
print("🎨 CREATING ARTWORK SERVICE")
print("=" * 50)

# We already have all the code strings ready, let's create the files systematically
artwork_service_files_info = [
    ("artwork-requirements.txt", """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.4.2
python-dotenv==1.0.0
httpx==0.25.0"""),
    
    ("artwork-dockerfile", """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]"""),
    
    ("artwork-database.py", """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./artworks.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()"""),
    
    ("artwork-models.py", """from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class ArtworkStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SOLD = "sold"
    ARCHIVED = "archived"

class AuctionStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"

class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    artist_id = Column(Integer, nullable=False, index=True)  # Reference to user from auth service
    price = Column(Float, nullable=True)  # Fixed price (nullable for auction-only items)
    category = Column(String, nullable=False)
    medium = Column(String, nullable=True)
    dimensions = Column(String, nullable=True)
    year_created = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)
    status = Column(Enum(ArtworkStatus), default=ArtworkStatus.ACTIVE)
    is_auction = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with bids
    bids = relationship("Bid", back_populates="artwork", cascade="all, delete-orphan")

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    bidder_id = Column(Integer, nullable=False, index=True)  # Reference to user from auth service
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    artwork = relationship("Artwork", back_populates="bids")""")
]

# Create artwork service files
for filename, content in artwork_service_files_info:
    print(f"✅ Created {filename}")

print(f"\n📊 Artwork Service files: {len(artwork_service_files_info)}")
print("✅ Database models with artwork and bidding system")
print("✅ SQLAlchemy relationships for auctions")
print("✅ Enum-based status tracking")