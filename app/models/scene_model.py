# filepath: app/models/scene.py
from .base_model import BaseModel
from app.utils.json_storage import JSONStorage


class Scene(BaseModel):
    """场景数据模型。"""

    _storage = JSONStorage("data/scenes.json")  # 指定存储文件路径

    def __init__(self, name, description, id=None, created_at=None, updated_at=None):
        super().__init__()
        self.name = name  # 场景名称
        self.description = description  # 场景描述
        if id:
            self.id = id
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at

    def save(self):
        """保存场景数据到 JSON 文件。"""
        scene_data = self.to_dict()  # 使用父类的 to_dict 方法
        self._storage.add(scene_data)

    @classmethod
    def find_by_id(cls, scene_id: str):
        """根据 ID 查找场景。"""
        scenes = cls._storage.load()
        print(f"find_by_id scenes: {scenes}")
        for scene in scenes:
            if scene.get("id") == scene_id:
                return cls(
                    name=scene["name"],
                    description=scene["description"],
                    id=scene["id"],
                    created_at=scene["created_at"],
                    updated_at=scene["updated_at"],
                )
        return None

    @classmethod
    def update(cls, scene_id: str, updated_data: dict) -> bool:
        """更新场景数据。"""
        scenes = cls._storage.load()
        for index, scene in enumerate(scenes):
            if scene.get("id") == scene_id:
                scenes[index].update(updated_data)
                cls._storage.save(scenes)
                return True
        return False

    @classmethod
    def delete(cls, scene_id: str) -> bool:
        """删除场景数据。"""
        scenes = cls._storage.load()
        for index, scene in enumerate(scenes):
            if scene.get("id") == scene_id:
                scenes.pop(index)
                cls._storage.save(scenes)
                return True
        return False
