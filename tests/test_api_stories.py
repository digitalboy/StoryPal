import pytest
from flask import Flask, jsonify
from app.api.stories import init_story_routes
from app.services.story_service import StoryService
from app.utils.error_handling import handle_error


# 模拟 StoryService
class MockStoryService:
    def __init__(self):
        self.stories = {}

    def get_story(self, story_id):
        return self.stories.get(story_id)

    def update_story(self, story_id, data):
        if story_id in self.stories:
            self.stories[story_id].update(data)
            return True
        return False

    def delete_story(self, story_id):
        if story_id in self.stories:
            del self.stories[story_id]
            return True
        return False

    def test_generate_story(client):
        # 生成故事
        response = client.post(
            "/v1/stories/generate",
            json={
                "vocabulary_level": 35,
                "scene_id": "550e8400-e29b-41d4-a716-446655440001",  # 确保是有效的 UUID
                "word_count": 120,
                "new_char_rate": 0.02,
                "key_word_ids": ["550e8400-e29b-41d4-a716-446655440002"],  # 确保是有效的 UUID
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["code"] == 200
        assert data["data"]["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert data["data"]["vocabulary_level"] == 35
        assert data["data"]["scene_id"] == "550e8400-e29b-41d4-a716-446655440001"
        assert data["data"]["word_count"] == 120
        assert data["data"]["new_char_rate"] == 0.02


# 创建 Flask 应用并初始化路由
@pytest.fixture
def app():
    app = Flask(__name__)
    app.testing = True
    story_service = MockStoryService()
    init_story_routes(app)
    return app


# 测试客户端
@pytest.fixture
def client(app):
    return app.test_client()


# 测试获取故事
def test_get_story(client):
    # 模拟一个故事
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client.get(f"/v1/stories/{story_id}")
    assert response.status_code == 404  # 故事不存在

    # 生成一个故事
    response = client.post(
        "/v1/stories/generate",
        json={
            "vocabulary_level": 35,
            "scene_id": "550e8400-e29b-41d4-a716-446655440001",
            "word_count": 120,
            "new_char_rate": 0.02,
            "key_word_ids": ["550e8400-e29b-41d4-a716-446655440002"],
        },
    )
    assert response.status_code == 200

    # 获取生成的故事
    response = client.get(f"/v1/stories/{story_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 200
    assert data["data"]["id"] == story_id


# 测试更新故事
def test_update_story(client):
    # 生成一个故事
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client.post(
        "/v1/stories/generate",
        json={
            "vocabulary_level": 35,
            "scene_id": "550e8400-e29b-41d4-a716-446655440001",
            "word_count": 120,
            "new_char_rate": 0.02,
            "key_word_ids": ["550e8400-e29b-41d4-a716-446655440002"],
        },
    )
    assert response.status_code == 200

    # 更新故事
    response = client.put(
        f"/v1/stories/{story_id}",
        json={
            "title": "更新后的故事标题",
            "content": "更新后的故事内容",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 200

    # 验证故事已更新
    response = client.get(f"/v1/stories/{story_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["title"] == "更新后的故事标题"
    assert data["data"]["content"] == "更新后的故事内容"


# 测试删除故事
def test_delete_story(client):
    # 生成一个故事
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client.post(
        "/v1/stories/generate",
        json={
            "vocabulary_level": 35,
            "scene_id": "550e8400-e29b-41d4-a716-446655440001",
            "word_count": 120,
            "new_char_rate": 0.02,
            "key_word_ids": ["550e8400-e29b-41d4-a716-446655440002"],
        },
    )
    assert response.status_code == 200

    # 删除故事
    response = client.delete(f"/v1/stories/{story_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 200

    # 验证故事已删除
    response = client.get(f"/v1/stories/{story_id}")
    assert response.status_code == 404


# 测试生成故事
def test_generate_story(client):
    # 生成故事
    response = client.post(
        "/v1/stories/generate",
        json={
            "vocabulary_level": 35,
            "scene_id": "550e8400-e29b-41d4-a716-446655440001",
            "word_count": 120,
            "new_char_rate": 0.02,
            "key_word_ids": ["550e8400-e29b-41d4-a716-446655440002"],
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 200
    assert data["data"]["id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert data["data"]["vocabulary_level"] == 35
    assert data["data"]["scene_id"] == "550e8400-e29b-41d4-a716-446655440001"
    assert data["data"]["word_count"] == 120
    assert data["data"]["new_char_rate"] == 0.02


# 测试生成故事时缺少必填字段
def test_generate_story_missing_fields(client):
    response = client.post(
        "/v1/stories/generate",
        json={
            "vocabulary_level": 35,
            "scene_id": "550e8400-e29b-41d4-a716-446655440001",
            "word_count": 120,
            # 缺少 new_char_rate
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == 4001
    assert "缺少必填字段: new_char_rate" in data["message"]
