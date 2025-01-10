# app/models/story_model.py
from app.models.base_model import BaseModel


class StoryModel(BaseModel):
    def __init__(
        self,
        story_id,
        title,
        content,
        vocabulary_level,
        scene,
        word_count,
        new_char_rate,
        new_char,
        key_words,
        **kwargs,
    ):
        super().__init__(id=story_id, **kwargs)
        self.story_id = self.id
        self.title = title
        self.content = content
        self.vocabulary_level = vocabulary_level
        self.scene = scene
        self.word_count = word_count
        self.new_char_rate = new_char_rate
        self.new_char = new_char
        self.key_words = key_words

    def to_dict(self):
        return {
            "story_id": self.story_id,
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
    def from_dict(cls, data):
        return cls(
            story_id=data.get("story_id"),
            title=data.get("title"),
            content=data.get("content"),
            vocabulary_level=data.get("vocabulary_level"),
            scene=data.get("scene"),
            word_count=data.get("word_count"),
            new_char_rate=data.get("new_char_rate"),
            new_char=data.get("new_char"),
            key_words=data.get("key_words"),
            created_at=data.get("created_at"),
        )
