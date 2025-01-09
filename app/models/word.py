# filepath: app/models/word.py
from .base import BaseModel
from app.utils.json_storage import JSONStorage


class Word(BaseModel):
    """字词数据模型。"""

    _storage = JSONStorage("data/words.json")  # 指定存储文件路径

    def __init__(
        self,
        word=None,
        pinyin=None,
        definition=None,
        part_of_speech=None,
        chaotong_level=None,
        characters=None,
        example=None,
    ):
        super().__init__()
        self.word = word  # 词
        self.pinyin = pinyin  # 拼音
        self.definition = definition  # 释义
        self.part_of_speech = part_of_speech  # 词性
        self.chaotong_level = chaotong_level  # 超童级别
        self.characters = characters  # 词中包含的字
        self.example = example  # 例句

    def save(self):
        """保存 Word 对象到 JSON 文件。"""
        word_data = self.to_dict()  # 使用父类的 to_dict 方法
        self._storage.add(word_data)

    @classmethod
    def find_by_id(cls, word_id: str):
        """根据 ID 查找字词，返回字典格式的数据。"""
        words = cls._storage.load()
        for word_data in words:
            if word_data.get("id") == word_id:
                return word_data  # 返回字典格式的数据
        return None

    @classmethod
    def update(cls, word_id: str, updated_data: dict) -> bool:
        """更新字词数据。"""
        words = cls._storage.load()
        for index, word in enumerate(words):
            if word.get("id") == word_id:
                words[index].update(updated_data)
                cls._storage.save(words)
                return True
        return False

    @classmethod
    def delete(cls, word_id: str) -> bool:
        """删除字词数据。"""
        words = cls._storage.load()
        for index, word in enumerate(words):
            if word.get("id") == word_id:
                words.pop(index)
                cls._storage.save(words)
                return True
        return False
