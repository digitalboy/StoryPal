# tests/services/test_story_service.py
import pytest
from app.services.story_service import StoryService
from unittest.mock import patch, MagicMock
from app.config import Config


@pytest.fixture
def story_service():
    return StoryService()


def test_calculate_literacy_rate(story_service):
    text = "你好，我喜欢跑步。"
    known_rate, unknown_rate = story_service._calculate_literacy_rate(text, 20)
    assert known_rate > 0
    assert unknown_rate < 1


def test_calculate_literacy_rate_empty_text(story_service):
    text = ""
    known_rate, unknown_rate = story_service._calculate_literacy_rate(text, 20)
    assert known_rate == 1
    assert unknown_rate == 0


def test_load_known_words(story_service):
    known_words_dict = story_service._load_known_words(20)
    assert len(known_words_dict) > 0
    assert "好" in known_words_dict
    assert "跑" in known_words_dict
    assert "早" in known_words_dict
    assert "公" in known_words_dict


def test_generate_prompt(story_service):
    prompt_messages = story_service._generate_prompt(
        vocabulary_level=10,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=100,
        key_word_ids=[
            "a1b2c3d4-e5f6-7890-1234-567890abcde1",
            "f0e9d8c7-b6a5-4321-9876-543210fedcb1",
        ],
    )
    assert len(prompt_messages) == 3
    assert "你是一个专业的中文故事生成器" in prompt_messages[0]["content"]
    assert "以下是一些已知词汇，你可以参考" in prompt_messages[1]["content"]
    assert "请你根据以上需求，编写故事" in prompt_messages[2]["content"]


def test_generate_prompt_scene_not_found(story_service):
    prompt_messages = story_service._generate_prompt(
        vocabulary_level=10,
        scene_id="non_existent_id",
        story_word_count=100,
        key_word_ids=[
            "a1b2c3d4-e5f6-7890-1234-567890abcde1",
            "f0e9d8c7-b6a5-4321-9876-543210fedcb1",
        ],
    )
    assert prompt_messages is None


def test_generate_prompt_key_word_not_found(story_service):
    prompt_messages = story_service._generate_prompt(
        vocabulary_level=10,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=100,
        key_word_ids=["non_existent_id", "f0e9d8c7-b6a5-4321-9876-543210fedcb1"],
    )
    assert prompt_messages is None


@patch("app.services.story_service.DeepSeekAPI.chat_completions")
def test_generate_story_success(mock_chat_completions, story_service):
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": """
                     {
                         "title": "测试故事",
                         "content": "你好，我喜欢跑步。",
                         "key_words": [
                             {
                                "word": "喜欢",
                                "pinyin": null,
                                "definition": null,
                                 "part_of_speech": "动词",
                                "example": null
                            },
                            {
                              "word": "跑步",
                                "pinyin": null,
                              "definition": null,
                               "part_of_speech": "动词",
                              "example": null
                             }
                          ]
                     }
                     """
                }
            }
        ]
    }
    mock_chat_completions.return_value = mock_response
    story = story_service.generate_story(
        vocabulary_level=20,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=10,
        new_char_rate=0.2,
        key_word_ids=[
            "a1b2c3d4-e5f6-7890-1234-567890abcde1",
            "f0e9d8c7-b6a5-4321-9876-543210fedcb1",
        ],
    )
    assert story.title == "测试故事"
    assert story.content == "你好，我喜欢跑步。"
    assert story.vocabulary_level == 20
    assert story.scene == "f0e9d8c7-b6a5-4321-9876-543210fedcba"
    assert story.word_count == 7
    assert story.new_char_rate < 1
    assert story.new_char > 0
    assert len(story.key_words) > 0
    mock_chat_completions.assert_called_once()


@patch("app.services.story_service.DeepSeekAPI.chat_completions")
def test_generate_story_failed_deepseek_api(mock_chat_completions, story_service):
    mock_chat_completions.side_effect = Exception("DeepSeek API Error")
    story = story_service.generate_story(
        vocabulary_level=20,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=10,
        new_char_rate=0.2,
        key_word_ids=[
            "a1b2c3d4-e5f6-7890-1234-567890abcde1",
            "f0e9d8c7-b6a5-4321-9876-543210fedcb1",
        ],
    )
    assert story is None


@patch("app.services.story_service.DeepSeekAPI.chat_completions")
def test_generate_story_failed_json_parse(mock_chat_completions, story_service):
    mock_response = {"choices": [{"message": {"content": "invalid json"}}]}
    mock_chat_completions.return_value = mock_response
    story = story_service.generate_story(
        vocabulary_level=20,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=10,
        new_char_rate=0.2,
        key_word_ids=[
            "a1b2c3d4-e5f6-7890-1234-567890abcde1",
            "f0e9d8c7-b6a5-4321-9876-543210fedcb1",
        ],
    )
    assert story is None


@patch("app.services.story_service.DeepSeekAPI.chat_completions")
def test_generate_story_failed_missing_field(mock_chat_completions, story_service):
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": """
                     {
                         "title": "测试故事",
                         "content": "你好，我喜欢跑步。"
                     }
                     """
                }
            }
        ]
    }
    mock_chat_completions.return_value = mock_response
    story = story_service.generate_story(
        vocabulary_level=20,
        scene_id="f0e9d8c7-b6a5-4321-9876-543210fedcba",
        story_word_count=10,
        new_char_rate=0.2,
        key_word_ids=[
            "a1b2c3d4-e5f6-7890-1234-567890abcde1",
            "f0e9d8c7-b6a5-4321-9876-543210fedcb1",
        ],
    )
    assert story is None
