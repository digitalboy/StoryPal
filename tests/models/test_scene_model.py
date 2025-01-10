# tests/models/test_scene_model.py
from app.models.scene_model import SceneModel
from datetime import datetime


def test_scene_model_creation(sample_scene):
    assert sample_scene.scene_id == "test_scene_id"
    assert sample_scene.name == "测试场景"
    assert sample_scene.description == "这是一个用于测试的场景"
    assert isinstance(sample_scene.created_at, str)
    try:
        datetime.fromisoformat(sample_scene.created_at.replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"


def test_scene_model_to_dict(sample_scene):
    scene_dict = sample_scene.to_dict()
    assert scene_dict["scene_id"] == "test_scene_id"
    assert scene_dict["name"] == "测试场景"
    assert scene_dict["description"] == "这是一个用于测试的场景"
    assert isinstance(scene_dict["created_at"], str)
    try:
        datetime.fromisoformat(scene_dict["created_at"].replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"


def test_scene_model_from_dict(sample_scene):
    scene_dict = sample_scene.to_dict()
    new_scene = SceneModel.from_dict(scene_dict)
    assert new_scene.scene_id == "test_scene_id"
    assert new_scene.name == "测试场景"
    assert new_scene.description == "这是一个用于测试的场景"
    assert isinstance(new_scene.created_at, str)
    try:
        datetime.fromisoformat(new_scene.created_at.replace("Z", "+00:00"))
    except:
        assert False, "created_at is not a valid ISO format"
    assert new_scene.created_at == sample_scene.created_at
