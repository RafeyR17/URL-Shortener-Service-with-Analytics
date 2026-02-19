from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.config import settings
from app.db.session import get_db
from app.core.redis import get_redis
from app.db.models import User
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    return user

async def get_url_service(
    db: AsyncSession = Depends(get_db),
    redis: redis.Redis = Depends(get_redis)
):
    from app.services.url_service import URLService
    return URLService(db, redis)

async def get_analytics_service(
    db: AsyncSession = Depends(get_db),
    redis: redis.Redis = Depends(get_redis)
):
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService(db, redis)
