# app/models/scene_model.py
from typing import Dict
from app.database import Base
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone


class SceneModel(Base):
    """
    场景数据模型。
    """

    __tablename__ = "scenes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    stories = relationship("StoryModel", back_populates="scene")

    def to_dict(self) -> Dict:
        """
        将模型对象转换为字典。
        """
        return {
            "scene_id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """
        从字典创建模型对象。
        """
        return cls(
            id=data.get("scene_id") or str(uuid.uuid4()),
            name=data.get("name"),
            description=data.get("description"),
            created_at=data.get("created_at"),
        )
