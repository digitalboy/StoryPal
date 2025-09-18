# app/services/original_story_service.py
import logging
from typing import List, Optional

from app.database import SessionLocal
from app.models.original_story_model import OriginalStoryModel


class OriginalStoryService:
    """
    旧有故事服务，提供与数据库交互的旧有故事相关业务逻辑。
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("OriginalStoryService initialized to work with the database.")

    def get_story_by_id(self, story_id: str) -> Optional[OriginalStoryModel]:
        """
        根据ID从数据库获取旧有故事。
        """
        db = SessionLocal()
        try:
            return (
                db.query(OriginalStoryModel)
                .filter(OriginalStoryModel.id == story_id)
                .first()
            )
        finally:
            db.close()

    def get_stories_by_level(
        self,
        level: int,
        page: int = 1,
        page_size: int = 10,
    ) -> List[OriginalStoryModel]:
        """
        根据级别从数据库获取旧有故事列表，支持分页。
        """
        db = SessionLocal()
        try:
            query = db.query(OriginalStoryModel).filter(
                OriginalStoryModel.level == level
            )
            return (
                query.order_by(OriginalStoryModel.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
        finally:
            db.close()

    def get_total_stories_by_level(self, level: int) -> int:
        """
        根据级别获取旧有故事总数。
        """
        db = SessionLocal()
        try:
            return (
                db.query(OriginalStoryModel)
                .filter(OriginalStoryModel.level == level)
                .count()
            )
        finally:
            db.close()
