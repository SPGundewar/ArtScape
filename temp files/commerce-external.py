import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

ARTWORK_SERVICE_URL = os.getenv("ARTWORK_SERVICE_URL", "http://localhost:8002")

async def get_artwork_details(artwork_id: int):
    """Get artwork details from artwork service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ARTWORK_SERVICE_URL}/internal/artworks/{artwork_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch artwork details"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Artwork service unavailable"
        )