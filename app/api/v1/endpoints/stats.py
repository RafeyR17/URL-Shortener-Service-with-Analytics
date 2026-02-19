from fastapi import APIRouter, Depends, HTTPException
from app.schemas import URLStats
from app.core.dependencies import get_analytics_service

router = APIRouter()

@router.get("/stats/{short_code}", response_model=URLStats)
async def get_url_stats(
    short_code: str,
    analytics_service = Depends(get_analytics_service)
):
    stats = await analytics_service.get_stats(short_code)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    return stats
