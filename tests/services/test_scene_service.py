# tests/services/test_scene_service.py
import pytest
from app.services.scene_service import SceneService
from unittest.mock import patch


@pytest.fixture
def scene_service():
    return SceneService()


def test_load_scenes_success(scene_service):
    assert len(scene_service.scenes) > 0


def test_load_scenes_not_found():
    with patch(
        "app.services.scene_service.Config.SCENES_FILE_PATH", "non_existent.json"
    ):
        scene_service = SceneService()
        assert len(scene_service.scenes) == 0


def test_get_scene_success(scene_service):
    scene = scene_service.get_scene("f0e9d8c7-b6a5-4321-9876-543210fedcba")
    assert scene.name == "日常生活"


def test_get_scene_not_found(scene_service):
    scene = scene_service.get_scene("non_existent_id")
    assert scene is None


def test_list_scenes_all(scene_service):
    scenes = scene_service.list_scenes()
    assert len(scenes) > 0


def test_add_scene(scene_service):
    new_scene_data = {
        "scene_id": "test_add_scene_id",
        "name": "测试添加场景",
        "description": "这是一个测试添加的场景",
    }
    new_scene = scene_service.add_scene(new_scene_data)
    assert new_scene.name == "测试添加场景"
    assert scene_service.get_scene("test_add_scene_id") == new_scene


def test_update_scene(scene_service):
    updated_scene_data = {
        "name": "更新测试场景",
        "description": "这是一个更新测试的场景",
    }
    updated_scene = scene_service.update_scene(
        "f0e9d8c7-b6a5-4321-9876-543210fedcba", updated_scene_data
    )
    assert updated_scene.name == "更新测试场景"
    assert updated_scene.description == "这是一个更新测试的场景"


def test_update_scene_not_found(scene_service):
    updated_scene = scene_service.update_scene(
        "non_existent_id", {"name": "更新测试场景"}
    )
    assert updated_scene is None


def test_delete_scene(scene_service):
    deleted_scene = scene_service.delete_scene("f0e9d8c7-b6a5-4321-9876-543210fedcba")
    assert deleted_scene.name == "日常生活"
    assert scene_service.get_scene("f0e9d8c7-b6a5-4321-9876-543210fedcba") is None


def test_delete_scene_not_found(scene_service):
    deleted_scene = scene_service.delete_scene("non_existent_id")
    assert deleted_scene is None
