# app/models/original_story_model.py
from app.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime, timezone

class OriginalStoryModel(Base):
    """
    用于存储从外部 API 获取的旧有故事的原始数据。
    """

    __tablename__ = "original_stories"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    level = Column(Integer)
    content = Column(Text)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
