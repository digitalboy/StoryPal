# tests/models/test_word_model.py
from app.models.word_model import WordModel
from datetime import datetime


def test_word_model_creation(sample_word):
    assert sample_word.word_id == "test_word_id"
    assert sample_word.word == "测试"
    assert sample_word.chaotong_level == 10
    assert sample_word.part_of_speech == "名词"
    assert sample_word.hsk_level == 1
    assert sample_word.characters == [
        {"character": "测", "part_of_speech": "v"},
        {"character": "试", "part_of_speech": "n"},
    ]
    assert isinstance(sample_word.created_at, str)
    try:
        datetime.fromisoformat(sample_word.created_at.replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"


def test_word_model_to_dict(sample_word):
    word_dict = sample_word.to_dict()
    assert word_dict["word_id"] == "test_word_id"
    assert word_dict["word"] == "测试"
    assert word_dict["chaotong_level"] == 10
    assert word_dict["part_of_speech"] == "名词"
    assert word_dict["hsk_level"] == 1
    assert word_dict["characters"] == [
        {"character": "测", "part_of_speech": "v"},
        {"character": "试", "part_of_speech": "n"},
    ]
    assert isinstance(word_dict["created_at"], str)
    try:
        datetime.fromisoformat(word_dict["created_at"].replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"


def test_word_model_from_dict(sample_word):
    word_dict = sample_word.to_dict()
    new_word = WordModel.from_dict(word_dict)
    assert new_word.word_id == "test_word_id"
    assert new_word.word == "测试"
    assert new_word.chaotong_level == 10
    assert new_word.part_of_speech == "名词"
    assert new_word.hsk_level == 1
    assert new_word.characters == [
        {"character": "测", "part_of_speech": "v"},
        {"character": "试", "part_of_speech": "n"},
    ]
    assert isinstance(new_word.created_at, str)
    try:
        datetime.fromisoformat(new_word.created_at.replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"
    assert new_word.created_at == sample_word.created_at
