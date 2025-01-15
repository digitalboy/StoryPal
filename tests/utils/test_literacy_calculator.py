# tests/utils/test_literacy_calculator.py
import pytest
from app.utils.literacy_calculator import LiteracyCalculator
from unittest.mock import MagicMock
import re


@pytest.fixture
def mock_word_service():
    """
    Mock word service for testing.
    """
    mock_service = MagicMock()
    mock_service.words = {
        "word1": MagicMock(
            word="你好",
            chaotong_level=1,
            characters=[
                {"character": "你", "part_of_speech": "PR"},
                {"character": "好", "part_of_speech": "adj"},
            ],
        ),
        "word2": MagicMock(
            word="喜欢",
            chaotong_level=5,
            characters=[
                {"character": "喜", "part_of_speech": "v"},
                {"character": "欢", "part_of_speech": "adj"},
            ],
        ),
        "word3": MagicMock(
            word="跑步",
            chaotong_level=10,
            characters=[
                {"character": "跑", "part_of_speech": "v"},
                {"character": "步", "part_of_speech": "n"},
            ],
        ),
        "word4": MagicMock(
            word="白色",
            chaotong_level=10,
            characters=[
                {"character": "白", "part_of_speech": "adj"},
                {"character": "色", "part_of_speech": "n"},
            ],
        ),
        "word5": MagicMock(
            word="白说",
            chaotong_level=10,
            characters=[
                {"character": "白", "part_of_speech": "adv"},
                {"character": "说", "part_of_speech": "v"},
            ],
        ),
        "word6": MagicMock(
            word="今天",
            chaotong_level=3,
            characters=[
                {"character": "今", "part_of_speech": "t"},
                {"character": "天", "part_of_speech": "t"},
            ],
        ),
        "word7": MagicMock(
            word="很好",
            chaotong_level=10,
            characters=[
                {"character": "很", "part_of_speech": "adv"},
                {"character": "好", "part_of_speech": "adj"},
            ],
        ),
    }
    return mock_service


def test_load_known_words(mock_word_service):
    """
    Test _load_known_words method.
    """
    calculator = LiteracyCalculator(mock_word_service)
    known_chars = calculator._load_known_words(5)
    assert len(known_chars) == 4
    assert ("你", "PR") in known_chars
    assert ("好", "adj") in known_chars
    assert ("今", "t") in known_chars
    assert ("天", "t") in known_chars

    known_chars = calculator._load_known_words(10)
    assert len(known_chars) == 6  #  '喜/v', '欢/adj', 不应该在里面，因为 level = 5
    assert ("你", "PR") in known_chars
    assert ("好", "adj") in known_chars
    assert ("今", "t") in known_chars
    assert ("天", "t") in known_chars
    assert ("喜", "v") in known_chars
    assert ("欢", "adj") in known_chars


def test_load_known_words_empty_words(mock_word_service):
    mock_word_service.words = {}
    calculator = LiteracyCalculator(mock_word_service)
    known_chars = calculator._load_known_words(5)
    assert len(known_chars) == 0


def test_tokenize(mock_word_service):
    """
    Test _tokenize method.
    """
    calculator = LiteracyCalculator(mock_word_service)
    tokens = calculator._tokenize("你好，我喜欢跑步")
    assert tokens == [
        ("你", "PR"),
        ("好", "adj"),
        ("，", "unknown"),
        ("我", "unknown"),
        ("喜", "v"),
        ("欢", "adj"),
        ("跑", "v"),
        ("步", "n"),
    ]

    tokens = calculator._tokenize("白色，白说")
    assert tokens == [
        ("白", "adj"),
        ("色", "n"),
        ("，", "unknown"),
        ("白", "adv"),
        ("说", "v"),
    ]

    tokens = calculator._tokenize("我喜欢游泳")
    assert tokens == [
        ("我", "unknown"),
        ("喜", "v"),
        ("欢", "adj"),
        ("游", "unknown"),
        ("泳", "unknown"),
    ]

    tokens = calculator._tokenize("今天天气很好")
    assert tokens == [
        ("今", "t"),
        ("天", "t"),
        ("天", "unknown"),
        ("气", "unknown"),
        ("很", "adv"),
        ("好", "adj"),
    ]

    tokens = calculator._tokenize("hello world")
    assert tokens == [
        ("h", "unknown"),
        ("e", "unknown"),
        ("l", "unknown"),
        ("l", "unknown"),
        ("o", "unknown"),
        (" ", "unknown"),
        ("w", "unknown"),
        ("o", "unknown"),
        ("r", "unknown"),
        ("l", "unknown"),
        ("d", "unknown"),
    ]


def test_calculate_literacy_rate(mock_word_service):
    """
    Test calculate_literacy_rate method.
    """
    calculator = LiteracyCalculator(mock_word_service)
    known_rate, unknown_rate, _ = calculator.calculate_literacy_rate("你好", 5)
    assert known_rate == 1.0
    assert unknown_rate == 0.0

    known_rate, unknown_rate, _ = calculator.calculate_literacy_rate("我喜欢跑步", 5)
    assert known_rate == 0.0
    assert unknown_rate == 1.0

    known_rate, unknown_rate, _ = calculator.calculate_literacy_rate("我喜欢跑步", 10)
    assert known_rate == 0.4
    assert unknown_rate == 0.6

    known_rate, unknown_rate, _ = calculator.calculate_literacy_rate("我喜欢游泳", 10)
    assert known_rate == pytest.approx(2 / 5)
    assert unknown_rate == pytest.approx(3 / 5)

    known_rate, unknown_rate, _ = calculator.calculate_literacy_rate("白色，白说", 10)
    assert known_rate == 0.0
    assert unknown_rate == 1.0

    known_rate, unknown_rate, _ = calculator.calculate_literacy_rate("今天天气很好", 10)
    assert known_rate == pytest.approx(3 / 6)
    assert unknown_rate == pytest.approx(3 / 6)


def test_calculate_literacy_rate_empty_text(mock_word_service):
    """
    Test calculate_literacy_rate with empty text.
    """
    calculator = LiteracyCalculator(mock_word_service)
    result = calculator.calculate_literacy_rate("", 5)
    assert result == (-1, -1, "No Chinese characters found.")


def test_calculate_literacy_rate_no_chinese_text(mock_word_service):
    calculator = LiteracyCalculator(mock_word_service)
    result = calculator.calculate_literacy_rate("hello world", 5)
    assert result == (-1, -1, "No Chinese characters found.")


def test_init_with_none_word_service():
    with pytest.raises(ValueError, match="word_service cannot be None"):
        LiteracyCalculator(None)
