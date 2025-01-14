# tests/services/test_scene_service.py
import unittest
from unittest.mock import patch, mock_open
import json
from app.services.scene_service import SceneService
from app.models.scene_model import SceneModel


class TestSceneService(unittest.TestCase):
    """
    测试场景服务 (SceneService) 的功能。
    """

    def setUp(self):
        """
        设置测试环境。
        """
        self.sample_scenes_data = [
            {
                "scene_id": "test_scene_id_1",
                "name": "问路",
                "description": "学习如何用中文问路。",
            },
            {
                "scene_id": "test_scene_id_2",
                "name": "点餐",
                "description": "学习如何在餐厅点餐。",
            },
        ]
        self.sample_scenes_json = json.dumps(self.sample_scenes_data)

    def test_load_scenes(self):
        """
        测试加载场景数据。
        """
        with patch(
            "app.services.scene_service.open",
            mock_open(read_data=self.sample_scenes_json),
        ):
            scene_service = SceneService()
        self.assertEqual(len(scene_service.scenes), 2)
        self.assertIsInstance(scene_service.scenes["test_scene_id_1"], SceneModel)
        self.assertEqual(scene_service.scenes["test_scene_id_1"].name, "问路")
        self.assertEqual(scene_service.scenes["test_scene_id_2"].name, "点餐")

    def test_load_scenes_file_not_found(self):
        """
        测试加载场景数据，文件不存在的情况。
        """
        with patch("app.services.scene_service.open", side_effect=FileNotFoundError):
            scene_service = SceneService()
        self.assertEqual(len(scene_service.scenes), 0)

    def test_load_scenes_json_decode_error(self):
        """
        测试加载场景数据，JSON 解析错误的情况。
        """
        with patch(
            "app.services.scene_service.open", mock_open(read_data="invalid json")
        ):
            scene_service = SceneService()
        self.assertEqual(len(scene_service.scenes), 0)

    def test_get_scene_by_id(self):
        """
        测试根据ID获取场景信息。
        """
        with patch(
            "app.services.scene_service.open",
            mock_open(read_data=self.sample_scenes_json),
        ):
            scene_service = SceneService()
            scene = scene_service.get_scene_by_id("test_scene_id_2")
            self.assertEqual(scene.name, "点餐")
            self.assertEqual(scene.description, "学习如何在餐厅点餐。")

    def test_get_scene_by_id_not_found(self):
        """
        测试根据ID获取场景信息，ID不存在的情况。
        """
        with patch(
            "app.services.scene_service.open",
            mock_open(read_data=self.sample_scenes_json),
        ):
            scene_service = SceneService()
            scene = scene_service.get_scene_by_id("not_exist_id")
            self.assertIsNone(scene)

    def test_create_scene(self):
        """
        测试创建场景。
        """
        with patch("app.services.scene_service.open", mock_open()) as mock_file:
            scene_service = SceneService()
            new_scene = scene_service.create_scene(
                name="新的场景", description="这是新的场景描述"
            )
            self.assertIsNotNone(new_scene.id)
            self.assertEqual(new_scene.name, "新的场景")
            self.assertEqual(new_scene.description, "这是新的场景描述")
            mock_file.assert_called()  # 检查是否调用了保存函数。

    def test_update_scene(self):
        """
        测试更新场景信息。
        """
        with patch(
            "app.services.scene_service.open",
            mock_open(read_data=self.sample_scenes_json),
        ) as mock_file:
            scene_service = SceneService()
            updated_scene = scene_service.update_scene(
                scene_id="test_scene_id_1",
                name="更新后的场景",
                description="更新后的场景描述",
            )
            self.assertEqual(updated_scene.name, "更新后的场景")
            self.assertEqual(updated_scene.description, "更新后的场景描述")
            mock_file.assert_called()

    def test_update_scene_not_found(self):
        """
        测试更新场景信息，场景不存在的情况。
        """
        with patch(
            "app.services.scene_service.open",
            mock_open(read_data=self.sample_scenes_json),
        ):
            scene_service = SceneService()
            updated_scene = scene_service.update_scene(
                scene_id="not_exist_id",
                name="更新后的场景",
                description="更新后的场景描述",
            )
            self.assertIsNone(updated_scene)

    def test_delete_scene(self):
        """
        测试删除场景。
        """
        with patch(
            "app.services.scene_service.open",
            mock_open(read_data=self.sample_scenes_json),
        ) as mock_file:
            scene_service = SceneService()
            result = scene_service.delete_scene("test_scene_id_1")
            self.assertTrue(result)
            self.assertNotIn("test_scene_id_1", scene_service.scenes)
            mock_file.assert_called()

    def test_delete_scene_not_found(self):
        """
        测试删除场景，场景不存在的情况。
        """
        with patch(
            "app.services.scene_service.open",
            mock_open(read_data=self.sample_scenes_json),
        ):
            scene_service = SceneService()
            result = scene_service.delete_scene("not_exist_id")
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
