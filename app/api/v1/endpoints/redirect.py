from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from app.core.dependencies import get_url_service, get_analytics_service

router = APIRouter()

@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    url_service = Depends(get_url_service),
    analytics_service = Depends(get_analytics_service)
):
    original_url = await url_service.get_original_url(short_code)
    
    if not original_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Record analytics in background
    background_tasks.add_task(
        analytics_service.record_click,
        short_code=short_code,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer")
    )
    
    return RedirectResponse(url=original_url, status_code=307)
