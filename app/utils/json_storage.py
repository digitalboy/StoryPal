import json
import logging
import os
from typing import List, Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONStorage:
    """
    一个通用的 JSON 文件存储类，用于加载、添加和保存字典列表。
    """

    def __init__(self, filepath: str):
        """
        初始化 JSONStorage。

        Args:
            filepath: JSON 文件的路径。
        """
        self.filepath = filepath
        self.data: List[Dict[str, Any]] = self._load()
        logger.info(
            f"Initialized JSONStorage for {filepath}. Loaded {len(self.data)} items."
        )

    def _load(self) -> List[Dict[str, Any]]:
        """
        从文件加载数据。如果文件不存在、为空或格式无效，则返回空列表。
        """
        try:
            # 检查文件是否存在且非空
            if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
                logger.warning(
                    f"File not found or empty: {self.filepath}. Initializing with empty list."
                )
                # 如果文件不存在，可以先创建一个空文件，确保目录存在
                os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump([], f)  # 写入空的 JSON 列表
                return []

            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # 再次检查内容是否为空（可能只有空白符）
                    logger.warning(
                        f"File content is empty or whitespace: {self.filepath}. Initializing with empty list."
                    )
                    return []
                try:
                    loaded_data = json.loads(content)
                    if isinstance(loaded_data, list):
                        return loaded_data
                    else:
                        logger.error(
                            f"Invalid format in {self.filepath}: Expected a list, got {type(loaded_data)}. Initializing with empty list."
                        )
                        return []
                except json.JSONDecodeError:
                    logger.exception(
                        f"Failed to decode JSON from {self.filepath}. File content might be corrupted. Initializing with empty list."
                    )
                    return []
        except IOError as e:
            logger.exception(
                f"IOError reading file {self.filepath}: {e}. Initializing with empty list."
            )
            return []
        except Exception as e:  # 捕获其他可能的异常
            logger.exception(
                f"Unexpected error loading file {self.filepath}: {e}. Initializing with empty list."
            )
            return []

    def _save(self):
        """
        将当前数据完整保存回文件，覆盖原有内容。
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            logger.debug(
                f"Successfully saved {len(self.data)} items to {self.filepath}"
            )
        except IOError as e:
            logger.exception(f"IOError writing file {self.filepath}: {e}")
        except Exception as e:  # 捕获其他可能的异常
            logger.exception(f"Unexpected error saving file {self.filepath}: {e}")

    def add(self, item: Dict[str, Any]):
        """
        向存储中添加一个新项，并立即保存。

        Args:
            item: 要添加的字典项。
        """
        if not isinstance(item, dict):
            logger.error(f"Attempted to add non-dict item: {type(item)}")
            return

        self.data.append(item)
        self._save()
        logger.info(f"Added new item to {self.filepath}. Total items: {len(self.data)}")

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有存储的项。
        """
        return self.data

    def find_by_id(
        self, item_id: str, id_field: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """
        根据 ID 查找项。

        Args:
            item_id: 要查找的 ID。
            id_field: 字典中用作 ID 的键名 (默认为 'id')。

        Returns:
            找到的字典项，如果未找到则返回 None。
        """
        for item in self.data:
            if item.get(id_field) == item_id:
                return item
        return None

    def update(
        self, item_id: str, updated_item: Dict[str, Any], id_field: str = "id"
    ) -> bool:
        """
        根据 ID 更新一个项，并立即保存。

        Args:
            item_id: 要更新的项的 ID。
            updated_item: 包含更新后数据的字典。
            id_field: 字典中用作 ID 的键名 (默认为 'id')。

        Returns:
            如果找到并更新成功则返回 True，否则返回 False。
        """
        for i, item in enumerate(self.data):
            if item.get(id_field) == item_id:
                # 确保更新后的项仍然包含 ID 字段
                if id_field not in updated_item:
                    updated_item[id_field] = item_id
                self.data[i] = updated_item
                self._save()
                logger.info(f"Updated item {item_id} in {self.filepath}.")
                return True
        logger.warning(
            f"Item with {id_field}={item_id} not found for update in {self.filepath}."
        )
        return False

    def delete(self, item_id: str, id_field: str = "id") -> bool:
        """
        根据 ID 删除一个项，并立即保存。

        Args:
            item_id: 要删除的项的 ID。
            id_field: 字典中用作 ID 的键名 (默认为 'id')。

        Returns:
            如果找到并删除成功则返回 True，否则返回 False。
        """
        original_length = len(self.data)
        self.data = [item for item in self.data if item.get(id_field) != item_id]
        if len(self.data) < original_length:
            self._save()
            logger.info(f"Deleted item {item_id} from {self.filepath}.")
            return True
        logger.warning(
            f"Item with {id_field}={item_id} not found for deletion in {self.filepath}."
        )
        return False
