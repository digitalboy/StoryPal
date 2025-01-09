# filepath: app/models/story.py
from .base import BaseModel
from app.utils.json_storage import JSONStorage


class Story(BaseModel):
    """故事数据模型。"""

    _storage = JSONStorage("data/stories.json")  # 指定存储文件路径

    def __init__(
        self,
        title,
        content,
        vocabulary_level,
        scene_id,
        word_count,
        new_words,
        new_char_rate,
        key_words,
    ):
        super().__init__()
        self.title = title
        self.content = content
        self.vocabulary_level = vocabulary_level
        self.scene_id = scene_id
        self.word_count = word_count
        self.new_words = new_words
        self.new_char_rate = new_char_rate
        self.key_words = key_words

    def save(self):
        """保存故事数据到 JSON 文件。"""
        story_data = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "vocabulary_level": self.vocabulary_level,
            "scene_id": self.scene_id,
            "word_count": self.word_count,
            "new_words": self.new_words,
            "new_char_rate": self.new_char_rate,
            "key_words": self.key_words,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        self._storage.add(story_data)

    @classmethod
    def find_by_id(cls, story_id: str):
        """根据 ID 查找故事。"""
        stories = cls._storage.load()
        for story in stories:
            if story.get("id") == story_id:
                return story
        return None
