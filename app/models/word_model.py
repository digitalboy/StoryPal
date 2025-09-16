# app/models/word_model.py
from typing import List, Dict, Optional
from app.database import Base
from sqlalchemy import Column, String, Integer, Float, DateTime
import uuid
from datetime import datetime, timezone


class WordModel(Base):
    """
    词语数据模型。
    """

    __tablename__ = "words"

    id = Column(String, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    chaotong_level = Column(Integer)
    hsk_level = Column(Float)
    part_of_speech = Column(String)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> Dict:
        """
        将模型对象转换为字典。
        """
        return {
            "word_id": self.id,
            "word": self.word,
            "chaotong_level": self.chaotong_level,
            "hsk_level": self.hsk_level,
            "part_of_speech": self.part_of_speech,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """
        从字典创建模型对象。
        """
        chaotong_level = data.get("chaotong_level")
        if chaotong_level is not None:
            try:
                chaotong_level = int(chaotong_level)
            except (ValueError, TypeError):
                chaotong_level = None  # 或者设置默认值，或者抛出异常
        return cls(
            id=data.get("word_id") or str(uuid.uuid4()),
            word=data.get("word"),
            chaotong_level=chaotong_level,
            hsk_level=data.get("hsk_level"),
            part_of_speech=data.get("part_of_speech"),
            created_at=data.get("created_at"),
        )
