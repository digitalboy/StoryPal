# tests/services/test_word_service.py
import pytest
from app.services.word_service import WordService
from app.models.word_model import WordModel
from unittest.mock import patch


@pytest.fixture
def word_service():
    return WordService()


def test_load_words_success(word_service):
    assert len(word_service.words) > 0


def test_load_words_not_found():
    with patch("app.services.word_service.Config.WORDS_FILE_PATH", "non_existent.json"):
        word_service = WordService()
        assert len(word_service.words) == 0


def test_get_word_success(word_service):
    word = word_service.get_word("a1b2c3d4-e5f6-7890-1234-567890abcdef")
    assert word.word == "你好"


def test_get_word_not_found(word_service):
    word = word_service.get_word("non_existent_id")
    assert word is None


def test_list_words_all(word_service):
    words = word_service.list_words()
    assert len(words) > 0


def test_list_words_with_level(word_service):
    words = word_service.list_words(level=10)
    assert len(words) == 3
    assert all(word.chaotong_level <= 10 for word in words)


def test_list_words_with_part_of_speech(word_service):
    words = word_service.list_words(part_of_speech="名词")
    assert len(words) == 2
    assert all(word.part_of_speech == "名词" for word in words)


def test_list_words_with_level_and_part_of_speech(word_service):
    words = word_service.list_words(level=20, part_of_speech="名词")
    assert len(words) == 1
    assert all(word.chaotong_level <= 20 for word in words)
    assert all(word.part_of_speech == "名词" for word in words)


def test_add_word(word_service):
    new_word_data = {
        "word_id": "test_add_word_id",
        "word": "测试添加",
        "chaotong_level": 30,
        "part_of_speech": "动词",
        "hsk_level": 5,
        "characters": [
            {"character": "测", "part_of_speech": "v"},
            {"character": "试", "part_of_speech": "n"},
        ],
    }
    new_word = word_service.add_word(new_word_data)
    assert new_word.word == "测试添加"
    assert word_service.get_word("test_add_word_id") == new_word


def test_update_word(word_service):
    updated_word_data = {
        "word": "更新测试",
        "chaotong_level": 40,
        "part_of_speech": "形容词",
        "hsk_level": 6,
        "characters": [
            {"character": "更", "part_of_speech": "v"},
            {"character": "新", "part_of_speech": "a"},
            {"character": "测", "part_of_speech": "v"},
            {"character": "试", "part_of_speech": "n"},
        ],
    }
    updated_word = word_service.update_word(
        "a1b2c3d4-e5f6-7890-1234-567890abcdef", updated_word_data
    )
    assert updated_word.word == "更新测试"
    assert updated_word.chaotong_level == 40
    assert updated_word.part_of_speech == "形容词"
    assert updated_word.hsk_level == 6
    assert updated_word.characters == [
        {"character": "更", "part_of_speech": "v"},
        {"character": "新", "part_of_speech": "a"},
        {"character": "测", "part_of_speech": "v"},
        {"character": "试", "part_of_speech": "n"},
    ]


def test_update_word_not_found(word_service):
    updated_word = word_service.update_word("non_existent_id", {"word": "更新测试"})
    assert updated_word is None


def test_delete_word(word_service):
    deleted_word = word_service.delete_word("a1b2c3d4-e5f6-7890-1234-567890abcdef")
    assert deleted_word.word == "你好"
    assert word_service.get_word("a1b2c3d4-e5f6-7890-1234-567890abcdef") is None


def test_delete_word_not_found(word_service):
    deleted_word = word_service.delete_word("non_existent_id")
    assert deleted_word is None
