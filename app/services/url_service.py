import string
import random
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import URL
import redis.asyncio as redis

class URLService:
    BASE62_ALPHABET = string.ascii_letters + string.digits

    def __init__(self, db: AsyncSession, redis: redis.Redis):
        self.db = db
        self.redis = redis

    async def generate_short_code(self, length: int = 6) -> str:
        while True:
            code = "".join(random.choices(self.BASE62_ALPHABET, k=length))
            # Check if code already exists in DB
            stmt = select(URL).where(URL.short_code == code)
            result = await self.db.execute(stmt)
            if not result.scalar_one_or_none():
                return code

    async def create_url(
        self, 
        original_url: str, 
        custom_alias: Optional[str] = None, 
        user_id: Optional[int] = None,
        expires_at: Optional[datetime] = None
    ) -> URL:
        if custom_alias:
            # Check if alias exists
            stmt = select(URL).where(URL.custom_alias == custom_alias)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise ValueError("Custom alias already in use")
            short_code = custom_alias
        else:
            short_code = await self.generate_short_code()

        db_url = URL(
            short_code=short_code,
            original_url=original_url,
            custom_alias=custom_alias if custom_alias else None,
            user_id=user_id,
            expires_at=expires_at
        )
        self.db.add(db_url)
        await self.db.commit()
        await self.db.refresh(db_url)
        
        # Cache in Redis
        await self.redis.setex(
            f"url:{short_code}", 
            3600, # Cache for 1 hour by default or until expiry
            original_url
        )
        
        return db_url

    async def get_original_url(self, short_code: str) -> Optional[str]:
        # Try Cache First
        cached_url = await self.redis.get(f"url:{short_code}")
        if cached_url:
            return cached_url
        
        # Try DB
        stmt = select(URL).where(URL.short_code == short_code)
        result = await self.db.execute(stmt)
        url_obj = result.scalar_one_or_none()
        
        if url_obj:
            # Cache it
            await self.redis.setex(f"url:{short_code}", 3600, url_obj.original_url)
            return url_obj.original_url
        
        return None
