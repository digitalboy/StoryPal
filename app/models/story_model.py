# app/models/story_model.py
from typing import List, Dict, Optional, Union
from app.models.base_model import BaseModel


class StoryModel(BaseModel):
    """
    故事数据模型。
    """

    def __init__(
        self,
        story_id: str = None,
        title: str = None,
        content: str = None,
        vocabulary_level: int = None,
        scene_id: str = None,  # scene -> scene_id
        scene_name: str = None,  # 新增 scene_name
        word_count: int = None,  # story_word_count -> word_count
        new_word_rate: float = None,  # new_char_rate -> new_word_rate
        key_words: List[Dict] = None,
        unknown_words: List[Dict[str, Union[str, int, None]]] = None,  # 修改类型
        created_at: str = None,
    ):
        """
        初始化方法。
        Args:
            story_id (str, optional): 故事的唯一ID，如果为None，则自动生成UUID.
            title (str): 故事标题.
            content (str): 故事内容.
            vocabulary_level (int):  超童级别， 取值范围 1-100.
            scene_id (str): 场景ID， UUID 格式. # scene -> scene_id
            scene_name (str): 场景名称.  # 新增 scene_name
            word_count (int): 故事的词数. #  story_word_count -> word_count
            new_word_rate (float): 故事的生词率， 取值范围 0-1. #  new_char_rate -> new_word_rate
            key_words (List[Dict]): 故事中包含的重点词汇列表。每个字典包含 'word' 和 'part_of_speech' (英文缩写)。
            unknown_words (List[Dict[str, Union[str, int, None]]]): 故事中的生词列表。每个字典包含 'word', 'pos' (英文缩写), 和 'level'。
            created_at (str, optional): 模型的创建时间，如果为None，则设置为当前时间.
        """
        super().__init__(id=story_id, created_at=created_at)
        self.title = title
        self.content = content
        self.vocabulary_level = vocabulary_level
        self.scene_id = scene_id  # scene -> scene_id
        self.scene_name = scene_name  # 新增 scene_name
        self.word_count = word_count  # story_word_count -> word_count
        self.new_word_rate = new_word_rate  # new_char_rate -> new_word_rate
        self.key_words = key_words if key_words else []
        self.unknown_words = unknown_words if unknown_words else []

    def to_dict(self) -> Dict:
        """
        将模型对象转换为字典。
        Returns:
            dict: 模型对象的字典表示。
        """
        return {
            "story_id": self.id,
            "title": self.title,
            "content": self.content,
            "vocabulary_level": self.vocabulary_level,
            "scene_id": self.scene_id,  # scene -> scene_id
            "scene_name": self.scene_name,  # 新增 scene_name
            "word_count": self.word_count,  # story_word_count -> word_count
            "new_word_rate": self.new_word_rate,  # new_char_rate -> new_word_rate
            "key_words": self.key_words,  # 存储包含英文词性缩写的字典列表
            "unknown_words": self.unknown_words,  # 存储包含英文词性缩写的字典列表
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """
        从字典创建模型对象。
        Args:
            data (dict): 模型对象的字典表示.
        Returns:
            StoryModel: 故事模型对象.
        """
        return cls(**data)
