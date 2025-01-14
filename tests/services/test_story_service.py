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
        word="喜欢",
        part_of_speech="动词",
        characters=[
            {"character": "喜", "part_of_speech": "ADJ"},
            {"character": "欢", "part_of_speech": "ADJ"},
        ],
    )
    mock_service.get_key_words_by_ids.return_value = [
        {
            "word": "喜欢",
            "pinyin": None,
            "definition": None,
            "part_of_speech": "动词",
            "example": None,
        }
    ]
    return mock_service


@pytest.fixture
def mock_scene_service():
    """
    创建一个模拟的 scene_service 对象，用于测试
    """
    mock_service = MagicMock()
    mock_service.get_scene_by_id.return_value = MagicMock(
        id="scene1", name="测试场景", description="这是一个测试场景"
    )
    return mock_service


@pytest.fixture
def mock_literacy_calculator():
    """
    创建一个模拟的 LiteracyCalculator 对象，用于测试
    """
    mock_calculator = MagicMock()
    mock_calculator.calculate_literacy_rate.return_value = (0.8, 0.2)
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
                    content='{"title": "测试故事", "content": "这是一个测试故事", "key_words": [{"word": "喜欢"}]}'
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


def test_generate_story(story_service):
    """
    测试生成故事
    """
    story = story_service.generate_story(
        vocabulary_level=30,
        scene_id="scene1",
        story_word_count=100,
        new_char_rate=0.2,
        key_word_ids=["word1"],
        new_char_rate_tolerance=0.1,
        word_count_tolerance=0.2,
        story_word_count_tolerance=20,
        request_limit=100,
    )
    assert story is not None
    assert story.title == "测试故事"
    assert story.content == "这是一个测试故事"
    assert len(story.key_words) == 1
    assert story.key_words[0]["word"] == "喜欢"


def test_adjust_story_level(story_service):
    """
    测试调整故事级别
    """
    pass


def test_generate_story_with_invalid_parameters(story_service):
    """
    测试生成故事时，使用无效的参数
    """
    pass


def test_adjust_story_level_with_invalid_parameters(story_service):
    """
    测试调整故事级别时，使用无效的参数
    """
    pass


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
            new_char_rate=0.2,
            key_word_ids=["word1"],
            new_char_rate_tolerance=0.1,
            word_count_tolerance=0.2,
            story_word_count_tolerance=20,
            request_limit=100,
        )


def test_generate_story_with_invalid_json_response(story_service, mock_deepseek_client):
    """
    测试生成故事时，AI 返回无效的 JSON 格式
    """
    mock_deepseek_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"title": "测试故事", "content": "这是一个测试故事", "key_words": [{"word": "喜欢"}]'
                )
            )
        ]
    )
    with pytest.raises(Exception, match="AI 服务返回无效的 JSON 格式"):
        story_service.generate_story(
            vocabulary_level=30,
            scene_id="scene1",
            story_word_count=100,
            new_char_rate=0.2,
            key_word_ids=["word1"],
            new_char_rate_tolerance=0.1,
            word_count_tolerance=0.2,
            story_word_count_tolerance=20,
            request_limit=100,
        )
