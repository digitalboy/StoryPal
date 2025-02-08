# app/services/word_service.py
import json
import logging
from typing import Dict, List, Set
from app.config import Config
from app.models.word_model import WordModel


class WordService:
    """
    词语服务，提供词语相关的业务逻辑。
    """

    def __init__(self):
        self.words = self._load_words()
        logging.info(f"Loaded {len(self.words)} words from {Config.WORDS_FILE_PATH}")

    def _load_words(self) -> Dict[str, WordModel]:
        """
        加载词语数据
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
        根据ID获取词语信息。
        Args:
            word_id (str): 词语ID.
        Returns:
            WordModel: 词语模型对象，如果不存在则返回 None.
        """
        return self.words.get(word_id)

    def get_words(
        self,
        chaotong_level: int = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[WordModel]:
        """
        根据条件获取词语列表。
        Args:
            chaotong_level (int, optional): 超童级别，如果指定则返回该级别的词汇.
            page (int, optional): 页码，默认为1.
            page_size (int, optional): 每页数量，默认为10.
        Returns:
            List[WordModel]: 词语模型对象列表.
        """
        filtered_words = list(self.words.values())

        if chaotong_level is not None:
            filtered_words = [
                word for word in filtered_words if word.chaotong_level == chaotong_level
            ]

        start = (page - 1) * page_size
        end = start + page_size
        return filtered_words[start:end]

    def get_total_words(self, chaotong_level: int = None) -> int:
        """
        根据条件获取词语总数
        Args:
            chaotong_level (int, optional): 超童级别，如果指定则返回该级别的词汇总数.
        Returns:
            int: 词语总数.
        """
        filtered_words = list(self.words.values())

        if chaotong_level is not None:
            filtered_words = [
                word for word in filtered_words if word.chaotong_level == chaotong_level
            ]

        return len(filtered_words)

    def get_words_below_level(self, level: int) -> List[WordModel]:
        """
        获取指定级别以下的所有词汇
        Args:
           level (int): 目标级别, 不包含这个级别
        Returns:
            List[WordModel]:  词语模型对象列表
        """
        filtered_words = [
            word
            for word in self.words.values()
            if level is not None
            and isinstance(word.chaotong_level, int)
            and word.chaotong_level < level
        ]
        return filtered_words

    def get_known_characters(self, level: int) -> Set[str]:
        """
        获取指定级别以下的所有已知字 (字 + 词性) 组合
        Args:
            level (int): 目标级别, 不包含这个级别
        Returns:
             Set[str]: 已知字集合，每个元素是 “字/词性” 字符串
        """
        known_characters = set()
        words_below_level = self.get_words_below_level(level)
        for word in words_below_level:
            for char_info in word.characters:
                char_with_pos = (
                    f"{char_info['character']}/{char_info['part_of_speech']}"
                )
                known_characters.add(char_with_pos)

        return known_characters

    def get_key_words_by_ids(self, key_word_ids: List[str]) -> List[Dict]:
        """
        根据 key_word_ids 获取重点词汇的详细信息。
        Args:
            key_word_ids: 重点词汇 ID 列表。
        Returns:
           List[Dict]: 重点词汇的详细信息列表，包含 `word`, `pinyin`, `definition`,  和 `example`
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
                        "example": None,  # 暂时设置为 None, 后续可以从 words.json 中获取
                    }
                )
        return key_words
