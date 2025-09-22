# ArtScape Microservices Platform

A comprehensive digital art marketplace built with microservices architecture, connecting art enthusiasts with artists through secure transactions and auctions.

## 🏗️ Architecture Overview

- **Auth Service** (Port 8001): User authentication, registration, and JWT token management
- **Artwork Service** (Port 8002): Artwork management, auctions, and bidding system
- **Commerce Service** (Port 8003): Wishlist management and order processing
- **API Gateway** (Port 8000): Centralized request routing and service orchestration

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Build and run all services
docker-compose up --build

# Access the application
open http://localhost:8000/docs
```

### Option 2: Local Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and run services (each in separate terminal)
cd auth-service && pip install -r requirements.txt && uvicorn app.main:app --port 8001 --reload
cd artwork-service && pip install -r requirements.txt && uvicorn app.main:app --port 8002 --reload
cd commerce-service && pip install -r requirements.txt && uvicorn app.main:app --port 8003 --reload
cd api-gateway && pip install -r requirements.txt && uvicorn app.main:app --port 8000 --reload
```

## 📋 API Documentation

- **Main Gateway**: http://localhost:8000/docs
- **Auth Service**: http://localhost:8001/docs
- **Artwork Service**: http://localhost:8002/docs
- **Commerce Service**: http://localhost:8003/docs

## 🧪 Testing Workflow

### 1. Register Artist
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist1",
    "email": "artist@artscape.com",
    "full_name": "Van Gogh",
    "password": "securepass123",
    "role": "artist",
    "bio": "Post-impressionist painter"
  }'
```

### 2. Login & Get Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist1",
    "password": "securepass123"
  }'
```

### 3. Create Artwork
```bash
curl -X POST "http://localhost:8000/artworks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Starry Night Redux",
    "description": "A modern take on the classic",
    "price": 1500.00,
    "category": "painting",
    "medium": "oil on canvas"
  }'
```

## 🎯 Assignment A2 Compliance

✅ **Three+ Microservices**: 4 services implemented  
✅ **Inter-service Communication**: Services communicate via HTTP APIs  
✅ **Consistent with A1**: All user stories and API design implemented  
✅ **Live Demonstration**: Swagger UI ready for TA presentation  
✅ **Technology Stack**: FastAPI + SQLite chosen for efficiency  

## 📊 Database Schema

Each service maintains its own database:
- **auth.db**: Users, artists, authentication data
- **artworks.db**: Artworks, bids, auction data
- **commerce.db**: Wishlist items, orders, transactions

## 🏛️ Service Communication Flow

```
Client → API Gateway → Auth Service (token verification)
                   → Artwork Service (artwork operations)
                   → Commerce Service (wishlist/orders)
```

Commerce Service → Artwork Service (artwork details)
All Services → Auth Service (authentication)

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (User/Artist/Admin)
- Service-to-service authentication
- Input validation and sanitization

## 📈 Scalability Considerations

- Stateless services for horizontal scaling
- Database per service pattern
- API Gateway for load balancing potential
- Docker containers for deployment flexibility