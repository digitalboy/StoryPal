# filepath: tests/test_scenes.py
import pytest
from app import create_app
import json
from app.models.scene_model import Scene


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
    clear_json_file("data/scenes.json")
    yield


def test_create_scene(client):
    """测试创建场景 API"""
    data = {"name": "测试场景", "description": "这是一个测试场景"}
    response = client.post("/v1/scenes", json=data)
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert "scene_id" in response.json["data"]
    scene_id = response.json["data"]["scene_id"]
    scene = Scene.find_by_id(scene_id)
    assert scene
    assert scene.name == "测试场景"


def test_create_scene_missing_name(client):
    """测试创建场景 API，缺少 name 参数"""
    data = {"description": "这是一个测试场景"}
    response = client.post("/v1/scenes", json=data)
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "缺少必填字段: name"


def test_create_scene_missing_description(client):
    """测试创建场景 API，缺少 description 参数"""
    data = {"name": "测试场景"}
    response = client.post("/v1/scenes", json=data)
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "缺少必填字段: description"


def test_get_scene(client):
    """测试获取场景 API"""
    data = {"name": "测试场景", "description": "这是一个测试场景"}
    response = client.post("/v1/scenes", json=data)
    scene_id = response.json["data"]["scene_id"]

    response = client.get(f"/v1/scenes/{scene_id}")
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert response.json["data"]["name"] == "测试场景"
    assert response.json["data"]["description"] == "这是一个测试场景"


def test_get_scene_not_found(client):
    """测试获取场景 API，场景不存在"""
    response = client.get("/v1/scenes/non_existent_id")
    assert response.status_code == 404
    assert response.json["code"] == 4041
    assert response.json["message"] == "Scene not found"


def test_update_scene(client):
    """测试更新场景 API"""
    data = {"name": "测试场景", "description": "这是一个测试场景"}
    response = client.post("/v1/scenes", json=data)
    scene_id = response.json["data"]["scene_id"]

    update_data = {"name": "更新后的场景", "description": "这是更新后的场景"}
    response = client.put(f"/v1/scenes/{scene_id}", json=update_data)
    assert response.status_code == 200
    assert response.json["code"] == 200

    response = client.get(f"/v1/scenes/{scene_id}")
    assert response.json["data"]["name"] == "更新后的场景"
    assert response.json["data"]["description"] == "这是更新后的场景"


def test_update_scene_not_found(client):
    """测试更新场景 API，场景不存在"""
    update_data = {"name": "更新后的场景", "description": "这是更新后的场景"}
    response = client.put("/v1/scenes/non_existent_id", json=update_data)
    assert response.status_code == 404
    assert response.json["code"] == 4041
    assert response.json["message"] == "Scene not found"


def test_delete_scene(client):
    """测试删除场景 API"""
    data = {"name": "测试场景", "description": "这是一个测试场景"}
    response = client.post("/v1/scenes", json=data)
    scene_id = response.json["data"]["scene_id"]

    response = client.delete(f"/v1/scenes/{scene_id}")
    assert response.status_code == 200
    assert response.json["code"] == 200

    response = client.get(f"/v1/scenes/{scene_id}")
    assert response.status_code == 404


def test_delete_scene_not_found(client):
    """测试删除场景 API，场景不存在"""
    response = client.delete("/v1/scenes/non_existent_id")
    assert response.status_code == 404
    assert response.json["code"] == 4041
    assert response.json["message"] == "Scene not found"
