# filepath: app/services/word_service.py
from app.models.word import Word
from app.utils.json_storage import JSONStorage


class WordService:
    """字词服务类，负责字词的查询和管理。"""

    def __init__(self):
        self.storage = JSONStorage("data/words.json")

    def get_words_by_level(self, level: int) -> list:
        """根据超童级别查询字词。"""
        words = self.storage.load()
        return [word for word in words if word.get("chaotong_level") == level]

    def get_words_by_part_of_speech(self, part_of_speech: str) -> list:
        """根据词性查询字词。"""
        words = self.storage.load()
        return [word for word in words if word.get("part_of_speech") == part_of_speech]
