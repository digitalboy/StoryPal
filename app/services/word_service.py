# filepath: app/services/word_service.py
from app.models.word_model import Word


class WordService:
    """字词服务，用于处理字词的业务逻辑。"""

    def create_word(self, data: dict) -> Word:
        """创建字词。"""
        word = Word(**data)
        word.save()
        return word

    def get_word(self, word_id: str) -> Word:
        """根据 ID 获取字词。"""
        return Word.find_by_id(word_id)

    def update_word(self, word_id: str, updated_data: dict) -> bool:
        """更新字词。"""
        return Word.update(word_id, updated_data)

    def delete_word(self, word_id: str) -> bool:
        """删除字词。"""
        return Word.delete(word_id)

    def get_words_by_level(self, level: int) -> list[Word]:
        """根据等级获取字词"""
        words = Word._storage.load()
        return [Word(**word) for word in words if word["chaotong_level"] == level]

    def get_words_by_part_of_speech(self, part_of_speech: str) -> list[Word]:
        """根据词性获取字词"""
        words = Word._storage.load()
        return [
            Word(**word) for word in words if word["part_of_speech"] == part_of_speech
        ]

    def get_all_words(self) -> list[Word]:
        """获取所有字词"""
        words = Word._storage.load()
        return [Word(**word) for word in words]
