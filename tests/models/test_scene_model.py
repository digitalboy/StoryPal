# tests/models/test_scene_model.py
import unittest
from app.models.scene_model import SceneModel


class TestSceneModel(unittest.TestCase):
    """
    测试场景模型 (SceneModel) 的功能。
    """

    def test_create_scene_model(self):
        """
        测试创建场景模型对象。
        """
        scene = SceneModel(
            scene_id="test_id", name="问路", description="学习如何用中文问路。"
        )
        self.assertEqual(scene.id, "test_id")
        self.assertEqual(scene.name, "问路")
        self.assertEqual(scene.description, "学习如何用中文问路。")

    def test_create_scene_model_without_id(self):
        """
        测试创建场景模型对象，不指定ID。
        """
        scene = SceneModel(name="问路", description="学习如何用中文问路。")
        self.assertIsNotNone(scene.id)
        self.assertEqual(scene.name, "问路")
        self.assertEqual(scene.description, "学习如何用中文问路。")

    def test_scene_model_to_dict(self):
        """
        测试将场景模型对象转换为字典。
        """
        scene = SceneModel(
            scene_id="test_id", name="问路", description="学习如何用中文问路。"
        )
        scene_dict = scene.to_dict()
        self.assertEqual(scene_dict["scene_id"], "test_id")
        self.assertEqual(scene_dict["name"], "问路")
        self.assertEqual(scene_dict["description"], "学习如何用中文问路。")
        self.assertIsNotNone(scene_dict["created_at"])

    def test_scene_model_from_dict(self):
        """
        测试从字典创建场景模型对象。
        """
        scene_dict = {
            "scene_id": "test_id",
            "name": "问路",
            "description": "学习如何用中文问路。",
            "created_at": "2025-01-10T04:47:20Z",
        }
        scene = SceneModel.from_dict(scene_dict)
        self.assertEqual(scene.id, "test_id")
        self.assertEqual(scene.name, "问路")
        self.assertEqual(scene.description, "学习如何用中文问路。")
        self.assertEqual(scene.created_at, "2025-01-10T04:47:20Z")


if __name__ == "__main__":
    unittest.main()
