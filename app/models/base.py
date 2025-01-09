# filepath: app/models/base.py
from datetime import datetime, UTC
from uuid import uuid4


class BaseModel:
    """基础数据模型，其他模型继承自此类。"""

    def __init__(self):
        self.id = str(uuid4())  # 使用UUID作为唯一ID
        self.created_at = datetime.now(UTC).isoformat()  # 使用时区感知的时间
        self.updated_at = self.created_at  # 更新时间

    def update(self):
        """更新模型的更新时间。"""
        self.updated_at = datetime.now(UTC).isoformat()  # 使用时区感知的时间

    def to_dict(self):
        """将模型对象转换为字典格式。"""
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("_")  # 排除私有属性
        }
