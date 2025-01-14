# tests/conftest.py
import pytest
from datetime import datetime


@pytest.fixture
def sample_word_data():
    return {
        "word_id": "test_word_id",
        "word": "测试",
        "chaotong_level": 10,
        "part_of_speech": "名词",
        "hsk_level": 1,
        "characters": [
            {"character": "测", "part_of_speech": "v"},
            {"character": "试", "part_of_speech": "n"},
        ],
    }


@pytest.fixture
def sample_scene_data():
    return {
        "scene_id": "test_scene_id",
        "name": "测试场景",
        "description": "这是一个用于测试的场景",
    }


@pytest.fixture
def sample_story_data():
    return {
        "story_id": "test_story_id",
        "title": "测试故事",
        "content": "这是一个用于测试的故事",
        "vocabulary_level": 20,
        "scene": "test_scene_id",
        "word_count": 100,
        "new_char_rate": 0.1,
        "new_char": 10,
        "key_words": [
            {
                "word": "测试",
                "pinyin": None,
                "definition": None,
                "part_of_speech": "动词",
                "example": None,
            }
        ],
    }
