# 🎨 ArtScape Microservices Platform

A lightweight **digital art marketplace** built with **microservices architecture**.
This demo showcases secure authentication, role-based authorization, and inter-service communication using **FastAPI + SQLite + Docker Compose**.

---

## 🏗️ Architecture Overview

* **🔐 Auth Service** (Port 8001)
  User registration, login, and JWT token management

* **🖼️ Artwork Service** (Port 8002)
  Artwork creation, listing, and ownership management

* **🛒 Orders Service** (Port 8003)
  Order placement and retrieval with role-based visibility

* **🌐 (Optional) API Gateway**
  Can be extended for centralized routing

Each service has its **own database**, following the **database-per-service** pattern.

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run all services
docker compose up --build -d

# Seed demo data (users + artworks)
docker compose run --rm auth python -m app.seed
docker compose run --rm artwork python -m app.seed
```

➡ Swagger UIs:

* Auth → [http://localhost:8001/docs](http://localhost:8001/docs)
* Artwork → [http://localhost:8002/docs](http://localhost:8002/docs)
* Orders → [http://localhost:8003/docs](http://localhost:8003/docs)

---

### Option 2: Local Development

```bash
# Setup environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run each service separately
cd service-auth && uvicorn main:app --port 8001 --reload
cd service-artwork && uvicorn main:app --port 8002 --reload
cd service-orders && uvicorn main:app --port 8003 --reload
```

---

## 📋 API Documentation

* **Auth Service** → [http://localhost:8001/docs](http://localhost:8001/docs)
* **Artwork Service** → [http://localhost:8002/docs](http://localhost:8002/docs)
* **Orders Service** → [http://localhost:8003/docs](http://localhost:8003/docs)

Each service has its own OpenAPI/Swagger documentation.

---

## 🧪 Demo Workflow

### 1. Register a User (Artist)

```bash
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"artist1","password":"pass","role":"artist"}'
```

### 2. Login & Get Token

```bash
curl -X POST "http://localhost:8001/auth/token" \
  -F "username=artist1" -F "password=pass"
```

➡ Copy the `access_token`.

### 3. Create Artwork

```bash
curl -X POST "http://localhost:8002/artworks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Sunset","description":"Beautiful","price":100.0}'
```

### 4. Place Order (as a User)

```bash
curl -X POST "http://localhost:8003/orders" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"art_id":1}'
```

### 5. Verify Results

```bash
# Artwork should now show as sold
curl http://localhost:8002/artworks/1

# Orders visible for the user
curl http://localhost:8003/orders
```

---

## 📊 Database Schema

* **auth.db** → Users, credentials, roles
* **artwork.db** → Artworks, ownership, sold flag
* **orders.db** → Orders, buyer references, status

---

## 🔒 Security Features

* JWT-based authentication (`HS256`)
* Role-based access control (`user`, `artist`, `admin`)
* Token forwarding between services
* CORS enabled for UI integration

---

## 🎯 Assignment A2 Compliance

✅ **Three+ Microservices** implemented
✅ **Inter-service Communication** via HTTP APIs
✅ **Role-based Access Control** (artist, user, admin)
✅ **Swagger UI** for each service (TA demo-ready)
✅ **Dockerized** for simple startup and reproducibility

---

## 📈 Scalability & Extensions

* Stateless services → scalable horizontally
* Database-per-service → clear ownership boundaries
* Extendable with API Gateway & load balancing
* Could integrate **auctions, bidding, payments** in future iterations

---

✨ ArtScape demonstrates a **clean microservices pattern** with minimal setup, while being extensible enough to evolve into a production-ready marketplace.

---

flowchart LR
    Client[👩‍💻 Client/UI] -->|Login / Register| Auth[🔐 Auth Service]
    Client -->|Browse / Buy| Artwork[🖼️ Artwork Service]
    Client -->|Place Order| Orders[🛒 Orders Service]

    Orders -->|Verify Artwork| Artwork
    Orders -->|Decode & Verify Token| Auth


flowchart TB
    subgraph AuthService[🔐 Auth Service]
        AuthDB[(auth.db)]
    end

    subgraph ArtworkService[🖼️ Artwork Service]
        ArtworkDB[(artwork.db)]
    end

    subgraph OrdersService[🛒 Orders Service]
        OrdersDB[(orders.db)]
    end

    Client[👩‍💻 Client/UI] --> AuthService
    Client --> ArtworkService
    Client --> OrdersService

    OrdersService --> ArtworkService
    OrdersService --> AuthService

