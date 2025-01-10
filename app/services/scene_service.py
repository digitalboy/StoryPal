# filepath: app/services/scene_service.py
from app.models.scene_model import Scene


class SceneService:
    """场景服务，用于处理场景的业务逻辑。"""

    def create_scene(self, name: str, description: str) -> Scene:
        """创建场景。"""
        scene = Scene(name=name, description=description)
        scene.save()
        return scene

    def get_scene(self, scene_id: str) -> Scene:
        """根据 ID 获取场景。"""
        return Scene.find_by_id(scene_id)

    def update_scene(self, scene_id: str, name: str, description: str) -> bool:
        """更新场景。"""
        updated_data = {"name": name, "description": description}
        return Scene.update(scene_id, updated_data)

    def delete_scene(self, scene_id: str) -> bool:
        """删除场景。"""
        return Scene.delete(scene_id)
