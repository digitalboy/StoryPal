# filepath: app/services/scene_service.py
from app.models.scene import Scene
from app.utils.json_storage import JSONStorage


class SceneService:
    """场景服务类，负责场景的 CRUD 操作。"""

    def __init__(self):
        self.storage = JSONStorage("data/scenes.json")

    def create_scene(self, name: str, description: str) -> Scene:
        """创建新场景。"""
        scene = Scene(name, description)
        scene.save()
        return scene

    def get_scene(self, scene_id: str) -> dict:
        """根据 ID 获取场景。"""
        return Scene.find_by_id(scene_id)

    def update_scene(self, scene_id: str, name: str, description: str) -> bool:
        """更新场景信息。"""
        scene_data = Scene.find_by_id(scene_id)
        if scene_data:
            scene_data["name"] = name
            scene_data["description"] = description
            self.storage.update(scene_id, scene_data)
            return True
        return False

    def delete_scene(self, scene_id: str) -> bool:
        """删除场景。"""
        return self.storage.delete(scene_id)
