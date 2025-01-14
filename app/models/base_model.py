# app/models/base_model.py
import uuid
from datetime import datetime, timezone
from typing import Dict


class BaseModel:
    """
    所有数据模型的基类，提供通用的属性和方法。
    """

    def __init__(self, id: str = None, created_at: str = None):
        """
        初始化方法。
        Args:
            id (str, optional): 模型的唯一ID，如果为None，则自动生成UUID。
            created_at (str, optional): 模型的创建时间，如果为None，则设置为当前时间。
        """
        self.id = id if id else str(uuid.uuid4())
        self.created_at = (
            created_at if created_at else datetime.now(timezone.utc).isoformat()
        )

    def to_dict(self) -> Dict:
        """
        将模型对象转换为字典。
        Returns:
            dict: 模型对象的字典表示。
        """
        return {"id": self.id, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, data: Dict):
        """
        从字典创建模型对象。
        Args:
            data (dict): 模型对象的字典表示。
        Returns:
            BaseModel: 模型对象。
        """
        return cls(**data)
