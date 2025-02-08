# tests/utils/test_literacy_calculator.py
import pytest
from app.utils.literacy_calculator import LiteracyCalculator
from unittest.mock import MagicMock
from app.models.word_model import WordModel

# 示例词汇数据
EXAMPLE_WORDS = [
    WordModel(word="你好", chaotong_level=1, part_of_speech="PHR"),
    WordModel(word="喜欢", chaotong_level=2, part_of_speech="V"),
    WordModel(word="跑步", chaotong_level=3, part_of_speech="V"),
    WordModel(word="白色", chaotong_level=4, part_of_speech="ADJ"),
    WordModel(word="白色", chaotong_level=5, part_of_speech="N"),
    WordModel(word="我们", chaotong_level=1, part_of_speech="PRON"),
    WordModel(word="我", chaotong_level=2, part_of_speech="PRON"),
    WordModel(word="游泳", chaotong_level=6, part_of_speech="V"),  # Added 游泳
]


@pytest.fixture
def literacy_calculator():
    # 模拟 word_service
    word_service_mock = MagicMock()
    word_service_mock.words = EXAMPLE_WORDS
    word_service_mock.is_word_exist.side_effect = lambda word, pos: any(
        wm.word == word and wm.part_of_speech == pos for wm in EXAMPLE_WORDS
    )
    word_service_mock.words = EXAMPLE_WORDS
    return LiteracyCalculator(word_service_mock)


def test_calculate_vocabulary_rate_no_chinese(literacy_calculator):
    text = "hello world"
    known_rate, unknown_rate, message = literacy_calculator.calculate_vocabulary_rate(
        text, 5
    )
    assert known_rate == -1
    assert unknown_rate == -1
    assert message == "No Chinese characters found."


def test_calculate_vocabulary_rate_level_1(literacy_calculator):
    text = "你好"
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 1)
    assert known_rate == 1.0
    assert unknown_rate == 0.0


def test_calculate_vocabulary_rate_level_2(literacy_calculator):
    text = "你好喜欢"
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 2)
    assert known_rate == 1.0
    assert unknown_rate == 0.0


def test_calculate_vocabulary_rate_level_3(literacy_calculator):
    text = "你好喜欢跑步"
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 3)
    assert known_rate == 1.0
    assert unknown_rate == 0.0


def test_calculate_vocabulary_rate_level_4(literacy_calculator):
    text = "你好喜欢跑步白色"  # 白色 level 4 (ADJ)
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 4)
    assert known_rate == 1.0
    assert unknown_rate == 0.0


def test_calculate_vocabulary_rate_level_5(literacy_calculator):
    text = "你好喜欢跑步白色"  # 白色 level 5 (N)
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 5)
    assert known_rate == 1.0
    assert unknown_rate == 0.0


def test_calculate_vocabulary_rate_level_6(literacy_calculator):
    text = "你好喜欢跑步白色游泳"  # 游泳现在 words 里面
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 6)
    assert abs(known_rate - 1.0) < 0.001  # Now 5/5 = 1.0
    assert abs(unknown_rate - 0.0) < 0.001


def test_calculate_vocabulary_rate_with_unknown_word(literacy_calculator):
    literacy_calculator.word_service.is_word_exist.return_value = False
    text = "不知道"
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 5)
    assert known_rate == 0.0
    assert unknown_rate == 1.0


def test_calculate_vocabulary_rate_with_duplicate_words_different_pos(
    literacy_calculator,
):
    # word service 需要判断 "白色" + "ADJ" 和 “白色" ＋ “N" 是否存在
    text = "白色 的 墙 是 白色 的"  # "的" 不在 words 里面
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 5)
    assert abs(known_rate - 2 / 11) < 0.001  # Corrected expected rate to 2/11
    assert abs(unknown_rate - 9 / 11) < 0.001  # Corrected expected rate to 9/11


def test_calculate_vocabulary_rate_with_word_and_unknown_char(literacy_calculator):
    text = "你好啊"  # "啊" 不在 words 里面
    known_rate, unknown_rate, _ = literacy_calculator.calculate_vocabulary_rate(text, 5)
    assert abs(known_rate - 1 / 2) < 0.001
    assert abs(unknown_rate - 1 / 2) < 0.001
