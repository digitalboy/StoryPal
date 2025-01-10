# filepath: tests/test_stories.py
import pytest
from app import create_app
import json
from app.models.story_model import Story


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


def clear_json_file(filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([], f)


@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    clear_json_file("data/stories.json")
    yield


def test_get_story(client):
    """测试获取故事 API"""
    data = {
        "title": "测试故事",
        "content": "这是一个测试故事",
        "vocabulary_level": 1,
        "scene_id": "test_scene_id",
        "word_count": 100,
        "new_words": [],
        "new_char_rate": 0.1,
        "key_words": [],
    }
    response = client.post("/v1/stories/generate", json=data)
    story_id = response.json["data"]["story_id"]
    response = client.get(f"/v1/stories/{story_id}")
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert response.json["data"]["title"] == "测试故事"


def test_get_story_not_found(client):
    """测试获取故事 API，故事不存在"""
    response = client.get("/v1/stories/non_existent_id")
    assert response.status_code == 404
    assert response.json["code"] == 4043
    assert response.json["message"] == "Story not found"


def test_update_story(client):
    """测试更新故事 API"""
    data = {
        "title": "测试故事",
        "content": "这是一个测试故事",
        "vocabulary_level": 1,
        "scene_id": "test_scene_id",
        "word_count": 100,
        "new_words": [],
        "new_char_rate": 0.1,
        "key_words": [],
    }
    response = client.post("/v1/stories/generate", json=data)
    story_id = response.json["data"]["story_id"]
    update_data = {"title": "更新后的故事", "content": "这是更新后的故事"}
    response = client.put(f"/v1/stories/{story_id}", json=update_data)
    assert response.status_code == 200
    assert response.json["code"] == 200
    response = client.get(f"/v1/stories/{story_id}")
    assert response.json["data"]["title"] == "更新后的故事"
    assert response.json["data"]["content"] == "这是更新后的故事"


def test_update_story_not_found(client):
    """测试更新故事 API，故事不存在"""
    update_data = {"title": "更新后的故事", "content": "这是更新后的故事"}
    response = client.put("/v1/stories/non_existent_id", json=update_data)
    assert response.status_code == 404
    assert response.json["code"] == 4043
    assert response.json["message"] == "Story not found"


def test_delete_story(client):
    """测试删除故事 API"""
    data = {
        "title": "测试故事",
        "content": "这是一个测试故事",
        "vocabulary_level": 1,
        "scene_id": "test_scene_id",
        "word_count": 100,
        "new_words": [],
        "new_char_rate": 0.1,
        "key_words": [],
    }
    response = client.post("/v1/stories/generate", json=data)
    story_id = response.json["data"]["story_id"]
    response = client.delete(f"/v1/stories/{story_id}")
    assert response.status_code == 200
    assert response.json["code"] == 200
    response = client.get(f"/v1/stories/{story_id}")
    assert response.status_code == 404


def test_delete_story_not_found(client):
    """测试删除故事 API，故事不存在"""
    response = client.delete("/v1/stories/non_existent_id")
    assert response.status_code == 404
    assert response.json["code"] == 4043
    assert response.json["message"] == "Story not found"


def test_generate_story(client):
    """测试生成故事 API"""
    data = {
        "vocabulary_level": 35,
        "scene_id": "test_scene_id",
        "word_count": 120,
        "new_char_rate": 0.02,
    }
    response = client.post("/v1/stories/generate", json=data)
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert "story_id" in response.json["data"]
    story_id = response.json["data"]["story_id"]
    story = Story.find_by_id(story_id)
    assert story
    assert story.vocabulary_level == 35
    assert story.word_count == 120


def test_generate_story_missing_required_fields(client):
    """测试生成故事 API，缺少必填字段"""
    data = {
        "scene_id": "test_scene_id",
        "word_count": 120,
        "new_char_rate": 0.02,
    }
    response = client.post("/v1/stories/generate", json=data)
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "缺少必填字段: vocabulary_level"


def test_generate_story_invalid_vocabulary_level(client):
    """测试生成故事API，vocabulary_level 超出范围"""
    data = {
        "vocabulary_level": 101,
        "scene_id": "test_scene_id",
        "word_count": 120,
        "new_char_rate": 0.02,
    }
    response = client.post("/v1/stories/generate", json=data)
    assert response.status_code == 422
    assert response.json["code"] == 4222
    assert response.json["message"] == "Invalid vocabulary_level: 101"


def test_generate_story_invalid_new_char_rate(client):
    """测试生成故事API，new_char_rate 超出范围"""
    data = {
        "vocabulary_level": 35,
        "scene_id": "test_scene_id",
        "word_count": 120,
        "new_char_rate": 1.2,
    }
    response = client.post("/v1/stories/generate", json=data)
    assert response.status_code == 422
    assert response.json["code"] == 4221
    assert response.json["message"] == "Invalid new_char_rate: 1.2"
