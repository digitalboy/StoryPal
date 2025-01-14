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


TEST_WORDS_DATA = load_test_data("tests/data/test_words.json")
TEST_SCENES_DATA = load_test_data("tests/data/test_scenes.json")


@pytest.fixture
def story_service():
    # 替换 Config 中的文件路径为测试数据文件路径
    Config.WORDS_FILE_PATH = "tests/data/test_words.json"
    Config.SCENES_FILE_PATH = "tests/data/test_scenes.json"
    # 创建 StoryService 实例
    return StoryService()


@pytest.fixture
def mock_deepseek_api():
    """
    模拟 DeepSeek API 的返回值
    """
    with patch("app.services.story_service.DeepSeekClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.chat.completions.create.return_value.choices[
            0
        ].message.content = json.dumps(
            {
                "title": "测试故事",
                "content": "这是一个测试故事，包含一些测试词汇。",
                "key_words": [
                    {
                        "word": "测试",
                        "pinyin": None,
                        "definition": None,
                        "part_of_speech": "v",
                        "example": None,
                    }
                ],
            }
        )
        yield mock_client


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


# 测试故事生成
def test_generate_story(story_service, mock_deepseek_api):
    # 模拟 API 返回
    story = story_service.generate_story(
        vocabulary_level=10,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=100,
        new_char_rate=0.2,
        key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],  # "喜欢"的id
    )
    assert story is not None
    assert story.title == "测试故事"
    assert story.content == "这是一个测试故事，包含一些测试词汇。"
    assert len(story.key_words) == 1
    assert story.key_words[0]["word"] == "测试"
    assert story.vocabulary_level == 10
    assert story.scene == "f0e9d8c7-b6a5-4321-9876-543210fedcba"
    assert story.word_count > 0
    assert 0 <= story.new_char_rate <= 1
    assert story.new_char >= 0


# 测试故事生成参数验证
def test_generate_story_with_invalid_params(story_service):
    with pytest.raises(ValueError) as exc_info:
        story_service.generate_story(
            vocabulary_level=101,
            scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
            story_word_count=100,
            new_char_rate=0.2,
            key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],
        )
    assert "Validation failed: 'vocabulary_level' must be between 1 and 100" in str(
        exc_info.value
    )

    with pytest.raises(ValueError) as exc_info:
        story_service.generate_story(
            vocabulary_level=10,
            scene_id="invalid_scene_id",
            story_word_count=100,
            new_char_rate=0.2,
            key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],
        )
    assert "Validation failed: 'scene_id' must be a valid UUID" in str(exc_info.value)
    with pytest.raises(ValueError) as exc_info:
        story_service.generate_story(
            vocabulary_level=10,
            scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
            story_word_count=0,
            new_char_rate=0.2,
            key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],
        )
    assert "Validation failed: 'story_word_count' must be greater than 0" in str(
        exc_info.value
    )
    with pytest.raises(ValueError) as exc_info:
        story_service.generate_story(
            vocabulary_level=10,
            scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
            story_word_count=100,
            new_char_rate=2,
            key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],
        )
    assert "Validation failed: 'new_char_rate' must be between 0 and 1" in str(
        exc_info.value
    )


# 测试故事调整
def test_adjust_story(story_service, mock_deepseek_api):
    story = story_service.generate_story(
        vocabulary_level=10,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=100,
        new_char_rate=0.2,
        key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],
    )
    adjusted_story = story_service.adjust_story(story.id, target_level=20)
    assert adjusted_story is not None
    assert adjusted_story.vocabulary_level == 20
    assert adjusted_story.content != story.content  # 确保调整后的故事内容发生变化


# 测试多轮对话
def test_generate_story_with_multi_turn_conversation(story_service, mock_deepseek_api):
    story = story_service.generate_story(
        vocabulary_level=10,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=100,
        new_char_rate=0.2,
        key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],
    )
    assert story is not None
    # 验证状态机状态
    assert story_service.state == "FINAL_INSTRUCTION"


# 测试 key_words 查询
def test_get_key_words_by_ids(story_service):
    key_words = story_service.get_key_words_by_ids(
        ["a1b2c3d4-e5f6-7890-1234-567890abcde1", "f0e9d8c7-b6a5-4321-9876-543210fedcb1"]
    )
    assert len(key_words) == 2
    assert key_words[0]["word"] == "喜欢"
    assert key_words[1]["word"] == "跑步"


def test_get_key_words_by_ids_not_exist(story_service):
    key_words = story_service.get_key_words_by_ids(["not_exist_id"])
    assert len(key_words) == 0


# 测试 words.json 文件加载失败
def test_load_words_file_not_found():
    Config.WORDS_FILE_PATH = "not_exist.json"
    with pytest.raises(FileNotFoundError) as exc_info:
        StoryService()
    assert "No such file or directory" in str(exc_info.value)


# 测试 DeepSeek API 调用失败
def test_generate_story_deepseek_api_failed(story_service, mock_deepseek_api):
    mock_deepseek_api.return_value.chat.completions.create.side_effect = Exception(
        "DeepSeek API failed"
    )
    with pytest.raises(Exception) as exc_info:
        story_service.generate_story(
            vocabulary_level=10,
            scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
            story_word_count=100,
            new_char_rate=0.2,
            key_word_ids=["a1b2c3d4-e5f6-7890-1234-567890abcde1"],
        )
    assert "DeepSeek API failed" in str(exc_info.value)
