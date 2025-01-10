# filepath: tests/test_word_service.py
import pytest
from app.services.word_service import WordService
from app.models.word_model import Word


@pytest.fixture
def word_service():
    """Fixture to initialize WordService."""
    return WordService()


@pytest.fixture
def test_word():
    """Fixture to create a test word."""
    word = Word(
        word="公园",
        pinyin="gōngyuán",
        definition="public park",
        part_of_speech="名词",
        chaotong_level=35,
        characters=[{"character": "公", "pinyin": "gōng", "definition": "public"}],
        example="我们去公园玩吧。",
    )
    word.save()
    return word


def test_get_words_by_level(word_service, test_word):
    """Test getting words by chaotong level."""
    words = word_service.get_words_by_level(35)
    assert len(words) >= 1
    assert words[0]["word"] == "公园"
    assert words[0]["chaotong_level"] == 35


def test_get_words_by_part_of_speech(word_service, test_word):
    """Test getting words by part of speech."""
    words = word_service.get_words_by_part_of_speech("名词")
    assert len(words) >= 1
    assert words[0]["word"] == "公园"
    assert words[0]["part_of_speech"] == "名词"


def test_get_words_by_level_not_found(word_service):
    """Test getting words by a non-existent chaotong level."""
    words = word_service.get_words_by_level(999)  # 假设 999 级别不存在
    assert len(words) == 0


def test_get_words_by_part_of_speech_not_found(word_service):
    """Test getting words by a non-existent part of speech."""
    words = word_service.get_words_by_part_of_speech(
        "未知词性"
    )  # 假设 "未知词性" 不存在
    assert len(words) == 0
