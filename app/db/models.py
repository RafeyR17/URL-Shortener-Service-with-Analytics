from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    urls: Mapped[List["URL"]] = relationship(back_populates="owner")

class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    original_url: Mapped[str] = mapped_column(Text)
    custom_alias: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    owner: Mapped[Optional["User"]] = relationship(back_populates="urls")
    clicks: Mapped[List["Click"]] = relationship(back_populates="url", cascade="all, delete-orphan")

class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url_id: Mapped[int] = mapped_column(ForeignKey("urls.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    referrer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    url: Mapped["URL"] = relationship(back_populates="clicks")

# Index for analytics queries
Index("ix_clicks_url_timestamp", Click.url_id, Click.timestamp)
