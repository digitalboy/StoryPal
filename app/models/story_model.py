# app/models/story_model.py
from typing import List, Dict, Optional, Union
from app.database import Base
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone


class StoryModel(Base):
    """
    故事数据模型。
    """

    __tablename__ = "stories"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    vocabulary_level = Column(Integer)
    scene_id = Column(String, ForeignKey("scenes.id"), index=True)
    word_count = Column(Integer)
    new_word_rate = Column(Float)
    key_words = Column(JSON)
    unknown_words = Column(JSON)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    scene = relationship("SceneModel", back_populates="stories")

    def to_dict(self) -> Dict:
        """
        将模型对象转换为字典。
        """
        return {
            "story_id": self.id,
            "title": self.title,
            "content": self.content,
            "vocabulary_level": self.vocabulary_level,
            "scene_id": self.scene_id,
            "scene_name": self.scene.name if self.scene else None,
            "word_count": self.word_count,
            "new_word_rate": self.new_word_rate,
            "key_words": self.key_words,
            "unknown_words": self.unknown_words,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """
        从字典创建模型对象。
        """
        return cls(
            id=data.get("story_id") or str(uuid.uuid4()),
            title=data.get("title"),
            content=data.get("content"),
            vocabulary_level=data.get("vocabulary_level"),
            scene_id=data.get("scene_id"),
            word_count=data.get("word_count"),
            new_word_rate=data.get("new_word_rate"),
            key_words=data.get("key_words", []),
            unknown_words=data.get("unknown_words", []),
            created_at=data.get("created_at"),
        )
