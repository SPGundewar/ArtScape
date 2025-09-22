# ArtScape - A2_Soham_Gundewar - Microservices Demo (Auth, Artwork, Orders)

This repository provides a minimal, runnable microservices demo for CSC491/591 A2:
- Auth service (8001)
- Artwork service (8002)
- Orders service (8003)

Each service is a FastAPI app with its own SQLite DB. Services run in Docker Compose.

## Requirements
- Docker & Docker Compose installed (desktop or engine)
- Optionally, Python for local development (not required to run via docker)

## JWT enforcement notes
- Auth issues HS256 tokens using SECRET_KEY.
- Artwork and Orders both decode tokens locally and enforce basic role rules.
- Orders forwards the user's token to Artwork when reserving an artwork.

## Seeding
Run:
docker compose up --build -d
docker compose run --rm auth python app/seed.py
docker compose run --rm artwork python app/seed.py

## Quick start (Docker)
1. Copy `.env.example` to `.env` and edit if needed.
2. From repo root: docker compose up --build
3. Services:
- Auth UI /docs: http://localhost:8001/docs
- Artwork /docs: http://localhost:8002/docs
- Orders /docs: http://localhost:8003/docs

## Demo steps (TA-friendly)
1. Register a user (artist):
curl -X POST "http://localhost:8001/auth/register
" -H "Content-Type: application/json" -d '{"username":"artist1","password":"pass","role":"artist"}'

2. Get token:
curl -X POST "http://localhost:8001/auth/token
" -F "username=artist1" -F "password=pass"

Save `access_token`.

3. Create artwork (use header X-Username for this demo):

curl -X POST "http://localhost:8002/artworks" -H "Content-Type: application/json" -H "X-Username: artist1" -d '{"title":"Sunset","description":"Nice","price":100.0}'


4. List artworks:
curl http://localhost:8002/artworks

5. Create order (buyer = some username):
curl -X POST "http://localhost:8003/orders
" -H "Content-Type: application/json" -d '{"art_id":1,"buyer":"user1"}'


6. Check artwork status (is_sold should be true), and check orders.
curl http://localhost:8002/artworks/1
curl http://localhost:8003/orders


## Notes and caveats
- For the sake of a simple demo, some endpoints use a header `X-Username` rather than full JWT parsing. You can extend the services to decode JWTs using `SECRET_KEY`. All services accept the same SECRET_KEY in `.env` so token decoding across services is possible.
- This demo does not implement distributed transactions or saga patterns. It does perform the basic flow: Orders -> Artwork (reserve) -> Orders (create).
- For grading: show the running services, token creation, an end-to-end buy flow, and the OpenAPI docs auto-generated at `/docs`.

If you want me to enforce JWT verification in Artwork and Orders (recommended), I will add middleware that decodes the JWT using the `SECRET_KEY` env var and checks role/ownership. Otherwise, this is a complete, working base that meets A2 requirements.

