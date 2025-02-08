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
        加载小于等于目标级别的所有词汇中包含的词和词性组合。
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

        for word_model in self.word_service.words:
            if word_model.chaotong_level <= target_level:
                if not word_model.part_of_speech:
                    self.logger.error(f"word {word_model.word} 不存在词性")
                    raise ValueError(
                        f"词 {word_model.word} 缺少词性，请检查 words.json 文件"
                    )
                known_words.add((word_model.word, word_model.part_of_speech))
        self.logger.debug(f"target_level: {target_level}, known_words: {known_words}")
        return known_words

    def _tokenize(self, text: str) -> List[Tuple[str, str]]:
        """
        使用自定义分词器，根据 words.json 文件进行分词，并返回词和词性组合。
        Args:
            text: 待分词的文本字符串。
        Returns:
            一个包含词和词性组合的列表，如果该词不在 `words.json` 文件中，词性为 "unknown" 。
        """
        tokens = []
        i = 0
        while i < len(text):
            # 默认当前字符为未知词
            longest_match = None
            # 遍历所有词， 找到最长匹配的词
            for word_model in self.word_service.words:
                if text.startswith(word_model.word, i):
                    if longest_match is None or len(word_model.word) > len(
                        longest_match.word
                    ):
                        longest_match = word_model

            if longest_match:
                tokens.append((longest_match.word, longest_match.part_of_speech))
                i += len(longest_match.word)
            else:
                tokens.append((text[i], "unknown"))
                i += 1

        self.logger.debug(f"text: {text}, tokens: {tokens}")
        return tokens

    def calculate_vocabulary_rate(
        self, text: str, target_level: int
    ) -> Tuple[float, float, str]:
        """
        计算文本的已知词率和生词率。
        """
        tokens = self._tokenize(text)
        total_words = len(tokens)

        has_chinese_chars = any(
            re.match(r"[\u4e00-\u9fff]", char) for char, _ in tokens
        )
        if not has_chinese_chars:
            return (-1, -1, "No Chinese characters found.")

        known_words = self._load_known_words(target_level)
        known_word_count = 0

        for word, pos in tokens:
            if (word, pos) in known_words:
                known_word_count += 1
            else:
                self.logger.debug(f"生词：{word}, 词性: {pos}")

        known_rate = known_word_count / total_words if total_words else 0.0  # 避免除以0
        unknown_rate = 1 - known_rate
        self.logger.debug(
            f"text: {text}, target_level: {target_level}, known_word_count: {known_word_count}, total_words: {total_words}, known_rate: {known_rate}, unknown_rate: {unknown_rate}"
        )
        return (known_rate, unknown_rate, "")