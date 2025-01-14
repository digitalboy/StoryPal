# tests/models/test_story_model.py
import unittest
from app.models.story_model import StoryModel


class TestStoryModel(unittest.TestCase):
    """
    测试故事模型 (StoryModel) 的功能。
    """

    def test_create_story_model(self):
        """
        测试创建故事模型对象。
        """
        story = StoryModel(
            story_id="test_id",
            title="小明的一天",
            content="小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心",
            vocabulary_level=30,
            scene="scene_id",
            word_count=15,
            new_char_rate=0.2,
            new_char=3,
            key_words=[
                {
                    "word": "喜欢",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
                {
                    "word": "跑步",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
            ],
        )
        self.assertEqual(story.id, "test_id")
        self.assertEqual(story.title, "小明的一天")
        self.assertEqual(
            story.content, "小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心"
        )
        self.assertEqual(story.vocabulary_level, 30)
        self.assertEqual(story.scene, "scene_id")
        self.assertEqual(story.word_count, 15)
        self.assertEqual(story.new_char_rate, 0.2)
        self.assertEqual(story.new_char, 3)
        self.assertEqual(len(story.key_words), 2)
        self.assertEqual(story.key_words[0]["word"], "喜欢")
        self.assertEqual(story.key_words[1]["word"], "跑步")
        self.assertEqual(story.key_words[0]["part_of_speech"], "v")
        self.assertEqual(story.key_words[1]["part_of_speech"], "v")

    def test_create_story_model_without_id(self):
        """
        测试创建故事模型对象，不指定ID。
        """
        story = StoryModel(
            title="小明的一天",
            content="小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心",
            vocabulary_level=30,
            scene="scene_id",
            word_count=15,
            new_char_rate=0.2,
            new_char=3,
            key_words=[
                {
                    "word": "喜欢",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
                {
                    "word": "跑步",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
            ],
        )
        self.assertIsNotNone(story.id)
        self.assertEqual(story.title, "小明的一天")
        self.assertEqual(
            story.content, "小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心"
        )
        self.assertEqual(story.vocabulary_level, 30)
        self.assertEqual(story.scene, "scene_id")
        self.assertEqual(story.word_count, 15)
        self.assertEqual(story.new_char_rate, 0.2)
        self.assertEqual(story.new_char, 3)
        self.assertEqual(len(story.key_words), 2)
        self.assertEqual(story.key_words[0]["word"], "喜欢")
        self.assertEqual(story.key_words[1]["word"], "跑步")
        self.assertEqual(story.key_words[0]["part_of_speech"], "v")
        self.assertEqual(story.key_words[1]["part_of_speech"], "v")

    def test_story_model_to_dict(self):
        """
        测试将故事模型对象转换为字典。
        """
        story = StoryModel(
            story_id="test_id",
            title="小明的一天",
            content="小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心",
            vocabulary_level=30,
            scene="scene_id",
            word_count=15,
            new_char_rate=0.2,
            new_char=3,
            key_words=[
                {
                    "word": "喜欢",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
                {
                    "word": "跑步",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
            ],
        )
        story_dict = story.to_dict()
        self.assertEqual(story_dict["story_id"], "test_id")
        self.assertEqual(story_dict["title"], "小明的一天")
        self.assertEqual(
            story_dict["content"],
            "小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心",
        )
        self.assertEqual(story_dict["vocabulary_level"], 30)
        self.assertEqual(story_dict["scene"], "scene_id")
        self.assertEqual(story_dict["word_count"], 15)
        self.assertEqual(story_dict["new_char_rate"], 0.2)
        self.assertEqual(story_dict["new_char"], 3)
        self.assertEqual(len(story_dict["key_words"]), 2)
        self.assertEqual(story_dict["key_words"][0]["word"], "喜欢")
        self.assertEqual(story_dict["key_words"][1]["word"], "跑步")
        self.assertEqual(story_dict["key_words"][0]["part_of_speech"], "v")
        self.assertEqual(story_dict["key_words"][1]["part_of_speech"], "v")
        self.assertIsNotNone(story_dict["created_at"])

    def test_story_model_from_dict(self):
        """
        测试从字典创建故事模型对象。
        """
        story_dict = {
            "story_id": "test_id",
            "title": "小明的一天",
            "content": "小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心",
            "vocabulary_level": 30,
            "scene": "scene_id",
            "word_count": 15,
            "new_char_rate": 0.2,
            "new_char": 3,
            "key_words": [
                {
                    "word": "喜欢",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
                {
                    "word": "跑步",
                    "pinyin": None,
                    "definition": None,
                    "part_of_speech": "v",
                    "example": None,
                },
            ],
            "created_at": "2025-01-10T04:47:20Z",
        }
        story = StoryModel.from_dict(story_dict)
        self.assertEqual(story.id, "test_id")
        self.assertEqual(story.title, "小明的一天")
        self.assertEqual(
            story.content, "小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心"
        )
        self.assertEqual(story.vocabulary_level, 30)
        self.assertEqual(story.scene, "scene_id")
        self.assertEqual(story.word_count, 15)
        self.assertEqual(story.new_char_rate, 0.2)
        self.assertEqual(story.new_char, 3)
        self.assertEqual(len(story.key_words), 2)
        self.assertEqual(story.key_words[0]["word"], "喜欢")
        self.assertEqual(story.key_words[1]["word"], "跑步")
        self.assertEqual(story.key_words[0]["part_of_speech"], "v")
        self.assertEqual(story.key_words[1]["part_of_speech"], "v")
        self.assertEqual(story.created_at, "2025-01-10T04:47:20Z")


if __name__ == "__main__":
    unittest.main()
