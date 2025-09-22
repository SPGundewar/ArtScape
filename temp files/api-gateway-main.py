from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="ArtScape API Gateway",
    description="Central API gateway for ArtScape microservices",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
ARTWORK_SERVICE_URL = os.getenv("ARTWORK_SERVICE_URL", "http://localhost:8002") 
COMMERCE_SERVICE_URL = os.getenv("COMMERCE_SERVICE_URL", "http://localhost:8003")

@app.get("/", tags=["Gateway"])
def read_root():
    return {
        "message": "ArtScape API Gateway",
        "services": {
            "auth": f"{AUTH_SERVICE_URL}",
            "artwork": f"{ARTWORK_SERVICE_URL}",
            "commerce": f"{COMMERCE_SERVICE_URL}"
        }
    }

@app.get("/health", tags=["Gateway"])
async def health_check():
    """Check health of all services"""
    services_health = {}
    
    async with httpx.AsyncClient() as client:
        # Check Auth Service
        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/health", timeout=5.0)
            services_health["auth"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_health["auth"] = "unreachable"
        
        # Check Artwork Service
        try:
            response = await client.get(f"{ARTWORK_SERVICE_URL}/health", timeout=5.0)
            services_health["artwork"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_health["artwork"] = "unreachable"
        
        # Check Commerce Service
        try:
            response = await client.get(f"{COMMERCE_SERVICE_URL}/health", timeout=5.0)
            services_health["commerce"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_health["commerce"] = "unreachable"
    
    return {
        "status": "healthy",
        "services": services_health
    }

async def proxy_request(service_url: str, path: str, request: Request):
    """Proxy request to target service"""
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request
            response = await client.request(
                method=request.method,
                url=f"{service_url}{path}",
                headers=dict(request.headers),
                content=await request.body(),
                params=dict(request.query_params),
                timeout=30.0
            )
            
            # Return the response
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timeout")

# Auth Service Routes
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Auth"])
@app.api_route("/register", methods=["POST"], tags=["Auth"])
@app.api_route("/users/{path:path}", methods=["GET", "PUT"], tags=["Auth"])
@app.api_route("/artists/{path:path}", methods=["GET", "PUT"], tags=["Auth"])
async def auth_proxy(request: Request, path: str = ""):
    """Proxy requests to Auth Service"""
    if request.url.path.startswith("/auth/"):
        full_path = request.url.path
    elif request.url.path == "/register":
        full_path = "/register"
    elif request.url.path.startswith("/users/"):
        full_path = request.url.path
    elif request.url.path.startswith("/artists/"):
        full_path = request.url.path
    else:
        full_path = f"/auth/{path}"
    
    return await proxy_request(AUTH_SERVICE_URL, full_path, request)

# Artwork Service Routes
@app.api_route("/artworks/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Artworks"])
@app.api_route("/artworks", methods=["GET", "POST"], tags=["Artworks"])
async def artwork_proxy(request: Request, path: str = ""):
    """Proxy requests to Artwork Service"""
    if path:
        full_path = f"/artworks/{path}"
    else:
        full_path = "/artworks"
    
    return await proxy_request(ARTWORK_SERVICE_URL, full_path, request)

# Commerce Service Routes  
@app.api_route("/users/{user_id}/wishlist/{path:path}", methods=["GET", "POST", "DELETE"], tags=["Commerce"])
@app.api_route("/users/{user_id}/wishlist", methods=["GET"], tags=["Commerce"])
@app.api_route("/users/{user_id}/orders", methods=["GET"], tags=["Commerce"])
@app.api_route("/orders/{path:path}", methods=["GET", "PUT"], tags=["Commerce"])
@app.api_route("/orders", methods=["POST"], tags=["Commerce"])
async def commerce_proxy(request: Request, user_id: int = None, path: str = ""):
    """Proxy requests to Commerce Service"""
    return await proxy_request(COMMERCE_SERVICE_URL, request.url.path, request)