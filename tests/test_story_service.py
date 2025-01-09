# filepath: tests/test_story_service.py
import unittest
from app.services.story_service import StoryService
from app.models.scene import Scene
from app.models.word import Word


class TestStoryService(unittest.TestCase):
    def setUp(self):
        self.story_service = StoryService()
        # 创建一个测试场景
        self.scene = Scene("问路", "一个关于问路的场景")
        self.scene.save()
        # 创建一个测试词汇
        self.word = Word(
            word="公园",
            pinyin="gōngyuán",
            definition="public park",
            part_of_speech="名词",
            chaotong_level=35,
            characters=[{"character": "公", "pinyin": "gōng", "definition": "public"}],
            example="我们去公园玩吧。",
        )
        self.word.save()

    def test_generate_story(self):
        """测试生成故事的功能。"""
        # 调用 generate_story 方法
        story = self.story_service.generate_story(
            vocabulary_level=35,
            scene_id=self.scene.id,
            word_count=120,
            new_char_rate=0.02,
            key_word_ids=[self.word.id],
        )

        # 验证返回的故事对象
        self.assertIsNotNone(story)
        self.assertEqual(story.vocabulary_level, 35)
        self.assertEqual(story.scene_id, self.scene.id)
        self.assertEqual(story.word_count, 120)
        self.assertEqual(story.new_char_rate, 0.02)
        self.assertEqual(len(story.key_words), 1)
        self.assertEqual(story.key_words[0]["word"], "公园")

    def test_generate_story_with_invalid_scene(self):
        """测试使用无效的场景 ID 生成故事时的错误处理。"""
        with self.assertRaises(ValueError) as context:
            self.story_service.generate_story(
                vocabulary_level=35,
                scene_id="invalid-scene-id",
                word_count=120,
                new_char_rate=0.02,
                key_word_ids=[self.word.id],
            )
        self.assertTrue(
            "Scene with ID invalid-scene-id not found" in str(context.exception)
        )

    def test_generate_story_with_invalid_word(self):
        """测试使用无效的词汇 ID 生成故事时的行为。"""
        story = self.story_service.generate_story(
            vocabulary_level=35,
            scene_id=self.scene.id,
            word_count=120,
            new_char_rate=0.02,
            key_word_ids=["invalid-word-id"],
        )
        # 无效的词汇 ID 应该被忽略，key_words 列表为空
        self.assertEqual(len(story.key_words), 0)


if __name__ == "__main__":
    unittest.main()
