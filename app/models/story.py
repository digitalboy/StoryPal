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
        story_data = self.to_dict()  # 使用父类的 to_dict 方法
        self._storage.add(story_data)

    @classmethod
    def find_by_id(cls, story_id: str):
        """根据 ID 查找故事。"""
        stories = cls._storage.load()
        for story in stories:
            if story.get("id") == story_id:
                return story
        return None
