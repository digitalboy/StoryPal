# app/services/scene_service.py
import json
import logging
from typing import Dict, List
from app.config import Config
from app.models.scene_model import SceneModel
from app.utils.json_storage import JSONStorage  # 导入 JSONStorage


class SceneService:
    """
    场景服务，提供场景相关的业务逻辑。
    """

    def __init__(self):
        self.storage = JSONStorage(Config.SCENES_FILE_PATH)  # 使用 JSONStorage
        self.scenes: Dict[str, SceneModel] = {}  # 初始化为空字典
        try:
            # 直接从 storage.data 加载数据
            for item in self.storage.data:
                try:
                    scene_model = SceneModel.from_dict(item)
                    self.scenes[scene_model.id] = scene_model
                except Exception as e:
                    logging.error(f"Error creating SceneModel from item {item}: {e}")
            logging.info(
                f"Loaded {len(self.scenes)} scenes from storage data ({Config.SCENES_FILE_PATH})"
            )
        except Exception as e:
            logging.exception(f"Error processing storage data for scenes: {e}")
            # 即使处理出错，也保持 self.scenes 为空字典

    def get_scene_by_id(self, scene_id: str) -> SceneModel | None:
        """
        根据ID获取场景信息。
        Args:
            scene_id (str): 场景ID.
        Returns:
            SceneModel: 场景模型对象，如果不存在则返回 None.
        """
        return self.scenes.get(scene_id)

    def create_scene(self, name: str, description: str) -> SceneModel:
        """
        创建场景。
        Args:
            name (str): 场景名称.
            description (str): 场景描述.
        Returns:
            SceneModel: 创建的场景模型对象.
        """
        # 检查场景名称是否已存在
        existing_scene = self.find_scene_by_name(name)
        if existing_scene:
            logging.warning(
                f"Scene with name '{name}' already exists with ID {existing_scene.id}. Returning existing scene."
            )
            return existing_scene

        scene = SceneModel(name=name, description=description)
        self.scenes[scene.id] = scene
        self._save_scenes()
        logging.info(f"Created new scene: ID={scene.id}, Name='{name}'")
        return scene

    def update_scene(self, scene_id: str, name: str, description: str) -> SceneModel:
        """
        更新场景信息。
        Args:
            scene_id (str): 场景ID.
            name (str): 新的场景名称.
            description (str): 新的场景描述.
        Returns:
             SceneModel: 更新后的场景模型对象，如果场景不存在则返回 None.
        """
        scene = self.get_scene_by_id(scene_id)
        if scene:
            scene.name = name
            scene.description = description
            self._save_scenes()
            return scene
        return None

    def delete_scene(self, scene_id: str) -> bool:
        """
        删除场景。
        Args:
            scene_id (str): 场景ID.
        Returns:
            bool: True 如果删除成功， False 如果场景不存在.
        """
        if scene_id in self.scenes:
            del self.scenes[scene_id]
            self._save_scenes()
            return True
        return False

    def find_scene_by_name(self, name: str) -> SceneModel | None:
        """
        根据名称查找场景。
        Args:
            name (str): 场景名称.
        Returns:
            SceneModel: 找到的场景模型对象，如果不存在则返回 None.
        """
        for scene in self.scenes.values():
            if scene.name == name:
                return scene
        return None

    def find_or_create_scene(
        self, name: str, description: str = "由 AI 生成"
    ) -> SceneModel:
        """
        根据名称查找场景，如果不存在则创建新场景。
        Args:
            name (str): 场景名称.
            description (str, optional): 场景描述，如果创建新场景时使用。默认为 "由 AI 生成".
        Returns:
            SceneModel: 找到或创建的场景模型对象.
        """
        existing_scene = self.find_scene_by_name(name)
        if existing_scene:
            logging.debug(
                f"Found existing scene by name '{name}': ID={existing_scene.id}"
            )
            return existing_scene
        else:
            logging.info(f"Scene with name '{name}' not found. Creating new scene.")
            return self.create_scene(name, description)

    def _save_scenes(self):
        """
        保存场景数据到文件。
        """
        try:
            self.storage.save(
                [scene.to_dict() for scene in self.scenes.values()]
            )  # 保存到 storage
        except Exception as e:
            logging.error(f"Error saving scenes to file: {e}")
