from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=50)
    expire_days: Optional[int] = Field(None, ge=1, le=365)

class URLCreate(URLBase):
    pass

class URLResponse(BaseModel):
    short_code: str
    original_url: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class URLStats(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    created_at: datetime
