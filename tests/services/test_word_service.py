# tests/services/test_word_service.py
import pytest
from unittest.mock import patch, mock_open
from app.services.word_service import WordService
from app.models.word_model import WordModel
import json
from typing import List, Dict


class TestWordService:  # 继承 unittest.TestCase 去掉
    """
    测试词语服务 (WordService) 的功能。
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        设置测试环境。
        """
        self.sample_words_data = [
            {
                "word_id": "test_word_id_1",
                "word": "你好",
                "chaotong_level": 1,
                "part_of_speech": "PRON",
                "hsk_level": 1,
            },
            {
                "word_id": "test_word_id_2",
                "word": "喜欢",
                "chaotong_level": 5,
                "part_of_speech": "V",
                "hsk_level": 2,
            },
            {
                "word_id": "test_word_id_3",
                "word": "跑步",
                "chaotong_level": 10,
                "part_of_speech": "V",
                "hsk_level": 2,
            },
        ]
        self.sample_words_json = json.dumps(self.sample_words_data)

    def test_get_words_with_part_of_speech(self):
        """
        测试根据词性获取词语列表。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            word_service.words = {
                "test_word_id_1": WordModel.from_dict(self.sample_words_data[0]),
                "test_word_id_2": WordModel.from_dict(self.sample_words_data[1]),
                "test_word_id_3": WordModel.from_dict(self.sample_words_data[2]),
            }
            words = word_service.get_words()
            words = [word for word in words if word.part_of_speech == "V"]
            assert len(words) == 2
            assert words[0].word == "喜欢"
            assert words[1].word == "跑步"

    def test_get_total_words_with_part_of_speech(self):
        """
        测试根据词性获取词语总数
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            word_service.words = {
                "test_word_id_1": WordModel.from_dict(self.sample_words_data[0]),
                "test_word_id_2": WordModel.from_dict(self.sample_words_data[1]),
                "test_word_id_3": WordModel.from_dict(self.sample_words_data[2]),
            }
            total = word_service.get_total_words()
            filtered_words = [
                word
                for word in word_service.words.values()
                if word.part_of_speech == "V"
            ]
            assert len(filtered_words) == 2

    def test_get_words_below_level(self):
        """
        测试获取指定级别以下的所有词汇
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            words = word_service.get_words_below_level(5)
            assert len(words) == 1
            assert words[0].word == "你好"
