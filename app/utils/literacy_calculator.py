# app/utils/literacy_calculator.py
import re
from typing import List, Tuple, Set
import logging


class LiteracyCalculator:
    """
    生词率计算器 (基于词级别和词性)
    """

    def __init__(self, word_service):
        if not word_service:
            raise ValueError("word_service cannot be None")
        self.word_service = word_service
        self.logger = logging.getLogger(__name__)

    def _load_known_words(self, target_level: int) -> Set[Tuple[str, str]]:
        """
        加载 **小于** 目标级别的所有词汇中包含的词和词性组合。  **(已更正为 < target_level)**
        Args:
            target_level: 目标级别 (整数)。
        Returns:
            一个包含已知词和词性组合的集合 (set)， 使用 (word, part_of_speech) tuple。
        Raises:
            ValueError: 如果 words.json 文件中存在词，但是没有词性。
        """
        known_words: Set[Tuple[str, str]] = set()
        if not self.word_service.words:
            return known_words

        for word_model in self.word_service.words.values():
            if word_model.chaotong_level < target_level:  # **已改回 < target_level**
                if not word_model.part_of_speech:
                    self.logger.error(f"word {word_model.word} 不存在词性")
                    raise ValueError(
                        f"词 {word_model.word} 缺少词性，请检查 words.json 文件"
                    )
                known_words.add((word_model.word, word_model.part_of_speech))
        self.logger.debug(f"target_level: {target_level}, known_words: {known_words}")
        return known_words

    def calculate_vocabulary_rate(
        self, text: str, target_level: int
    ) -> Tuple[int, float, List[str]]:
        """
        计算文本的词数、生词率，并返回生词列表。
        """
        tokens = text.split("|")
        word_count = len(tokens)
        unknown_words = []
        known_words = self._load_known_words(target_level)
        unknown_word_count = 0

        for token in tokens:
            parts = token.split("(")  # 使用中文括号分割词语和词性
            if len(parts) == 2:
                word = parts[0].strip()
                pos = parts[1].replace(")", "").strip()  # 移除中文括号和空格
            else:
                word = token.strip()
                pos = "UNKNOWN"  # 无法识别词性时设置为 unknown
                self.logger.warning(f"无法识别词性: {token}")

            if (word, pos) not in known_words:
                unknown_words.append(f"{word}({pos})")
                unknown_word_count += 1
            else:
                self.logger.debug(f"已知词：{word}, 词性: {pos}")

        new_word_rate = unknown_word_count / word_count if word_count else 0.0
        self.logger.debug(
            f"text: {text}, target_level: {target_level}, word_count: {word_count}, new_word_rate: {new_word_rate}, unknown_words: {unknown_words}"
        )
        return word_count, new_word_rate, unknown_words
