# app/services/scene_service.py
import json
import logging
from typing import Dict, List
from app.config import Config
from app.models.scene_model import SceneModel


class SceneService:
    """
    场景服务，提供场景相关的业务逻辑。
    """

    def __init__(self):
        self.scenes = self._load_scenes()
        logging.info(f"Loaded {len(self.scenes)} scenes from {Config.SCENES_FILE_PATH}")

    def _load_scenes(self) -> Dict[str, SceneModel]:
        """
        加载场景数据。
        Returns:
           一个字典，key 是 scene_id， value 是 SceneModel 对象。
        """
        try:
            with open(Config.SCENES_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                scenes = {}
                for item in data:
                    scene_model = SceneModel.from_dict(item)
                    scenes[scene_model.id] = scene_model
                return scenes
        except FileNotFoundError:
            logging.error(f"File not found: {Config.SCENES_FILE_PATH}")
            return {}
        except json.JSONDecodeError:
            logging.error(f"JSON decode error: {Config.SCENES_FILE_PATH}")
            return {}

    def get_scene_by_id(self, scene_id: str) -> SceneModel:
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
        scene = SceneModel(name=name, description=description)
        self.scenes[scene.id] = scene
        self._save_scenes()
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

    def _save_scenes(self):
        """
        保存场景数据到文件。
        """
        try:
            with open(Config.SCENES_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    [scene.to_dict() for scene in self.scenes.values()],
                    f,
                    indent=4,
                    ensure_ascii=False,
                )
        except Exception as e:
            logging.error(f"Error saving scenes to file: {e}")
