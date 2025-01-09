# filepath: app/utils/json_storage.py
import json
import os
from typing import Dict, List, Any


class JSONStorage:
    """JSON 文件存储工具类，用于数据的加载和保存。"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump([], f)  # 初始化空列表

    def load(self) -> List[Dict[str, Any]]:
        """从 JSON 文件加载数据。"""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 如果文件损坏，返回空列表并修复文件
            self.save([])
            return []

    def save(self, data: List[Dict[str, Any]]) -> None:
        """将数据保存到 JSON 文件。"""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, item: Dict[str, Any]) -> None:
        """向 JSON 文件中添加一条数据。"""
        data = self.load()
        data.append(item)
        self.save(data)

    def update(self, item_id: str, updated_item: Dict[str, Any]) -> bool:
        """更新 JSON 文件中的一条数据。"""
        data = self.load()
        for index, item in enumerate(data):
            if item.get("id") == item_id:
                data[index] = updated_item
                self.save(data)
                return True
        return False

    def delete(self, item_id: str) -> bool:
        """从 JSON 文件中删除一条数据。"""
        data = self.load()
        for index, item in enumerate(data):
            if item.get("id") == item_id:
                data.pop(index)
                self.save(data)
                return True
        return False
