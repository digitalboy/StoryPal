# app/models/scene_model.py
from typing import Dict
from app.models.base_model import BaseModel


class SceneModel(BaseModel):
    """
    场景数据模型。
    """

    def __init__(
        self,
        scene_id: str = None,
        name: str = None,
        description: str = None,
        created_at: str = None,
    ):
        """
        初始化方法。
        Args:
             scene_id (str, optional): 场景的唯一ID，如果为None，则自动生成UUID.
            name (str): 场景名称.
            description (str): 场景描述.
            created_at (str, optional): 模型的创建时间，如果为None，则设置为当前时间.
        """
        super().__init__(id=scene_id, created_at=created_at)
        self.name = name
        self.description = description

    def to_dict(self) -> Dict:
        """
        将模型对象转换为字典。
        Returns:
            dict: 模型对象的字典表示。
        """
        return {
            "scene_id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """
        从字典创建模型对象。
        Args:
            data (dict): 模型对象的字典表示.
        Returns:
            SceneModel: 场景模型对象.
        """
        # 映射 JSON 中的 scene_id 到模型的 id
        scene_id = data.get("scene_id")
        return cls(
            scene_id=scene_id,  # 使用 scene_id 初始化 id
            name=data.get("name"),
            description=data.get("description"),
            created_at=data.get("created_at"),
        )
