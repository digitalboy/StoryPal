# filepath: tests/test_story.py
import unittest
from app.models.story_model import Story


class TestStoryModel(unittest.TestCase):
    def setUp(self):
        self.story = Story(
            title="问路的故事",
            content="有一天，小明想去公园...",
            vocabulary_level=35,
            scene_id="550e8400-e29b-41d4-a716-446655440000",
            word_count=120,
            new_words=[
                {"word": "公园", "pinyin": "gōngyuán", "definition": "public park"}
            ],
            new_char_rate=0.02,
            key_words=[
                {"word": "问路", "pinyin": "wènlù", "definition": "ask for directions"}
            ],
        )

    def test_story_creation(self):
        self.assertEqual(self.story.title, "问路的故事")
        self.assertEqual(self.story.vocabulary_level, 35)
        self.assertEqual(self.story.scene_id, "550e8400-e29b-41d4-a716-446655440000")

    def test_story_save(self):
        self.story.save()
        found_story = Story.find_by_id(self.story.id)
        self.assertIsNotNone(found_story)
        self.assertEqual(found_story["title"], "问路的故事")


if __name__ == "__main__":
    unittest.main()
