# tests/services/test_story_service.py
import pytest
import json
from unittest.mock import patch, MagicMock
from app.services.story_service import StoryService
from app.config import Config
from app.models.word_model import WordModel
from app.utils.error_handling import handle_error
import os
from jinja2 import Template


# 加载测试数据
def load_test_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        pytest.fail(f"Failed to load test data from {file_path}: {e}")
        return None


@pytest.fixture
def story_service():
    # 使用 app/data 目录下的文件
    Config.WORDS_FILE_PATH = "app/data/words.json"
    Config.SCENES_FILE_PATH = "app/data/scenes.json"
    # 创建 StoryService 实例
    return StoryService()


# 测试生字率计算
@pytest.mark.parametrize(
    "text, target_level, expected_known_rate, expected_unknown_rate",
    [
        ("你好", 1, 1, 0),  # 文本中只有已知字
        ("你好世界", 1, 0.5, 0.5),  # 部分已知，部分未知
        ("你好世界", 10, 0.5, 0.5),  # 部分已知，部分未知
        ("我喜欢跑步", 10, 1, 0),  # 文本中只有已知字
        ("我喜欢游泳", 10, 0.5, 0.5),  # 文本中有生字
        ("", 10, 1, 0),  # 文本为空
        ("今天天气真好", 10, 0, 1),  # 文本中只有生字
        ("今天天气真好。", 10, 0, 1),  # 文本中包含标点符号
        ("你好，我喜欢跑步。", 10, 1, 0),  # 文本中包含标点符号
        ("白色，白说", 10, 0.5, 0.5),  # 同一个字在不同词性下，计算生字率
        ("我喜欢跑步，我喜欢跑步", 10, 1, 0),  #  文本中包含重复的词
    ],
)
def test_calculate_literacy_rate(
    story_service, text, target_level, expected_known_rate, expected_unknown_rate
):
    known_rate, unknown_rate = story_service._calculate_literacy_rate(
        text, target_level
    )
    assert round(known_rate, 2) == expected_known_rate
    assert round(unknown_rate, 2) == expected_unknown_rate
