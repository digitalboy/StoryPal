# tests/utils/test_literacy_calculator.py
import pytest
import re
from app.utils.literacy_calculator import LiteracyCalculator
from unittest.mock import MagicMock


@pytest.fixture
def mock_word_service():
    """
    创建一个模拟的 word_service 对象，用于测试
    """
    mock_service = MagicMock()
    mock_service.words = {
        "word1": MagicMock(
            word="你好",
            chaotong_level=1,
            part_of_speech="动词",
            characters=[
                {"character": "你", "part_of_speech": "PR"},
                {"character": "好", "part_of_speech": "ADJ"},
            ],
        ),
        "word2": MagicMock(
            word="喜欢",
            chaotong_level=5,
            part_of_speech="动词",
            characters=[
                {"character": "喜", "part_of_speech": "ADJ"},
                {"character": "欢", "part_of_speech": "ADJ"},
            ],
        ),
        "word3": MagicMock(
            word="跑步",
            chaotong_level=10,
            part_of_speech="动词",
            characters=[
                {"character": "跑", "part_of_speech": "v"},
                {"character": "步", "part_of_speech": "n"},
            ],
        ),
        "word4": MagicMock(
            word="早上",
            chaotong_level=15,
            part_of_speech="名词",
            characters=[
                {"character": "早", "part_of_speech": "ADJ"},
                {"character": "上", "part_of_speech": "n"},
            ],
        ),
        "word5": MagicMock(
            word="公园",
            chaotong_level=20,
            part_of_speech="名词",
            characters=[
                {"character": "公", "part_of_speech": "n"},
                {"character": "园", "part_of_speech": "n"},
            ],
        ),
        "word6": MagicMock(
            word="开心",
            chaotong_level=25,
            part_of_speech="形容词",
            characters=[
                {"character": "开", "part_of_speech": "v"},
                {"character": "心", "part_of_speech": "n"},
            ],
        ),
    }
    return mock_service


def test_calculate_literacy_rate_no_chinese(mock_word_service):
    """
    测试当文本中没有中文的情况
    """
    calculator = LiteracyCalculator(mock_word_service)
    known_rate, unknown_rate = calculator.calculate_literacy_rate("hello world", 10)
    assert pytest.approx(known_rate, 0.0001) == 1.0
    assert pytest.approx(unknown_rate, 0.0001) == 0.0


def test_calculate_literacy_rate_level_1(mock_word_service):
    """
    测试当目标级别为1的情况
    """
    calculator = LiteracyCalculator(mock_word_service)
    known_rate, unknown_rate = calculator.calculate_literacy_rate("你好", 1)
    assert pytest.approx(known_rate, 0.0001) == 1.0  # 你, 好
    assert pytest.approx(unknown_rate, 0.0001) == 0.0


def test_calculate_literacy_rate_level_5(mock_word_service):
    """
    测试当目标级别为5的情况
    """
    calculator = LiteracyCalculator(mock_word_service)
    known_rate, unknown_rate = calculator.calculate_literacy_rate("我喜欢跑步", 5)
    assert pytest.approx(known_rate, 0.0001) == 2 / 5  # 喜, 欢
    assert pytest.approx(unknown_rate, 0.0001) == 3 / 5


def test_calculate_literacy_rate_level_10(mock_word_service):
    """
    测试当目标级别为10的情况
    """
    calculator = LiteracyCalculator(mock_word_service)
    known_rate, unknown_rate = calculator.calculate_literacy_rate("我喜欢跑步", 10)
    assert pytest.approx(known_rate, 0.0001) == 4 / 5  # 喜, 欢, 跑, 步
    assert pytest.approx(unknown_rate, 0.0001) == 1 / 5


def test_calculate_literacy_rate_level_20(mock_word_service):
    """
    测试当目标级别为20的情况
    """
    calculator = LiteracyCalculator(mock_word_service)
    known_rate, unknown_rate = calculator.calculate_literacy_rate(
        "今天天气真好，白云很多，我去跑步了，结果白跑了。", 20
    )
    known_chars = {"你", "好", "喜", "欢", "跑", "步", "公", "园"}
    text_chars = re.findall(
        r"[\u4e00-\u9fff]", "今天天气真好，白云很多，我去跑步了，结果白跑了。"
    )
    expected_known_count = sum(1 for char in text_chars if char in known_chars)
    expected_known_rate = expected_known_count / len(text_chars)

    assert pytest.approx(known_rate, 0.0001) == expected_known_rate
