# app/utils/literacy_calculator.py
import re
from typing import List, Tuple


class LiteracyCalculator:
    """
    生字率计算器 (基于字级别和词性)
    """

    def __init__(self, word_service):
        if not word_service:
            raise ValueError("word_service cannot be None")
        self.word_service = word_service

    def _load_known_words(self, target_level: int) -> set:
        """
        加载小于目标级别的所有词汇中包含的字和词性组合。
        Args:
            target_level: 目标级别 (整数)。
        Returns:
            一个包含已知字和词性组合的集合 (set)， 使用 (character, part_of_speech) tuple。
        """
        known_characters = set()
        if not self.word_service.words:
            return known_characters
        for word_model in self.word_service.words.values():
            if word_model.chaotong_level < target_level:
                for char_data in word_model.characters:
                    known_characters.add(
                        (char_data["character"], char_data["part_of_speech"])
                    )
        return known_characters

    def _tokenize(self, text: str) -> List[Tuple[str, str]]:
        """
        使用自定义分词器，根据 words.json 文件进行分词，并返回字和词性组合。
        Args:
            text: 待分词的文本字符串。
        Returns:
             一个包含字和词性组合的列表，如果该字不在 `words.json` 文件中，词性为 "unkown" 。
        """
        tokens = []
        i = 0
        while i < len(text):
            matched = False
            # 优先匹配长词
            for word_model in sorted(
                self.word_service.words.values(),
                key=lambda x: len(x.word),
                reverse=True,
            ):
                if text.startswith(word_model.word, i):
                    for char_data in word_model.characters:
                        tokens.append(
                            (char_data["character"], char_data["part_of_speech"])
                        )
                    i += len(word_model.word)
                    matched = True
                    break
            if not matched:
                tokens.append((text[i], "unknown"))  # 所有的字符都作为token
                i += 1
        return tokens

    def calculate_literacy_rate(
        self, text: str, target_level: int
    ) -> Tuple[float, float, str]:
        """
        计算文本的已知字率和生字率。
        Args:
            text: 待计算的文本字符串。
            target_level: 目标级别 (整数)。
        Returns:
             一个包含已知字率和生字率的元组 (known_rate, unknown_rate), 如果没有中文字符，返回 (-1, -1, "No Chinese characters found.")。
        """
        tokens = self._tokenize(text)
        total_chars = len(tokens)

        has_chinese_chars = any(
            re.match(r"[\u4e00-\u9fff]", char) for char, _ in tokens
        )
        if not has_chinese_chars:
            return (-1, -1, "No Chinese characters found.")

        known_characters = self._load_known_words(target_level)
        known_char_count = 0
        for char, pos in tokens:
            if (char, pos) in known_characters:
                known_char_count += 1

        known_rate = known_char_count / total_chars
        unknown_rate = 1 - known_rate
        return (known_rate, unknown_rate, "")
