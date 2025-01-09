# filepath: app/services/word_service.py
from app.models.word import Word
from app.utils.json_storage import JSONStorage


class WordService:
    """字词服务类，负责字词的查询和管理。"""

    def __init__(self):
        self.storage = JSONStorage("data/words.json")

    def create_word(self, word_data: dict) -> dict:
        """创建字词。"""
        word = Word(
            word=word_data.get("word"),
            pinyin=word_data.get("pinyin"),
            definition=word_data.get("definition"),
            part_of_speech=word_data.get("part_of_speech"),
            chaotong_level=word_data.get("chaotong_level"),
            characters=word_data.get("characters"),
            example=word_data.get("example"),
        )
        word.save()
        return word.to_dict()

    def get_word(self, word_id: str) -> dict:
        """根据 ID 获取字词。"""
        return Word.find_by_id(word_id)

    def update_word(self, word_id: str, updated_data: dict) -> bool:
        """更新字词信息。"""
        return Word.update(word_id, updated_data)

    def delete_word(self, word_id: str) -> bool:
        """删除字词。"""
        return Word.delete(word_id)

    def get_words_by_level(self, level: int) -> list:
        """根据超童级别查询字词。"""
        words = self.storage.load()
        return [word for word in words if word.get("chaotong_level") == level]

    def get_words_by_part_of_speech(self, part_of_speech: str) -> list:
        """根据词性查询字词。"""
        words = self.storage.load()
        return [word for word in words if word.get("part_of_speech") == part_of_speech]
