# app/models/story_model.py
from typing import List, Dict, Optional
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
        scene: str = None,
        word_count: int = None,
        new_char_rate: float = None,
        new_char: int = None,
        key_words: List[Dict] = None,
        created_at: str = None,
    ):
        """
        初始化方法。
        Args:
            story_id (str, optional): 故事的唯一ID，如果为None，则自动生成UUID.
            title (str): 故事标题.
            content (str): 故事内容.
            vocabulary_level (int):  超童级别， 取值范围 1-100.
            scene (str): 场景ID， UUID 格式.
            word_count (int): 故事的字数.
            new_char_rate (float): 故事的生字率， 取值范围 0-1.
             new_char (int): 故事的生字数量.
            key_words (List[Dict]): 故事中包含的重点词汇列表.
            created_at (str, optional): 模型的创建时间，如果为None，则设置为当前时间.
        """
        super().__init__(id=story_id, created_at=created_at)
        self.title = title
        self.content = content
        self.vocabulary_level = vocabulary_level
        self.scene = scene
        self.word_count = word_count
        self.new_char_rate = new_char_rate
        self.new_char = new_char
        self.key_words = key_words if key_words else []

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
            "scene": self.scene,
            "word_count": self.word_count,
            "new_char_rate": self.new_char_rate,
            "new_char": self.new_char,
            "key_words": self.key_words,
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
