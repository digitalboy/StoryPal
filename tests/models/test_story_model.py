# tests/models/test_story_model.py
from app.models.story_model import StoryModel
from datetime import datetime


def test_story_model_creation(sample_story):
    assert sample_story.story_id == "test_story_id"
    assert sample_story.title == "测试故事"
    assert sample_story.content == "这是一个用于测试的故事"
    assert sample_story.vocabulary_level == 20
    assert sample_story.scene == "test_scene_id"
    assert sample_story.word_count == 100
    assert sample_story.new_char_rate == 0.1
    assert sample_story.new_char == 10
    assert sample_story.key_words == [
        {
            "word": "测试",
            "pinyin": None,
            "definition": None,
            "part_of_speech": "动词",
            "example": None,
        }
    ]
    assert isinstance(sample_story.created_at, str)
    try:
        datetime.fromisoformat(sample_story.created_at.replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"


def test_story_model_to_dict(sample_story):
    story_dict = sample_story.to_dict()
    assert story_dict["story_id"] == "test_story_id"
    assert story_dict["title"] == "测试故事"
    assert story_dict["content"] == "这是一个用于测试的故事"
    assert story_dict["vocabulary_level"] == 20
    assert story_dict["scene"] == "test_scene_id"
    assert story_dict["word_count"] == 100
    assert story_dict["new_char_rate"] == 0.1
    assert story_dict["new_char"] == 10
    assert story_dict["key_words"] == [
        {
            "word": "测试",
            "pinyin": None,
            "definition": None,
            "part_of_speech": "动词",
            "example": None,
        }
    ]
    assert isinstance(story_dict["created_at"], str)
    try:
        datetime.fromisoformat(story_dict["created_at"].replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"


def test_story_model_from_dict(sample_story):
    story_dict = sample_story.to_dict()
    new_story = StoryModel.from_dict(story_dict)
    assert new_story.story_id == "test_story_id"
    assert new_story.title == "测试故事"
    assert new_story.content == "这是一个用于测试的故事"
    assert new_story.vocabulary_level == 20
    assert new_story.scene == "test_scene_id"
    assert new_story.word_count == 100
    assert new_story.new_char_rate == 0.1
    assert new_story.new_char == 10
    assert new_story.key_words == [
        {
            "word": "测试",
            "pinyin": None,
            "definition": None,
            "part_of_speech": "动词",
            "example": None,
        }
    ]
    assert isinstance(new_story.created_at, str)
    try:
        datetime.fromisoformat(new_story.created_at.replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"
    assert new_story.created_at == sample_story.created_at
