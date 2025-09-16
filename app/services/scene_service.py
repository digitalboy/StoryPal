# app/services/scene_service.py
import logging
from typing import List, Optional
import uuid

from sqlalchemy import or_
from app.database import SessionLocal
from app.models.scene_model import SceneModel


class SceneService:
    """
    场景服务，提供与数据库交互的场景相关业务逻辑。
    """

    def __init__(self):
        """
        初始化场景服务。
        现在，它不再从 JSON 文件加载数据，而是按需与数据库交互。
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("SceneService initialized to work with the database.")

    def get_scene_by_id(self, scene_id: str) -> SceneModel | None:
        """
        根据ID从数据库获取场景信息。
        """
        db = SessionLocal()
        try:
            return db.query(SceneModel).filter(SceneModel.id == scene_id).first()
        finally:
            db.close()

    def get_all_scenes(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[SceneModel]:
        """
        从数据库获取所有场景，支持按名称和描述进行模糊搜索和分页。
        """
        db = SessionLocal()
        try:
            query = db.query(SceneModel)
            filters = []
            if name:
                filters.append(SceneModel.name.ilike(f"%{name}%"))
            if description:
                filters.append(SceneModel.description.ilike(f"%{description}%"))

            if filters:
                query = query.filter(or_(*filters))

            return (
                query.order_by(SceneModel.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
        finally:
            db.close()

    def get_total_scenes(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> int:
        """
        获取场景总数，支持按名称和描述进行模糊搜索。
        """
        db = SessionLocal()
        try:
            query = db.query(SceneModel)
            filters = []
            if name:
                filters.append(SceneModel.name.ilike(f"%{name}%"))
            if description:
                filters.append(SceneModel.description.ilike(f"%{description}%"))

            if filters:
                query = query.filter(or_(*filters))
            return query.count()
        finally:
            db.close()

    def create_scene(self, name: str, description: str) -> SceneModel:
        """
        在数据库中创建新场景。
        """
        db = SessionLocal()
        try:
            # 检查场景名称是否已存在
            existing_scene = (
                db.query(SceneModel).filter(SceneModel.name == name).first()
            )
            if existing_scene:
                self.logger.warning(
                    f"Scene with name '{name}' already exists with ID {existing_scene.id}. Returning existing scene."
                )
                return existing_scene

            new_scene = SceneModel(
                id=str(uuid.uuid4()), name=name, description=description
            )
            db.add(new_scene)
            db.commit()
            db.refresh(new_scene)
            self.logger.info(
                f"Created new scene in DB: ID={new_scene.id}, Name='{name}'"
            )
            return new_scene
        finally:
            db.close()

    def update_scene(
        self, scene_id: str, name: str, description: str
    ) -> SceneModel | None:
        """
        更新数据库中的场景信息。
        """
        db = SessionLocal()
        try:
            scene = db.query(SceneModel).filter(SceneModel.id == scene_id).first()
            if scene:
                scene.name = name
                scene.description = description
                db.commit()
                db.refresh(scene)
                self.logger.info(f"Updated scene in DB: ID={scene.id}")
                return scene
            return None
        finally:
            db.close()

    def delete_scene(self, scene_id: str) -> bool:
        """
        从数据库删除场景。
        """
        db = SessionLocal()
        try:
            scene = db.query(SceneModel).filter(SceneModel.id == scene_id).first()
            if scene:
                db.delete(scene)
                db.commit()
                self.logger.info(f"Deleted scene from DB: ID={scene_id}")
                return True
            return False
        finally:
            db.close()

    def find_scene_by_name(self, name: str) -> SceneModel | None:
        """
        根据名称从数据库查找场景。
        """
        db = SessionLocal()
        try:
            return db.query(SceneModel).filter(SceneModel.name == name).first()
        finally:
            db.close()

    def find_or_create_scene(
        self, name: str, description: str = "由 AI 生成"
    ) -> SceneModel:
        """
        根据名称查找场景，如果不存在则在数据库中创建新场景。
        """
        db = SessionLocal()
        try:
            existing_scene = (
                db.query(SceneModel).filter(SceneModel.name == name).first()
            )
            if existing_scene:
                self.logger.debug(
                    f"Found existing scene by name '{name}': ID={existing_scene.id}"
                )
                return existing_scene
            else:
                self.logger.info(
                    f"Scene with name '{name}' not found. Creating new scene."
                )
                new_scene = SceneModel(
                    id=str(uuid.uuid4()), name=name, description=description
                )
                db.add(new_scene)
                db.commit()
                db.refresh(new_scene)
                self.logger.info(
                    f"Created new scene in DB: ID={new_scene.id}, Name='{name}'"
                )
                return new_scene
        finally:
            db.close()
