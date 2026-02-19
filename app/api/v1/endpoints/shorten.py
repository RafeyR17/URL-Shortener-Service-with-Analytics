from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from app.schemas import URLCreate, URLResponse
from app.core.dependencies import get_url_service
from app.core.config import settings

router = APIRouter()

@router.post("/shorten", response_model=URLResponse)
async def shorten_url(
    url_data: URLCreate,
    url_service = Depends(get_url_service)
):
    expires_at = None
    if url_data.expire_days:
        expires_at = datetime.utcnow() + timedelta(days=url_data.expire_days)
    
    try:
        db_url = await url_service.create_url(
            original_url=str(url_data.original_url),
            custom_alias=url_data.custom_alias,
            expires_at=expires_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return URLResponse(
        short_code=db_url.short_code,
        original_url=db_url.original_url,
        short_url=f"{settings.BASE_URL}/{db_url.short_code}",
        created_at=db_url.created_at,
        expires_at=db_url.expires_at
    )
