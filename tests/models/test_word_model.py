# tests/services/test_word_service.py
import unittest
from unittest.mock import patch, mock_open
from app.services.word_service import WordService
from app.models.word_model import WordModel
import json
from typing import List, Dict


class TestWordService(unittest.TestCase):
    """
    测试字词服务 (WordService) 的功能。
    """

    def setUp(self):
        """
        设置测试环境。
        """
        self.sample_words_data = [
            {
                "word_id": "test_word_id_1",
                "word": "你好",
                "chaotong_level": 1,
                "part_of_speech": "其他",
                "hsk_level": 1,
                "characters": [
                    {"character": "你", "part_of_speech": "PR"},
                    {"character": "好", "part_of_speech": "ADJ"},
                ],
            },
            {
                "word_id": "test_word_id_2",
                "word": "喜欢",
                "chaotong_level": 5,
                "part_of_speech": "动词",
                "hsk_level": 2,
                "characters": [
                    {"character": "喜", "part_of_speech": "ADJ"},
                    {"character": "欢", "part_of_speech": "ADJ"},
                ],
            },
            {
                "word_id": "test_word_id_3",
                "word": "跑步",
                "chaotong_level": 10,
                "part_of_speech": "动词",
                "hsk_level": 2,
                "characters": [
                    {"character": "跑", "part_of_speech": "v"},
                    {"character": "步", "part_of_speech": "n"},
                ],
            },
        ]
        self.sample_words_json = json.dumps(self.sample_words_data)

    def test_load_words(self):
        """
        测试加载字词数据。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
        self.assertEqual(len(word_service.words), 3)
        self.assertIsInstance(word_service.words["test_word_id_1"], WordModel)
        self.assertEqual(word_service.words["test_word_id_1"].word, "你好")
        self.assertEqual(word_service.words["test_word_id_2"].word, "喜欢")
        self.assertEqual(word_service.words["test_word_id_3"].word, "跑步")

    def test_load_words_file_not_found(self):
        """
        测试加载字词数据，文件不存在的情况。
        """
        with patch("app.services.word_service.open", side_effect=FileNotFoundError):
            word_service = WordService()
        self.assertEqual(len(word_service.words), 0)

    def test_load_words_json_decode_error(self):
        """
        测试加载字词数据，JSON 解析错误的情况。
        """
        with patch(
            "app.services.word_service.open", mock_open(read_data="invalid json")
        ):
            word_service = WordService()
        self.assertEqual(len(word_service.words), 0)

    def test_get_word_by_id(self):
        """
        测试根据ID获取字词信息。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            word = word_service.get_word_by_id("test_word_id_2")
            self.assertEqual(word.word, "喜欢")
            self.assertEqual(word.chaotong_level, 5)
            self.assertEqual(word.part_of_speech, "动词")

    def test_get_word_by_id_not_found(self):
        """
        测试根据ID获取字词信息，ID不存在的情况。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            word = word_service.get_word_by_id("not_exist_id")
            self.assertIsNone(word)

    def test_get_words(self):
        """
        测试根据条件获取字词列表。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            words = word_service.get_words()
            self.assertEqual(len(words), 3)
            self.assertEqual(words[0].word, "你好")
            self.assertEqual(words[1].word, "喜欢")
            self.assertEqual(words[2].word, "跑步")

    def test_get_words_with_level(self):
        """
        测试根据级别获取字词列表。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            words = word_service.get_words(level=5)
            self.assertEqual(len(words), 1)
            self.assertEqual(words[0].word, "喜欢")

    def test_get_words_with_part_of_speech(self):
        """
        测试根据词性获取字词列表。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            words = word_service.get_words(part_of_speech="动词")
            self.assertEqual(len(words), 2)
            self.assertEqual(words[0].word, "喜欢")
            self.assertEqual(words[1].word, "跑步")

    def test_get_words_with_pagination(self):
        """
        测试分页获取字词列表。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            words = word_service.get_words(page=2, page_size=2)
            self.assertEqual(len(words), 1)
            self.assertEqual(words[0].word, "跑步")

    def test_get_total_words(self):
        """
        测试获取字词总数
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            total = word_service.get_total_words()
            self.assertEqual(total, 3)

    def test_get_total_words_with_level(self):
        """
        测试根据级别获取字词总数
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            total = word_service.get_total_words(level=5)
            self.assertEqual(total, 1)

    def test_get_total_words_with_part_of_speech(self):
        """
        测试根据词性获取字词总数
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            total = word_service.get_total_words(part_of_speech="动词")
            self.assertEqual(total, 2)

    def test_get_key_words_by_ids(self):
        """
        测试根据 key_word_ids 获取重点词汇。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            key_word_ids = ["test_word_id_1", "test_word_id_3"]
            key_words = word_service.get_key_words_by_ids(key_word_ids)
            self.assertEqual(len(key_words), 2)
            self.assertEqual(key_words[0]["word"], "你好")
            self.assertEqual(key_words[1]["word"], "跑步")
            self.assertEqual(key_words[0]["part_of_speech"], "其他")
            self.assertEqual(key_words[1]["part_of_speech"], "动词")
            self.assertIsNone(key_words[0]["pinyin"])
            self.assertIsNone(key_words[0]["definition"])
            self.assertIsNone(key_words[0]["example"])

    def test_get_key_words_by_ids_not_found(self):
        """
        测试根据 key_word_ids 获取重点词汇，ID不存在的情况。
        """
        with patch(
            "app.services.word_service.open",
            mock_open(read_data=self.sample_words_json),
        ):
            word_service = WordService()
            key_word_ids = ["test_word_id_1", "not_exist_id"]
            key_words = word_service.get_key_words_by_ids(key_word_ids)
            self.assertEqual(len(key_words), 1)
            self.assertEqual(key_words[0]["word"], "你好")


if __name__ == "__main__":
    unittest.main()
