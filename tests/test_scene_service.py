# filepath: tests/test_scene_service.py
import pytest
from app.services.scene_service import SceneService
from app.models.scene import Scene


@pytest.fixture
def scene_service():
    """Fixture to initialize SceneService."""
    return SceneService()


@pytest.fixture
def test_scene():
    """Fixture to create a test scene."""
    scene = Scene("问路", "一个关于问路的场景")
    scene.save()
    return scene


def test_create_scene(scene_service):
    """Test creating a new scene."""
    scene = scene_service.create_scene("打车", "一个关于打车的场景")
    assert scene is not None
    assert scene.name == "打车"  # 使用 scene.name 访问属性
    assert scene.description == "一个关于打车的场景"  # 使用 scene.description 访问属性


def test_get_scene(scene_service, test_scene):
    """Test getting a scene by ID."""
    scene_id = test_scene.id
    scene = scene_service.get_scene(scene_id)
    assert scene is not None
    assert scene["id"] == scene_id  # get_scene 返回的是字典，因此可以使用下标访问
    assert scene["name"] == "问路"
    assert scene["description"] == "一个关于问路的场景"


def test_update_scene(scene_service, test_scene):
    """Test updating a scene."""
    scene_id = test_scene.id
    updated = scene_service.update_scene(scene_id, "点餐", "一个关于点餐的场景")
    assert updated is True

    # Verify the update
    scene = scene_service.get_scene(scene_id)
    assert scene["name"] == "点餐"
    assert scene["description"] == "一个关于点餐的场景"


def test_update_scene_not_found(scene_service):
    """Test updating a scene that does not exist."""
    updated = scene_service.update_scene(
        "invalid-scene-id", "点餐", "一个关于点餐的场景"
    )
    assert updated is False


def test_delete_scene(scene_service, test_scene):
    """Test deleting a scene."""
    scene_id = test_scene.id
    deleted = scene_service.delete_scene(scene_id)
    assert deleted is True

    # Verify the deletion
    scene = scene_service.get_scene(scene_id)
    assert scene is None


def test_delete_scene_not_found(scene_service):
    """Test deleting a scene that does not exist."""
    deleted = scene_service.delete_scene("invalid-scene-id")
    assert deleted is False
