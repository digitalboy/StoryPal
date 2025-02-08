# tests/services/test_story_service.py
import pytest
from unittest.mock import MagicMock

from app.services.story_service import StoryService


@pytest.fixture
def mock_word_service():
    """
    创建一个模拟的 word_service 对象，用于测试
    """
    mock_service = MagicMock()
    mock_service.get_word_by_id.return_value = MagicMock(
        word="喜欢", part_of_speech="动词"
    )  # 简化
    mock_service.get_key_words_by_ids.return_value = [
        {
            "word": "喜欢",
            "pinyin": None,
            "definition": None,
            "part_of_speech": "动词",
            "example": None,
        }
    ]
    mock_service.get_known_words.return_value = [
        ("你好", "PHR"),
        ("喜欢", "V"),
    ]  # 模拟已知词汇
    return mock_service


@pytest.fixture
def mock_scene_service():
    """
    创建一个模拟的 scene_service 对象，用于测试
    """
    mock_service = MagicMock()
    mock_service.get_scene_by_id.return_value = MagicMock(
        id="scene1", description="这是一个测试场景"
    )  # 简化
    return mock_service


@pytest.fixture
def mock_literacy_calculator():
    """
    创建一个模拟的 LiteracyCalculator 对象，用于测试
    """
    mock_calculator = MagicMock()
    mock_calculator.calculate_vocabulary_rate.return_value = (
        0.8,
        0.2,
        "",
    )  # 添加 message
    return mock_calculator


@pytest.fixture
def mock_deepseek_client():
    """
    创建一个模拟的 DeepSeek 客户端，用于测试
    """
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"title": "测试故事", "content": "你好喜欢", "key_words": [{"word": "喜欢"}]}'
                )
            )
        ]
    )
    return mock_client


@pytest.fixture
def story_service(
    mock_word_service,
    mock_scene_service,
    mock_literacy_calculator,
    mock_deepseek_client,
):
    """
    创建一个 StoryService 对象，用于测试
    """
    return StoryService(
        mock_word_service,
        mock_scene_service,
        mock_literacy_calculator,
        mock_deepseek_client,
    )


def test_generate_story(
    story_service, mock_word_service, mock_scene_service, mock_literacy_calculator
):
    """
    测试生成故事
    """
    target_new_word_rate = 0.2  # 设置目标生词率
    story = story_service.generate_story(
        vocabulary_level=30,
        scene_id="scene1",
        story_word_count=100,
        new_word_rate=target_new_word_rate,  # 设置目标生词率
        key_word_ids=["word1"],
        new_word_rate_tolerance=0.1,
        story_word_count_tolerance=20,
        request_limit=100,
    )
    assert story is not None
    assert story.title == "测试故事"
    assert story.content == "你好喜欢"
    assert len(story.key_words) == 1
    assert story.key_words[0]["word"] == "喜欢"

    # 验证 mock 调用
    mock_scene_service.get_scene_by_id.assert_called_once_with("scene1")
    mock_word_service.get_key_words_by_ids.assert_called_once_with(["word1"])
    mock_literacy_calculator.calculate_vocabulary_rate.assert_called_once_with(
        "你好喜欢", 30
    )


def test_generate_story_with_ai_error(story_service, mock_deepseek_client):
    """
    测试生成故事时，AI 服务调用失败
    """
    mock_deepseek_client.chat.completions.create.side_effect = Exception(
        "AI 服务调用失败"
    )
    with pytest.raises(Exception, match="AI 服务调用失败"):
        story_service.generate_story(
            vocabulary_level=30,
            scene_id="scene1",
            story_word_count=100,
            new_word_rate=0.2,
            key_word_ids=["word1"],
            new_word_rate_tolerance=0.1,
            story_word_count_tolerance=20,
            request_limit=100,
        )


def test_generate_story_with_invalid_json_response(story_service, mock_deepseek_client):
    """
    测试生成故事时，AI 返回无效的 JSON 格式
    """
    mock_deepseek_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="invalid json"))]
    )  # 模拟无效 JSON
    with pytest.raises(Exception, match="AI 服务返回无效的 JSON 格式"):
        story_service.generate_story(
            vocabulary_level=30,
            scene_id="scene1",
            story_word_count=100,
            new_word_rate=0.2,
            key_word_ids=["word1"],
            new_word_rate_tolerance=0.1,
            story_word_count_tolerance=20,
            request_limit=100,
        )


def test_generate_story_scene_not_found(story_service, mock_scene_service):
    """
    测试生成故事时，场景未找到
    """
    mock_scene_service.get_scene_by_id.return_value = None
    with pytest.raises(Exception, match="Scene id scene1 not found"):
        story_service.generate_story(
            vocabulary_level=30,
            scene_id="scene1",
            story_word_count=100,
            new_word_rate=0.2,
            key_word_ids=["word1"],
            new_word_rate_tolerance=0.1,
            story_word_count_tolerance=20,
            request_limit=100,
        )


def test_validate_story(story_service, mock_literacy_calculator):
    """测试 _validate_story 函数"""
    from app.models.story_model import StoryModel

    # 创建一个模拟的故事
    target_new_word_rate = 0.2  # 设置目标生词率
    story = StoryModel(
        title="测试故事",
        content="你好喜欢跑步",
        vocabulary_level=30,
        scene="scene1",
        story_word_count=3,
        new_word_rate=target_new_word_rate,  # 使用目标生词率
        new_words=1,
        key_words=[{"word": "喜欢"}],
    )
    # 测试用例 1: 验证通过
    mock_literacy_calculator_return_value_1 = (
        0.8,
        target_new_word_rate,  # 0.2， 模拟实际生词率等于目标生词率
        "",
    )
    mock_literacy_calculator.calculate_vocabulary_rate.return_value = (
        mock_literacy_calculator_return_value_1
    )
    story.new_word_rate = mock_literacy_calculator_return_value_1[
        1
    ]  #  更新 story.new_word_rate 为 mock 返回值
    #  调用函数
    story_service.literacy_calculator.calculate_vocabulary_rate(
        story.content, story.vocabulary_level
    )

    is_valid = story_service._validate_story(
        story,
        target_new_word_rate,  # 传入目标生词率
        new_word_rate_tolerance=0.2,
        story_word_count_tolerance=1,
    )
    assert is_valid == True
    mock_literacy_calculator.calculate_vocabulary_rate.assert_called()  # 确保调用的验证

    # 测试用例 2:   生词率超出范围
    mock_literacy_calculator_return_value_2 = (
        0.0,
        1.0,  # 模拟实际生词率超出范围
        "",
    )
    mock_literacy_calculator.calculate_vocabulary_rate.return_value = (
        mock_literacy_calculator_return_value_2
    )
    story.new_word_rate = mock_literacy_calculator_return_value_2[
        1
    ]  #  更新 story.new_word_rate 为 mock 返回值
    #  调用函数
    story_service.literacy_calculator.calculate_vocabulary_rate(
        story.content, story.vocabulary_level
    )

    is_valid = story_service._validate_story(
        story,
        target_new_word_rate,  # 传入目标生词率
        new_word_rate_tolerance=0.1,
    )
    assert is_valid == False
    mock_literacy_calculator.calculate_vocabulary_rate.assert_called()  # 确保调用的验证
