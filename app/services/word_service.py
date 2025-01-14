# app/services/word_service.py
import json
import logging
from typing import Dict, List
from app.config import Config
from app.models.word_model import WordModel


class WordService:
    """
    字词服务，提供字词相关的业务逻辑。
    """

    def __init__(self):
        self.words = self._load_words()
        logging.info(f"Loaded {len(self.words)} words from {Config.WORDS_FILE_PATH}")

    def _load_words(self) -> Dict[str, WordModel]:
        """
        加载字词数据
        Returns:
           一个字典， key 是 word_id， value 是 WordModel 对象
        """
        try:
            with open(Config.WORDS_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                words = {}
                for item in data:
                    word_model = WordModel.from_dict(item)
                    words[word_model.id] = word_model
                return words
        except FileNotFoundError:
            logging.error(f"File not found: {Config.WORDS_FILE_PATH}")
            return {}
        except json.JSONDecodeError:
            logging.error(f"JSON decode error: {Config.WORDS_FILE_PATH}")
            return {}

    def get_word_by_id(self, word_id: str) -> WordModel:
        """
        根据ID获取字词信息。
        Args:
            word_id (str): 字词ID.
        Returns:
            WordModel: 字词模型对象，如果不存在则返回 None.
        """
        return self.words.get(word_id)

    def get_words(
        self,
        level: int = None,
        part_of_speech: str = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[WordModel]:
        """
        根据条件获取字词列表。
        Args:
            level (int, optional): 超童级别，如果指定则返回该级别的词汇.
            part_of_speech (str, optional): 词性，如果指定则返回该词性的词汇.
            page (int, optional): 页码，默认为1.
            page_size (int, optional): 每页数量，默认为10.
        Returns:
            List[WordModel]: 字词模型对象列表.
        """
        filtered_words = list(self.words.values())

        if level:
            filtered_words = [
                word for word in filtered_words if word.chaotong_level == level
            ]
        if part_of_speech:
            filtered_words = [
                word for word in filtered_words if word.part_of_speech == part_of_speech
            ]

        start = (page - 1) * page_size
        end = start + page_size
        return filtered_words[start:end]

    def get_total_words(self, level: int = None, part_of_speech: str = None) -> int:
        """
        根据条件获取字词总数
        Args:
            level (int, optional): 超童级别，如果指定则返回该级别的词汇总数.
            part_of_speech (str, optional): 词性，如果指定则返回该词性的词汇总数.
        Returns:
            int: 字词总数.
        """
        filtered_words = list(self.words.values())

        if level:
            filtered_words = [
                word for word in filtered_words if word.chaotong_level == level
            ]
        if part_of_speech:
            filtered_words = [
                word for word in filtered_words if word.part_of_speech == part_of_speech
            ]

        return len(filtered_words)

    def get_key_words_by_ids(self, key_word_ids: List[str]) -> List[Dict]:
        """
        根据 key_word_ids 获取重点词汇的详细信息。
        Args:
            key_word_ids: 重点词汇 ID 列表。
        Returns:
           List[Dict]: 重点词汇的详细信息列表，包含 `word`, `pinyin`, `definition`, `part_of_speech` 和 `example`
        """
        key_words = []
        for word_id in key_word_ids:
            word_model = self.get_word_by_id(word_id)
            if word_model:
                key_words.append(
                    {
                        "word": word_model.word,
                        "pinyin": None,  # 暂时设置为 None, 后续可以从 words.json 中获取
                        "definition": None,  # 暂时设置为 None, 后续可以从 words.json 中获取
                        "part_of_speech": word_model.part_of_speech,
                        "example": None,  # 暂时设置为 None, 后续可以从 words.json 中获取
                    }
                )
        return key_words
