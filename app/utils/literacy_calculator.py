# app/utils/literacy_calculator.py
import re
import logging
from typing import Dict, List, Tuple


class LiteracyCalculator:
    """
    生字率计算器 (基于字级别)
    """

    def __init__(self, word_service):
        self.word_service = word_service

    def _load_known_words(self, target_level):
        """
        加载小于等于目标级别的所有词汇中包含的字。
        Args:
            target_level: 目标级别 (整数)。
        Returns:
            一个包含已知字的集合 (set)。
        """
        known_characters = set()
        for word_model in self.word_service.words.values():
            if word_model.chaotong_level <= target_level:
                for char_data in word_model.characters:
                    known_characters.add(char_data["character"])
        return known_characters

    def calculate_literacy_rate(self, text, target_level):
        """
        计算文本的已知字率和生字率。
        Args:
            text: 待计算的文本字符串。
            target_level: 目标级别 (整数)。
        Returns:
            一个包含已知字率和生字率的元组 (known_rate, unknown_rate)。
        """
        known_characters = self._load_known_words(target_level)
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
        total_chinese_chars = len(chinese_chars)

        if total_chinese_chars == 0:
            return (1.0, 0.0)

        known_char_count = 0
        for char in chinese_chars:
            if char in known_characters:
                known_char_count += 1

        known_rate = known_char_count / total_chinese_chars
        unknown_rate = 1 - known_rate
        return (known_rate, unknown_rate)
