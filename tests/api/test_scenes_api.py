# tests/api/test_scenes_api.py
import pytest
import json
from app.config import Config
from unittest.mock import MagicMock
from app.utils.error_handling import handle_error
from app.utils.api_key_auth import api_key_required


@pytest.fixture
def mock_scene_service():
    """
    创建一个模拟的 scene_service 对象，用于测试
    """
    mock_service = MagicMock()
    mock_service.get_scene_by_id.return_value = MagicMock(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="问路",
        description="学习如何用中文问路。",
        created_at="2025-01-10T10:00:00Z",
    )
    return mock_service


@pytest.fixture
def app():
    """
    创建一个测试用的 Flask app 实例
    """
    from flask import Flask
    from app.api.scene_api import scene_api
    from app.utils.error_handling import handle_error
    from app.config import Config

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["APPLICATION_ROOT"] = Config.BASE_URL  # 设置baseURL
    app.config["SECRET_KEY"] = "test_secret_key"  # 添加 secret_key
    app.register_blueprint(scene_api)

    # 全局错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return handle_error(4041, "Resource not found")

    @app.errorhandler(500)
    def internal_server_error(error):
        return handle_error(5001, "Internal server error")

    return app


@pytest.fixture
def client(app):
    """
    创建一个测试客户端
    """
    return app.test_client(use_cookies=True)


def test_create_scene_success(client, mock_scene_service):
    """
    测试成功创建场景
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    mock_scene_service.create_scene.return_value = MagicMock(
        id="550e8400-e29b-41d4-a716-446655440001"
    )
    headers = {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json",
    }
    data = {"name": "测试场景", "description": "这是一个测试场景"}
    response = client.post("/v1/scenes", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert response.json["message"] == "Scene created successfully"
    assert response.json["data"]["scene_id"] == "550e8400-e29b-41d4-a716-446655440001"


def test_create_scene_missing_name(client, mock_scene_service):
    """
    测试创建场景缺少 name 参数
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    headers = {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json",
    }
    data = {"description": "这是一个测试场景"}
    response = client.post("/v1/scenes", headers=headers, json=data)
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "Missing required field: name"
    assert response.json["data"] == None


def test_create_scene_missing_description(client, mock_scene_service):
    """
    测试创建场景缺少 description 参数
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    headers = {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json",
    }
    data = {"name": "测试场景"}
    response = client.post("/v1/scenes", headers=headers, json=data)
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "Missing required field: description"
    assert response.json["data"] == None


def test_get_scene_success(client, mock_scene_service):
    """
    测试成功获取场景
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    headers = {"Authorization": "Bearer test_api_key"}
    response = client.get(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440000", headers=headers
    )
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert response.json["message"] == "Scene retrieved successfully"
    assert response.json["data"]["scene_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert response.json["data"]["name"] == "问路"
    assert response.json["data"]["description"] == "学习如何用中文问路。"


def test_get_scene_not_found(client, mock_scene_service):
    """
    测试获取不存在的场景
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    mock_scene_service.get_scene_by_id.return_value = None
    headers = {"Authorization": "Bearer test_api_key"}
    response = client.get(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440001", headers=headers
    )
    assert response.status_code == 404
    assert response.json["code"] == 4041
    assert response.json["message"] == "Scene not found"
    assert response.json["data"] == None


def test_update_scene_success(client, mock_scene_service):
    """
    测试成功更新场景
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    headers = {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json",
    }
    data = {"name": "更新后的场景", "description": "更新后的场景描述"}
    response = client.put(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440000", headers=headers, json=data
    )
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert response.json["message"] == "Scene updated successfully"
    assert response.json["data"] == None


def test_update_scene_not_found(client, mock_scene_service):
    """
    测试更新不存在的场景
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key
    mock_scene_service.get_scene_by_id.return_value = None
    headers = {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json",
    }
    data = {"name": "更新后的场景", "description": "更新后的场景描述"}
    response = client.put(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440001", headers=headers, json=data
    )
    assert response.status_code == 404
    assert response.json["code"] == 4041
    assert response.json["message"] == "Scene not found"
    assert response.json["data"] == None


def test_update_scene_missing_name(client, mock_scene_service):
    """
    测试更新场景缺少 name 参数
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    headers = {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json",
    }
    data = {"description": "这是一个测试场景"}
    response = client.put(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440000", headers=headers, json=data
    )
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "Missing required field: name"
    assert response.json["data"] == None


def test_update_scene_missing_description(client, mock_scene_service):
    """
    测试更新场景缺少 description 参数
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    headers = {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json",
    }
    data = {"name": "测试场景"}
    response = client.put(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440000", headers=headers, json=data
    )
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "Missing required field: description"
    assert response.json["data"] == None


def test_delete_scene_success(client, mock_scene_service):
    """
    测试成功删除场景
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key
    headers = {"Authorization": "Bearer test_api_key"}
    response = client.delete(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440000", headers=headers
    )
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert response.json["message"] == "Scene deleted successfully"
    assert response.json["data"] == None


def test_delete_scene_not_found(client, mock_scene_service):
    """
    测试删除不存在的场景
    """
    with client.application.test_request_context():
        with client.session_transaction() as session:
            session["api_key"] = "test_api_key"  # 设置API key

    mock_scene_service.delete_scene.return_value = False
    headers = {"Authorization": "Bearer test_api_key"}
    response = client.delete(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440001", headers=headers
    )
    assert response.status_code == 404
    assert response.json["code"] == 4041
    assert response.json["message"] == "Scene not found"
    assert response.json["data"] == None


def test_api_key_missing(client, mock_scene_service):
    """
    测试API key 缺失
    """
    response = client.get("/v1/scenes/550e8400-e29b-41d4-a716-446655440000")
    assert response.status_code == 401
    assert response.json["code"] == 4011
    assert response.json["message"] == "API Key missing"
    assert response.json["data"] == None


def test_api_key_invalid(client, mock_scene_service):
    """
    测试API key 无效
    """
    headers = {"Authorization": "Bearer invalid_api_key"}
    response = client.get(
        "/v1/scenes/550e8400-e29b-41d4-a716-446655440000", headers=headers
    )
    assert response.status_code == 401
    assert response.json["code"] == 4012
    assert response.json["message"] == "Invalid API Key"
    assert response.json["data"] == None
