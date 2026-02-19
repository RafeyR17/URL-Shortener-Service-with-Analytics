from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import URL, Click
import redis.asyncio as redis

class AnalyticsService:
    def __init__(self, db: AsyncSession, redis: redis.Redis):
        self.db = db
        self.redis = redis

    async def record_click(
        self, 
        short_code: str, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None
    ):
        # Atomic counter in Redis
        await self.redis.incr(f"clicks:{short_code}")
        
        # We find the URL id to record a detailed click in Postgres
        # This part could be moved to a background task for higher performance
        stmt = select(URL.id).where(URL.short_code == short_code)
        result = await self.db.execute(stmt)
        url_id = result.scalar_one_or_none()
        
        if url_id:
            click = Click(
                url_id=url_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                timestamp=datetime.utcnow()
            )
            self.db.add(click)
            await self.db.commit()

    async def get_stats(self, short_code: str):
        # Get total clicks from Redis or DB
        redis_clicks = await self.redis.get(f"clicks:{short_code}")
        
        stmt = select(URL).where(URL.short_code == short_code)
        result = await self.db.execute(stmt)
        url_obj = result.scalar_one_or_none()
        
        if not url_obj:
            return None
        
        # If redis clicks is none, count from DB
        total_clicks = int(redis_clicks) if redis_clicks else 0
        if not redis_clicks:
             count_stmt = select(func.count(Click.id)).where(Click.url_id == url_obj.id)
             count_res = await self.db.execute(count_stmt)
             total_clicks = count_res.scalar_one()

        return {
            "short_code": short_code,
            "original_url": url_obj.original_url,
            "total_clicks": total_clicks,
            "created_at": url_obj.created_at
        }
