# filepath: app/models/story.py
from .base_model import BaseModel
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
        id=None,
        created_at=None,
        updated_at=None,
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
        if id:
            self.id = id
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at

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
                return cls(**story)
        return None

    @classmethod
    def update(cls, story_id: str, updated_data: dict) -> bool:
        """更新故事数据。"""
        stories = cls._storage.load()
        for index, story in enumerate(stories):
            if story.get("id") == story_id:
                stories[index].update(updated_data)
                cls._storage.save(stories)
                return True
        return False

    @classmethod
    def delete(cls, story_id: str) -> bool:
        """删除故事数据。"""
        stories = cls._storage.load()
        for index, story in enumerate(stories):
            if story.get("id") == story_id:
                stories.pop(index)
                cls._storage.save(stories)
                return True
        return False
